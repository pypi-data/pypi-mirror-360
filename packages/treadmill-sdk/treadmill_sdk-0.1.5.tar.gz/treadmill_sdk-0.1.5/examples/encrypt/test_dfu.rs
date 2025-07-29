#![allow(unused_imports)]
use futures::Stream;
use std::fs::File;
use std::io::Read;
use std::sync::Arc;
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::sync::Mutex;
use tokio_serial::{available_ports, SerialPortInfo, SerialPortType, SerialStream};
use treadmill_sdk::dfu::dfu_manager::DfuManager;
use treadmill_sdk::dfu::frame::DfuFrame;
use treadmill_sdk::dfu::model::{load_dfu_file, DfuState};
use treadmill_sdk::encrypt::callback_c::*;
use treadmill_sdk::proto::treadmill::msg_builder::tml_msg_builder;
use treadmill_sdk::utils::logging::LogLevel;

treadmill_sdk::cfg_import_logging!();

/// cargo run --example test_dfu --features "examples"
#[tokio::main]
async fn main() -> anyhow::Result<(), anyhow::Error> {
  // initialize_logging(LogLevel::Debug);
  initialize_logging(LogLevel::Info);

  // let ota_path = "ota_bin/0.2.0/tm_app_fw.bin";
  let ota_path = "ota_bin/0.2.1/tm_app_fw.bin";
  // return print_dfu_frame(ota_path).await;

  let baudrate: u32 = 38400; // 替换为实际的波特率
  let available_ports = list_available_ports(6790, 29987); // 替换为实际的 VID 和 PID
  let available_ports: Vec<SerialPortInfo> = available_ports
    .into_iter()
    .filter(|port| !port.port_name.starts_with("/dev/cu."))
    .collect();
  info!("Available ports: {:?}", available_ports);
  if available_ports.is_empty() {
    error!("No available USB ports found with the specified VID and PID.");
    return Err(anyhow::anyhow!("No available USB ports found"));
  }
  let port_name = available_ports[0].port_name.clone();
  let builder = tokio_serial::new(port_name.clone(), baudrate);
  let port = SerialStream::open(&builder)?;
  info!("Connected to port: {}", port_name);
  let (reader, writer) = tokio::io::split(port);

  let writer_arc = Arc::new(Mutex::new(writer));
  let mut dfu_manager = DfuManager::new();
  dfu_manager.set_write_callback(Box::new(move |data| {
    let writer_clone = writer_arc.clone();
    tokio::spawn(async move {
      let mut writer = writer_clone.lock().await;
      if let Err(e) = writer.write_all(&data).await {
        error!("Failed to write data: {}", e);
      }
    });
  }));

  // 创建一个适配器，将 AsyncRead 包装为 Stream<Item = Vec<u8>>
  let rx = ReaderStream::new(reader);

  // check if the file exists
  if !std::path::Path::new(ota_path).exists() {
    error!("OTA file does not exist: {}", ota_path);
    return Err(anyhow::anyhow!("OTA file does not exist"));
  }

  // 获取状态和进度的接收器
  let mut state_rx = dfu_manager.state_receiver();
  let mut progress_rx = dfu_manager.progress_receiver();

  // 监听状态变化
  tokio::spawn(async move {
    while let Ok(()) = state_rx.changed().await {
      let state = *state_rx.borrow();
      info!("DFU 状态变更为: {:?}", state);

      if state == DfuState::Finished || state == DfuState::Error {
        break;
      }
    }
  });

  // 单独监听进度变化
  tokio::spawn(async move {
    while let Ok(()) = progress_rx.changed().await {
      let progress = *progress_rx.borrow();
      info!(
        "DFU 上传进度: {:.1}% ({}/{} 字节)",
        progress.percentage, progress.uploaded_size, progress.total_size
      );
    }
  });

  let manager_arc = Arc::new(Mutex::new(dfu_manager));
  if let Err(e) = DfuManager::start_dfu_with_file(manager_arc, ota_path, rx).await {
    error!("Failed to start DFU: {}", e);
    return Err(e);
  }

  Ok(())
}

