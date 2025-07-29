use super::constants::*;
use crate::impl_enum_conversion;
use prost::{DecodeError, Message};
use serde::{Deserialize, Serialize};
use thiserror::Error;

crate::cfg_import_logging!();

impl_enum_conversion!(
  MsgType,
  Crimson = 0,
  OxyZen = 1,
  Mobius = 3,
  MobiusV1_5 = 4,
  Almond = 5,
  AlmondV2 = 6,
  Morpheus = 2,
  Luna = 7,
  REN = 8,
  Breeze = 9,
  Stark = 0xa,
  EEGCap = 0xb, // EEG Cap with 32 channels
  Edu = 0xc,
  Clear = 0xd,
  Melody = 0xf,
  Aura = 0x10,
  Treadmill = 0x13
);

pub fn get_project_info(msg_type: MsgType) -> (u8, u8, usize) {
  let (project_id, header_version, header_length) = match msg_type {
    MsgType::Edu => (0xc, HEADER_VERSION_V2, 11), // NOTE: Edu has 11 bytes header
    // MsgType::Treadmill => (0x0c, HEADER_VERSION_V2, 11),
    MsgType::Treadmill => (0x13, HEADER_VERSION_V2, 11), // NOTE: Treadmill has 11 bytes header
    #[allow(unreachable_patterns)]
    _ => (0, 0, 0),    // Default values
  };
  (project_id, header_version, header_length)
}

// #[wasm_bindgen]
#[derive(Debug, Error)]
pub enum ParseError {
  #[error("Unknown proto type: {0:?}")]
  UnknownProtoType(MsgType),

  #[error("Unsupported header version: {0:?}, {1}")]
  UnsupportedHeaderVersion(MsgType, u8),

  #[error("Unsupported payload version: {0:?}, {1}")]
  UnsupportedPayloadVersion(MsgType, u8),

  #[error("Invalid source module: {0:?}, {1:?}")]
  InvalidSourceModule(MsgType, u8),

  #[error("Invalid destination module: {0:?}, {1:?}")]
  InvalidDestinationModule(MsgType, u8),

  #[error("Invalid module: {0:?}, {1}, {2}")]
  InvalidModule(MsgType, u8, u8),

  #[error("Decoding error for {0}")]
  DecodingError(DecodeError),

  #[error("Decrypt error for {0}")]
  DecryptError(anyhow::Error),

  #[error("Content error for {0}")]
  ContentError(anyhow::Error),

  #[error("Decoding Json error for {0}")]
  JsonError(serde_json::Error),
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ParsedMessage {
  Treadmill(super::treadmill::msg_builder::TreadmillMessage),
}

pub fn handle_resp_message(device_id: String, message: &ParsedMessage) {
  debug!(
    "Received message, device_id: {:?}, message: {:?}",
    device_id, message
  );
}

pub fn decode<T>(payload: &[u8]) -> Result<T, ParseError>
where
  T: Message + Default,
{
  match T::decode(payload) {
    Ok(res) => Ok(res),
    Err(e) => {
      error!(
        "Decoding error for type {}: {:?}",
        std::any::type_name::<T>(),
        payload
      );
      Err(ParseError::DecodingError(e))
    }
  }
}
