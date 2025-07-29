use parking_lot::Mutex;
use parking_lot::RwLock;

use crate::generated::treadmill_proto::*;
use crate::proto::enums::MsgType;
use crate::proto::msg_parser::Parser;

crate::cfg_import_logging!();

pub type DfuStateCallback = extern "C" fn(state: u8);
pub type DfuProgressCallback = extern "C" fn(percentage: f32); // percentage is in the range of 0.0 to 100.0
pub type DfuWriteCallback = extern "C" fn(data: *const u8, len: usize);
pub type GaitDataCallback = extern "C" fn(
  timmstamp: u32,
  sport_runtime: u32,
  sport_id: u32,
  foot: u8,
  pattern: u8,
  gait_duration: u32,
  step_load: f32,
);
pub type AbnormalEventCallback =
  extern "C" fn(timmstamp: u32, sport_runtime: u32, sport_id: u32, event_type: u8);

lazy_static::lazy_static! {
  pub(crate) static ref DFU_STATE_CALLBACK: RwLock<Option<DfuStateCallback>> = RwLock::new(None);
  pub(crate) static ref DFU_PROGRESS_CALLBACK: RwLock<Option<DfuProgressCallback>> = RwLock::new(None);
  pub(crate) static ref DFU_WRITE_CALLBACK: RwLock<Option<DfuWriteCallback>> = RwLock::new(None);
  pub(crate) static ref GAIT_DATA_CALLBACK: RwLock<Option<GaitDataCallback>> = RwLock::new(None);
  pub(crate) static ref ABNORMAL_EVENT_CALLBACK: RwLock<Option<AbnormalEventCallback>> = RwLock::new(None);
  pub(crate) static ref MSG_PARSER: Mutex<Parser> = Mutex::new(Parser::new("treadmill-device".into(), MsgType::Treadmill));
}

fn run_gait_data_callback(
  timestamp: u32,
  sport_runtime: u32,
  sport_id: u32,
  foot: u8,
  pattern: u8,
  gait_duration: u32,
  step_load: f32,
) {
  cfg_if::cfg_if! {
    if #[cfg(feature = "python")] {
      use crate::python::callback::run_py_gait_data_callback;
      run_py_gait_data_callback(timestamp, sport_runtime, sport_id, foot, pattern, gait_duration, step_load);
    } else {
      let cb = GAIT_DATA_CALLBACK.read();
      if let Some(cb) = &*cb {
        cb(timestamp, sport_runtime, sport_id, foot, pattern, gait_duration, step_load);
      }
    }
  }
}

fn run_abnormal_event_callback(timestamp: u32, sport_runtime: u32, sport_id: u32, event_type: u8) {
  cfg_if::cfg_if! {
    if #[cfg(feature = "python")] {
      use crate::python::callback::run_py_abnormal_event_callback;
      run_py_abnormal_event_callback(timestamp, sport_runtime, sport_id, event_type);
    } else {
      let cb = ABNORMAL_EVENT_CALLBACK.read();
      if let Some(cb) = &*cb {
        cb(timestamp, sport_runtime, sport_id, event_type);
      }
    }
  }
}

pub fn handle_receive_data(data: &[u8]) {
  let mut parser = MSG_PARSER.lock();
  parser.receive_data(data);
}

pub fn on_recv_gait_result(result: GaitAnalysisResult) {
  if result.abnormal_gait > 0 {
    run_abnormal_event_callback(
      result.timestamp,
      result.sport_runtime,
      result.sport_id,
      result.abnormal_gait as u8,
      // AbnormalGait::try_from(result.abnormal_gait).unwrap(),
    );
  }
  if result.pattern > 0 || result.gait_duration > 0 {
    run_gait_data_callback(
      result.timestamp,
      result.sport_runtime,
      result.sport_id,
      result.foot as u8,
      result.pattern as u8,
      result.gait_duration,
      result.step_load,
    );
  } else if result.abnormal_gait <= 0 {
    warn!(
      "invalid gait result: {:?}",
      serde_json::to_string(&result).unwrap_or_default()
    );
  }
}

pub fn run_dfu_write_callback(data: &[u8]) {
  let cb = DFU_WRITE_CALLBACK.read();
  if let Some(cb) = &*cb {
    cb(data.as_ptr(), data.len());
  }
}

pub fn run_dfu_state_callback(state: u8) {
  let cb = DFU_STATE_CALLBACK.read();
  if let Some(cb) = &*cb {
    cb(state);
  }
}

pub fn run_dfu_progress_callback(percentage: f32) {
  let cb = DFU_PROGRESS_CALLBACK.read();
  if let Some(cb) = &*cb {
    cb(percentage);
  }
}

pub fn is_dfu_state_callback_set() -> bool {
  let cb = DFU_STATE_CALLBACK.read();
  cb.is_some()
}

pub fn is_dfu_progress_callback_set() -> bool {
  let cb = DFU_PROGRESS_CALLBACK.read();
  cb.is_some()
}
