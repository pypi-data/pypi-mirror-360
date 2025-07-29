#![allow(clippy::not_unsafe_ptr_arg_deref)]
use std::sync::Arc;

use crate::dfu::dfu_manager::DfuManager;
use crate::utils::logging::LogLevel;
use crate::utils::logging_desktop as logging;
use tokio::runtime::Runtime;

use super::callback::*;

crate::cfg_import_logging!();

lazy_static::lazy_static! {
  pub(crate) static ref GLOBAL_RUNTIME: Arc<Runtime> = Arc::new(Runtime::new().unwrap());
  pub(crate) static ref DFU_MANAGER: Arc<tokio::sync::Mutex<DfuManager>> = Arc::new(tokio::sync::Mutex::new(DfuManager::new()));
}

/// 初始化日志记录功能
///
/// # 参数
/// - `level`: 日志级别
#[no_mangle]
pub extern "C" fn initialize_logging(level: LogLevel) {
  logging::initialize_logging(level);
}

/// Sets the callback for GaitAnalysisResult data.
///
/// # Arguments
/// * `callback` - The function to call when receiving GaitAnalysisResult data.
#[no_mangle]
pub extern "C" fn set_gait_data_callback(cb: GaitDataCallback) {
  let mut cb_guard = GAIT_DATA_CALLBACK.write();
  *cb_guard = Some(cb);
}

/// Sets the callback for AbnormalEvent data.
///
/// # Arguments
/// * `callback` - The function to call when receiving AbnormalEvent data.
#[no_mangle]
pub extern "C" fn set_abnormal_event_callback(cb: AbnormalEventCallback) {
  let mut cb_guard = ABNORMAL_EVENT_CALLBACK.write();
  *cb_guard = Some(cb);
}

/// Sets the callback for DFU state changes.
/// This function allows the C code to provide a callback that will be called
/// whenever the DFU state changes during the DFU process.
#[no_mangle]
pub extern "C" fn set_dfu_state_callback(cb: DfuStateCallback) {
  let mut cb_guard = DFU_STATE_CALLBACK.write();
  *cb_guard = Some(cb);
}

/// Sets the callback for DFU progress updates.
/// This function allows the C code to provide a callback that will be called
/// whenever the DFU progress is updated during the DFU process.
/// The callback receives a percentage value indicating the progress,
/// which is in the range of 0.0 to 100.0.
#[no_mangle]
pub extern "C" fn set_dfu_progress_callback(cb: DfuProgressCallback) {
  let mut cb_guard = DFU_PROGRESS_CALLBACK.write();
  *cb_guard = Some(cb);
}

/// Sets the callback for DFU write operations.
/// This function allows the C code to provide a callback that will be called
/// whenever the Rust code needs to write data during the DFU process.
#[no_mangle]
pub extern "C" fn set_dfu_write_callback(cb: DfuWriteCallback) {
  // pub extern "C" fn set_dfu_write_callback(cb: extern "C" fn(data: *const u8, len: usize)) {
  let mut cb_guard = DFU_WRITE_CALLBACK.write();
  *cb_guard = Some(cb);
}

/// Receives a pointer to data and its length from C.
/// The data is borrowed and not freed by this function.
/// The caller is responsible for managing the memory.
#[no_mangle]
pub extern "C" fn did_receive_dfu_data(data: *const u8, len: usize) {
  if data.is_null() || len == 0 {
    return;
  }
  let data = unsafe { std::slice::from_raw_parts(data, len) }.to_vec();
  // info!("did_receive_dfu_data: received {} bytes", data.len());
  let manager_arc = DFU_MANAGER.clone();
  let rt = get_runtime();
  rt.spawn(async move {
    // info!("did_receive_dfu_data: entering async block");
    let manager = manager_arc.lock().await;
    if let Some(tx) = &manager.tx {
      // info!("did_receive_dfu_data: sending data to DFU manager");
      if let Err(e) = tx.send(data).await {
        error!("Failed to send DFU data: {}", e);
      }
    }
  });
}

/// Receives a pointer to data and its length from C.
/// The data is borrowed and not freed by this function.
/// The caller is responsible for managing the memory.
#[no_mangle]
pub extern "C" fn did_receive_data(data: *const u8, len: usize) {
  if data.is_null() || len == 0 {
    // 处理空指针或无效长度的情况
    error!("did_receive_data: invalid data or length");
    return;
  }
  let data = unsafe { std::slice::from_raw_parts(data, len) }.to_vec();
  handle_receive_data(&data);
}

fn get_runtime() -> Arc<Runtime> {
  GLOBAL_RUNTIME.clone()
}

/// 启动 DFU 操作
/// This function allows the C code to start the DFU process with the provided data.
/// It uses the `DfuManager` to handle the DFU operation asynchronously.
#[no_mangle]
pub extern "C" fn start_dfu(file_data: *const u8, len: usize) {
  if file_data.is_null() || len == 0 {
    error!("invalid file_data or len");
    return;
  }

  if is_dfu_in_progress() {
    error!("DFU 操作正在进行中，无法启动新的 DFU");
    return;
  }

  let manager_arc = DFU_MANAGER.clone();
  let data = unsafe { std::slice::from_raw_parts(file_data, len) }.to_vec();

  let rt = get_runtime();
  rt.block_on(async move {
    let result = DfuManager::start_dfu_with_data(manager_arc, data).await;
    if let Err(e) = result {
      error!("start_dfu failed: {}", e);
    } else {
      info!("start_dfu success");
    }
  });
}

/// 中止 DFU 操作
/// This function allows the C code to request an abort of the DFU process.
/// It uses the `DfuManager` to handle the abort operation asynchronously.
#[no_mangle]
pub extern "C" fn abort_dfu() {
  let manager_arc = DFU_MANAGER.clone();
  let rt = get_runtime();
  rt.block_on(async move {
    let result = DfuManager::abort_dfu(manager_arc).await;
    if let Err(e) = result {
      error!("中止 DFU 失败: {}", e);
    } else {
      info!("DFU 中止成功");
    }
  });
}

/// 检查 DFU 是否正在进行中
/// This function allows the C code to check if a DFU operation is currently in progress.
/// It uses the `DfuManager` to check the status asynchronously.
#[no_mangle]
pub extern "C" fn is_dfu_in_progress() -> bool {
  let manager_arc = DFU_MANAGER.clone();
  let rt = get_runtime();
  rt.block_on(async move {
    let manager = manager_arc.lock().await;
    manager.is_dfu_in_progress()
  })
}