#[allow(dead_code)]
async fn print_dfu_frame(ota_path: &str) -> anyhow::Result<()> {
  let ret = load_dfu_file(ota_path);
  match ret {
    Ok((file_data, info)) => {
      info!("Loaded DFU file successfully: {:?}", info);
      info!("File data length: {}", file_data.len());
      let frame = DfuFrame::start_transfer(&info);
      info!("start_transfer Frame: {:?}", frame);

      let payload = frame.encode();
      debug!("DFU 帧编码: {:02x?}", payload);
      let data = tml_msg_builder::build_dfu_msg(&payload);
      debug!(
        "发送数据: {}",
        data
          .iter()
          .map(|b| format!("0x{:02x}", b))
          .collect::<Vec<_>>()
          .join(", ")
      );
    }
    Err(e) => {
      error!("Failed to load DFU file: {}", e);
      return Err(e);
    }
  }

  let file_data = {
    let file = File::open(ota_path)?;
    let mut data = Vec::new();
    file.take(220).read_to_end(&mut data)?;
    // info!("Read {} bytes from file", data.len());
    if data.len() < 220 {
      return Err(anyhow::anyhow!(
        "File is too short, expected at least 220 bytes"
      ));
    }
    // Ensure the data is exactly 220 bytes
    if data.len() > 220 {
      data.truncate(220);
    }
    data
  };
  let frame = DfuFrame::transfer_data(0, &file_data[0..220]);
  info!("transfer_data Frame: {:?}", frame);

  Ok(())
}

// 添加辅助类，将 AsyncRead 转换为 Stream
struct ReaderStream<R> {
  reader: R,
  buffer: [u8; 4096],
}

impl<R: AsyncReadExt + Unpin> ReaderStream<R> {
  fn new(reader: R) -> Self {
    Self {
      reader,
      buffer: [0; 4096],
    }
  }
}

impl<R: AsyncReadExt + Unpin> Stream for ReaderStream<R> {
  type Item = Vec<u8>;

  fn poll_next(
    mut self: std::pin::Pin<&mut Self>,
    cx: &mut std::task::Context<'_>,
  ) -> std::task::Poll<Option<Self::Item>> {
    use futures::ready;
    use std::task::Poll;
    use tokio::io::ReadBuf;

    let this = &mut *self;
    let mut buf = ReadBuf::new(&mut this.buffer);
    match ready!(std::pin::Pin::new(&mut this.reader).poll_read(cx, &mut buf)) {
      Ok(()) => {
        let n = buf.filled().len();
        if n == 0 {
          return Poll::Ready(None); // EOF
        }
        let data = buf.filled().to_vec();
        // Log the read data
        trace!(
          "Read {} bytes from serial: {:?}",
          n,
          data
            .iter()
            .map(|b| format!("0x{:02x}", b))
            .collect::<Vec<_>>()
            .join(", ")
        );
        Poll::Ready(Some(data))
      }
      Err(e) => {
        error!("Error reading from serial: {}", e);
        Poll::Ready(None)
      }
    }
  }
}

pub fn list_available_ports(vid: u16, pid: u16) -> Vec<SerialPortInfo> {
  let usb_ports = get_usb_available_ports();
  let filtered_ports: Vec<SerialPortInfo> = usb_ports
    .into_iter()
    .filter(|port| {
      if let SerialPortType::UsbPort(ref info) = port.port_type {
        return info.vid == vid && info.pid == pid;
      }
      false
    })
    .collect();
  info!("Available USB ports: {:?}", filtered_ports);
  filtered_ports
}

pub fn get_usb_available_ports() -> Vec<SerialPortInfo> {
  let ports = available_ports();
  match ports {
    Ok(ports) => {
      // 过滤条件：USB 端口
      let usb_ports: Vec<SerialPortInfo> = ports
        .iter()
        .filter(|port| {
          trace!("port: {:?}", port);
          matches!(port.port_type, SerialPortType::UsbPort(ref _info))
        })
        .cloned()
        .collect();
      debug!("usb ports: {:?}", usb_ports);
      usb_ports
    }
    Err(e) => {
      info!("Error getting available ports: {:?}", e);
      Vec::new()
    }
  }
}
