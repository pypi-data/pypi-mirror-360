use crate::dfu::frame::DfuFrame;
use crate::encrypt::aes_gcm::default_decrypt;
use crate::encrypt::callback::on_recv_gait_result;
use crate::proto::enums::*;
use crate::proto::msg_builder::Builder;
use crate::{generated::treadmill_proto::*, impl_enum_conversion};
use serde::{Deserialize, Serialize};

crate::cfg_import_logging!();

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum TreadmillMessage {
  AnalysisResult(Box<GaitAnalysisResult>),
  DfuFrame(Box<DfuFrame>),
  SensorApp(Box<SensorApp>),
  // Payload(Vec<u8>),
  // Dongle2App(Box<DongleApp>),
}
impl_enum_conversion!(TreadmillModuleId, APP = 1, PITPAT = 2, ALGO = 3, DFU = 0x10);

impl TreadmillMessage {
  pub fn parse_message(payload: &[u8]) -> Result<TreadmillMessage, ParseError> {
    let decrypted = default_decrypt(payload).map_err(|e| ParseError::DecryptError(e.into()))?;
    let resp = decode::<SensorApp>(&decrypted)?;
    // info!("parse_message, decrypted: {:02x?}", decrypted);

    let json_str = serde_json::to_string(&resp).unwrap_or("".to_string());
    #[cfg(any(feature = "examples", feature = "python"))]
    trace!("SensorApp: {:?}", json_str);

    cfg_if::cfg_if! {
      if #[cfg(feature = "python")] {
        use crate::python::callback::*;
        if is_registered_msg_resp() {
          run_msg_resp_callback("".to_string(), json_str);
        }
      }
    }

    if let Some(result) = resp.ga_result {
      on_recv_gait_result(result);
      Ok(TreadmillMessage::AnalysisResult(Box::new(result)))
    } else {
      Ok(TreadmillMessage::SensorApp(Box::new(resp)))
      // let err: anyhow::Error = if cfg!(any(feature = "examples")) {
      //   anyhow::anyhow!(
      //     "No GaitAnalysisResult in SensorApp: {:?}",
      //     serde_json::to_string(&resp).unwrap_or_default()
      //   )
      // } else {
      //   anyhow::anyhow!("No GaitAnalysisResult in SensorApp")
      // };
      // Err(ParseError::ContentError(err))
    }
  }
}

impl Builder {
  pub fn build_to_app(&self, payload: &[u8]) -> Vec<u8> {
    self.build_msg(
      payload,
      TreadmillModuleId::PITPAT.into(),
      TreadmillModuleId::APP.into(),
    )
  }

  pub fn build_to_slave(&self, payload: &[u8]) -> Vec<u8> {
    self.build_msg(
      payload,
      TreadmillModuleId::APP.into(),
      TreadmillModuleId::ALGO.into(),
    )
  }

  pub fn build_dfu_msg(&self, payload: &[u8]) -> Vec<u8> {
    self.build_msg(
      payload,
      TreadmillModuleId::DFU.into(),
      TreadmillModuleId::ALGO.into(),
    )
  }
}

pub mod tml_msg_builder {
  // use crate::generated::treadmill_proto::*;
  use crate::{
    generated::treadmill_proto::{AppSensor, ConfigReqType, GaitAnalysisResult},
    proto::{enums::MsgType, msg_builder::Builder},
  };
  use lazy_static::lazy_static;
  use prost::Message;
  use std::sync::atomic::{AtomicU32, Ordering};
  crate::cfg_import_logging!();

  lazy_static! {
    static ref BUILDER: Builder = Builder::new(MsgType::Treadmill);
    static ref MSG_ID: AtomicU32 = AtomicU32::new(1);
  }

  pub fn gen_msg_id() -> u32 {
    MSG_ID.fetch_add(1, Ordering::SeqCst)
  }

  pub fn build_to_app(payload: &[u8]) -> Vec<u8> {
    BUILDER.build_to_app(&payload)
  }

  pub fn build_dfu_msg(payload: &[u8]) -> Vec<u8> {
    BUILDER.build_dfu_msg(&payload)
  }

  pub fn build_to_slave(payload: &[u8]) -> Vec<u8> {
    BUILDER.build_to_slave(&payload)
  }

  pub fn encode_to_app(msg: GaitAnalysisResult) -> (u32, Vec<u8>) {
    info!(
      "encode_app_to_dongle, msg: {:?}",
      serde_json::to_string(&msg).unwrap_or_else(|_| "".to_string())
    );
    // msg.msg_id = gen_msg_id();
    (msg.msg_id, BUILDER.build_to_app(&msg.encode_to_vec()))
  }

  pub fn get_device_info() -> (u32, Vec<u8>) {
    let msg_id = gen_msg_id();
    let msg = AppSensor {
      msg_id,
      msg_cmd: ConfigReqType::GetDeviceInfo as i32,
      ..Default::default()
    };
    (msg.msg_id, BUILDER.build_to_slave(&msg.encode_to_vec()))
  }
}
