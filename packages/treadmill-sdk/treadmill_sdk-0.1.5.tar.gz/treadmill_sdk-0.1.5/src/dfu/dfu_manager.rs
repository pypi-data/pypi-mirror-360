use crate::{
  dfu::{frame::*, model::*},
  encrypt::callback::{
    is_dfu_progress_callback_set, is_dfu_state_callback_set, run_dfu_progress_callback,
    run_dfu_state_callback,
  },
  proto::{enums::*, msg_parser::Parser, treadmill::msg_builder::*},
};
use futures::{Stream, StreamExt};
use std::cmp::min;
use std::sync::Arc;
use std::time::Duration;
use tokio::sync::{oneshot, watch, Mutex};
use tokio_stream::wrappers::ReceiverStream;

crate::cfg_import_logging!();

pub type DfuWriteCallback = Box<dyn Fn(Vec<u8>) + Send + Sync>;
pub const OTA_SEGMENT_SIZE: usize = 220;

pub struct DfuManager {
  write_callback: Option<DfuWriteCallback>,
  version_value: u16,
  file_crc32: u32,
  start_update: Option<StartUpdate>,
  uploaded_size: usize,
  file_length: usize, // 用于跟踪文件长度
  file_data: Option<Vec<u8>>,
  state_tx: watch::Sender<DfuState>,              // 用于广播状态
  state_rx: watch::Receiver<DfuState>,            // 用于订阅状态
  progress_tx: watch::Sender<TransferProgress>,   // 用于广播传输进度
  progress_rx: watch::Receiver<TransferProgress>, // 用于订阅传输进度
  abort_tx: Option<oneshot::Sender<()>>,
  pub tx: Option<tokio::sync::mpsc::Sender<Vec<u8>>>, // 接收数据
}

impl DfuManager {
  pub fn new() -> Self {
    let (state_tx, state_rx) = watch::channel(DfuState::Idle);
    let (progress_tx, progress_rx) = watch::channel(TransferProgress::new(0, 0));
    Self {
      write_callback: None,
      version_value: 0,
      file_crc32: 0,
      start_update: None,
      uploaded_size: 0,
      file_length: 0, // 初始化文件长度为0
      file_data: None,
      state_tx,
      state_rx,
      progress_tx,
      progress_rx,
      abort_tx: None,
      tx: None, // 初始化时设置为 None
    }
  }

  pub fn state(&self) -> DfuState {
    *self.state_rx.borrow()
  }

  pub fn progress(&self) -> TransferProgress {
    *self.progress_rx.borrow()
  }

  // 获取状态和进度的订阅者
  pub fn state_receiver(&self) -> watch::Receiver<DfuState> {
    self.state_rx.clone()
  }

  pub fn progress_receiver(&self) -> watch::Receiver<TransferProgress> {
    self.progress_rx.clone()
  }

  // 状态更新
  fn update_state(&mut self, state: DfuState) {
    // 获取当前状态
    let current_state = self.state();

    // 只有在状态发生变化时才发送通知
    if current_state != state {
      self.state_tx.send(state).unwrap_or_else(|_| {
        warn!("无法更新状态，接收者已关闭");
      });
      debug!("DFU 状态从 {:?} 变更为 {:?}", current_state, state);
    }
  }

  // 进度更新
  fn update_progress(&mut self) {
    let progress = TransferProgress::new(self.file_length, self.uploaded_size);
    self.progress_tx.send(progress).unwrap_or_else(|_| {
      warn!("无法更新进度，接收者已关闭");
    });
  }

  // fn update_progress(&mut self) {
  //   let current_progress = self.progress();
  //   let new_progress = TransferProgress::new(self.file_length, self.uploaded_size);

  //   // 只在进度有明显变化时才发送通知（比如变化超过1%）
  //   if new_progress.percentage - current_progress.percentage >= 1.0 ||
  //      new_progress.percentage == 100.0 && current_progress.percentage != 100.0 {
  //     self.progress_tx.send(new_progress).unwrap_or_else(|_| {
  //       warn!("无法更新进度，接收者已关闭");
  //     });
  //     debug!("DFU 进度更新: {:.1}% ({}/{})",
  //            new_progress.percentage,
  //            new_progress.uploaded_size,
  //            new_progress.total_size);
  //   }
  // }

  fn init_dfu(&mut self, file_data: Vec<u8>, info: StartUpdate) -> anyhow::Result<()> {
    self.file_data = Some(file_data);
    self.uploaded_size = 0;
    self.file_length = info.file_size as usize; // 更新文件长度
    self.version_value = info.version_value;
    self.file_crc32 = info.file_crc32;
    self.start_update = Some(info);
    // 初始化进度
    self.update_progress();
    // 更新状态
    self.update_state(DfuState::AwaitingFirmwareInfo);
    Ok(())
  }

  pub fn is_dfu_in_progress(&self) -> bool {
    let state = self.state();
    state != DfuState::Idle && state != DfuState::Error && state != DfuState::Finished
  }

  pub async fn start_dfu_with_file<T: Stream<Item = Vec<u8>> + Send + Sync + Unpin + 'static>(
    self_arc: Arc<Mutex<Self>>,
    file_path: &str,
    rx: T,
  ) -> anyhow::Result<()> {
    {
      let (file_data, info) = load_dfu_file(file_path)?;
      let mut manager = self_arc.lock().await;
      manager.init_dfu(file_data, info)?;
    }
    Self::run_dfu_process(self_arc, rx).await
  }

  pub async fn start_dfu_with_data(
    self_arc: Arc<Mutex<Self>>,
    data: Vec<u8>,
  ) -> anyhow::Result<()> {
    let (file_data, info) = load_dfu_from_data(data)?;
    let (tx, rx) = tokio::sync::mpsc::channel::<Vec<u8>>(100);
    {
      let mut manager = self_arc.lock().await;
      manager.tx = Some(tx); // 存储 tx
      manager.init_dfu(file_data, info)?;

      if is_dfu_state_callback_set() {
        let mut state_rx = manager.state_receiver();
        // 监听状态变化
        tokio::spawn(async move {
          while let Ok(()) = state_rx.changed().await {
            let state = *state_rx.borrow();
            run_dfu_state_callback(state as u8);
            // info!("DFU 状态变更为: {:?}", state);
            if state == DfuState::Finished || state == DfuState::Error {
              break;
            }
          }
        });
      }

      if is_dfu_progress_callback_set() {
        let mut progress_rx = manager.progress_receiver();
        // 单独监听进度变化
        tokio::spawn(async move {
          while let Ok(()) = progress_rx.changed().await {
            let progress = *progress_rx.borrow();
            // info!(
            //   "DFU 上传进度: {:.1}% ({}/{} 字节)",
            //   progress.percentage, progress.uploaded_size, progress.total_size
            // );
            run_dfu_progress_callback(progress.percentage);
          }
        });
      }
    }
    let rx_stream = ReceiverStream::new(rx);
    Self::run_dfu_process(self_arc, rx_stream).await
  }

  pub async fn abort_dfu(self_arc: Arc<Mutex<Self>>) -> anyhow::Result<()> {
    let mut self_guard = self_arc.lock().await;
    let state = self_guard.state();
    if state == DfuState::Idle {
      info!("DFU 已经处于 Idle 状态，无需中止");
      return Ok(());
    }
    info!("中止 DFU 流程，当前状态: {:?}", state);

    // 清理状态
    self_guard.uploaded_size = 0;
    self_guard.file_length = 0;
    self_guard.file_data = None;
    self_guard.start_update = None;

    // 重置进度
    self_guard.update_progress();
    self_guard.update_state(DfuState::Idle);

    // 发送终止信号
    if let Some(tx) = self_guard.abort_tx.take() {
      let _ = tx.send(());
      info!("已发送终止信号");
    } else {
      warn!("未找到终止信号通道，可能尚未开始 DFU 流程");
    }

    Ok(())
  }

  async fn run_dfu_process<T: Stream<Item = Vec<u8>> + Send + Sync + Unpin + 'static>(
    self_arc: Arc<Mutex<Self>>,
    mut rx: T,
  ) -> anyhow::Result<()> {
    {
      let self_guard = self_arc.lock().await;
      self_guard.write(DfuFrame::get_firmware_info());
    }

    let (abort_tx, mut abort_rx) = oneshot::channel::<()>();
    {
      let mut self_guard = self_arc.lock().await;
      self_guard.abort_tx = Some(abort_tx);
    }

    let self_clone = self_arc.clone();

    let mut parser = Parser::new("EvoRun-DFU".into(), MsgType::Treadmill);
    let mut stream = parser.message_stream();

    let handle = tokio::spawn(async move {
      debug!("Starting read");
      while let Some(result) = stream.next().await {
        match result {
          Ok((_, message)) => match message {
            ParsedMessage::Treadmill(msg) => match msg {
              TreadmillMessage::DfuFrame(frame) => {
                let frame = *frame;
                debug!("收到 DFU 消息: {:?}", frame);
                let mut self_guard = self_clone.lock().await;
                if let Err(e) = self_guard.handle_response(frame).await {
                  error!("处理 DFU 响应失败: {:?}", e);
                  self_guard.update_state(DfuState::Error);
                  let _ = self_guard.abort_tx.take().map(|tx| tx.send(()));
                  break;
                }
                if self_guard.state() == DfuState::Finished {
                  debug!("状态为 Finished，终止消息流处理");
                  let _ = self_guard.abort_tx.take().map(|tx| tx.send(()));
                  break;
                }
              }
              _ => {
                warn!("收到非 DFU 消息，跳过处理");
              }
            },
          },
          Err(e) => {
            error!("解析消息失败: {:?}", e);
            let mut self_guard = self_clone.lock().await;
            self_guard.update_state(DfuState::Error);
            let _ = self_guard.abort_tx.take().map(|tx| tx.send(()));
            break;
          }
        }
      }
      debug!("Read completed");
    });

    let mut state_rx = {
      let self_guard = self_arc.lock().await;
      self_guard.state_rx.clone()
    };
    // let mut progress_rx = {
    //   let self_guard = self_arc.lock().await;
    //   self_guard.progress_rx.clone()
    // };
    loop {
      tokio::select! {
        _ = &mut abort_rx => {
          debug!("收到终止信号，退出循环");
          handle.abort();
          break;
        }
        _ = state_rx.changed() => {
          let state = *state_rx.borrow();
          if state == DfuState::Finished {
            debug!("状态为 Finished，退出循环");
            handle.abort();
            break;
          } else if state == DfuState::Error {
            warn!("状态为 Error，退出循环");
            handle.abort();
            return Err(anyhow::anyhow!("DFU 流程错误，状态: {:?}", state));
          }
        }
        // _ = progress_rx.changed() => {
        //   let progress = *progress_rx.borrow();
        //   debug!("DFU 进度更新: {:.1}% ({}/{})", progress.percentage, progress.uploaded_size, progress.total_size);
        // }
        result = rx.next() => {
          match result {
            Some(input) if !input.is_empty() => {
              parser.receive_data(&input);
            }
            Some(_) => {
              warn!("收到空输入数据，跳过");
            }
            None => {
              let mut self_guard = self_arc.lock().await;
              self_guard.update_state(DfuState::Error);
              warn!("输入流提前结束，未完成 DFU 流程");
              handle.abort();
              return Err(anyhow::anyhow!(
                "输入流提前结束，当前状态: {:?}",
                self_guard.state()
              ));
            }
          }
        }
      }
    }

    let self_guard = self_arc.lock().await;
    if self_guard.state() != DfuState::Finished {
      warn!("DFU 流程未完成，当前状态: {:?}", self_guard.state());
      Err(anyhow::anyhow!(
        "DFU 流程未完成，状态: {:?}",
        self_guard.state()
      ))
    } else {
      info!("DFU 流程成功完成");
      Ok(())
    }
  }

  async fn handle_response(&mut self, frame: DfuFrame) -> anyhow::Result<()> {
    let data = &frame.data;
    let cmd_type = frame.cmd_type;
    debug!(
      "处理 DFU 命令: {:?}, 当前状态: {:?}",
      cmd_type,
      self.state()
    );

    let check_status = |data: &[u8], operation: &str| -> anyhow::Result<()> {
      if data.is_empty() {
        return Err(anyhow::anyhow!("收到空的 {} 命令数据", operation));
      }
      let status_code = data[0];
      if status_code != 0x01 {
        return Err(anyhow::anyhow!(
          "{} 失败，状态码: {}",
          operation,
          status_code
        ));
      }
      Ok(())
    };

    match (self.state(), cmd_type) {
      (DfuState::AwaitingFirmwareInfo, DfuCommandType::GetFirmwareInfo) => {
        let info = FirmwareInfo::from_bytes(data)?;
        debug!("解析 FirmwareInfo: {:?}", info);
        info!("进入 DFU 模式");
        self.write(DfuFrame::enter_dfu_mode());
        tokio::time::sleep(Duration::from_millis(100)).await;

        if let Some(start_update) = self.start_update.clone() {
          self.update_state(DfuState::InDfuMode);
          self.write(DfuFrame::start_transfer(&start_update));
        } else {
          self.update_state(DfuState::Error);
          error!("start_update 为空，无法开始更新");
          return Err(anyhow::anyhow!("start_update 为空"));
        }
      }
      (DfuState::InDfuMode, DfuCommandType::StartTransfer) => {
        check_status(data, "StartUpdate")?;
        debug!("成功收到 StartUpdate 命令");
        self.transfer_next_chunk()?;
      }
      (DfuState::Transferring, DfuCommandType::TransferData) => {
        check_status(data, "UpdateData")?;
        debug!("成功收到 UpdateData 命令");
        self.transfer_next_chunk()?;
      }
      (DfuState::Finished, DfuCommandType::FinishTransfer) => {
        check_status(data, "FinishUpdate")?;
        debug!("成功收到 FinishUpdate 命令");
      }
      (state, cmd_type) => {
        self.update_state(DfuState::Error);
        return Err(anyhow::anyhow!(
          "命令类型与状态不匹配: {:?}, {:?}",
          cmd_type,
          state
        ));
      }
    }
    Ok(())
  }

  fn transfer_next_chunk(&mut self) -> anyhow::Result<()> {
    if let Some(file_data) = &self.file_data {
      let offset = self.uploaded_size;
      if offset >= file_data.len() {
        info!("所有数据上传完成，发送 FinishUpdate 命令");
        self.write(DfuFrame::finish_transfer(self.file_crc32));
        self.update_state(DfuState::Finished);
        self.update_progress(); // 确保最终进度为100%
        return Ok(());
      }

      let chunk_size = min(file_data.len(), offset + OTA_SEGMENT_SIZE);
      self.write(DfuFrame::transfer_data(
        offset,
        &file_data[offset..chunk_size],
      ));
      self.uploaded_size += OTA_SEGMENT_SIZE;
      // 更新状态
      self.update_state(DfuState::Transferring);
      // 更新进度
      self.update_progress();
      Ok(())
    } else {
      self.update_state(DfuState::Error);
      error!("file_data 为空，无法继续传输");
      Err(anyhow::anyhow!("file_data 为空"))
    }
  }

  fn write(&self, req: DfuFrame) {
    // info!("发送 DFU 帧: {:?}", req);
    let payload = req.encode();
    // debug!("DFU 帧编码: {:02x?}", payload);
    let data = tml_msg_builder::build_dfu_msg(&payload);
    trace!(
      "发送数据: {}",
      data
        .iter()
        .map(|b| format!("0x{:02x}", b))
        .collect::<Vec<_>>()
        .join(", ")
    );
    if let Some(callback) = &self.write_callback {
      callback(data);
    } else {
      cfg_if::cfg_if! {
        if #[cfg(feature = "python")] {
          // crate::python::callback::run_py_dfu_write_callback(data); FIXME
        } else if #[cfg(feature = "cbindgen")] {
          crate::encrypt::callback::run_dfu_write_callback(&data);
        }
      }
    }
  }

  pub fn set_write_callback(&mut self, callback: DfuWriteCallback) {
    self.write_callback = Some(callback);
  }
}
