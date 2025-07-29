crate::cfg_import_logging!();

use super::{constants::*, enums::*};

use crate::utils::crc::*;

pub struct Builder {
  pub msg_type: MsgType,
  header_version: u8,
  header_flag: u8,
  header_prefix: Vec<u8>,
}

impl Builder {
  pub fn new(msg_type: MsgType) -> Self {
    let (project_id, header_version, header_length) = get_project_info(msg_type);
    let header_flag = 0;
    let payload_version = 1;
    let mut header_prefix = Vec::new();
    if msg_type == MsgType::Stark {
      header_prefix.extend_from_slice(&PROTO_HEADER_MAGIC_BNCP);
    } else {
      header_prefix.extend_from_slice(&PROTO_HEADER_MAGIC);
      header_prefix.push(header_version);
      header_prefix.push(project_id);
      if header_version == HEADER_VERSION_V2 && header_length == 12 {
        header_prefix.push(payload_version);
      }
    }
    debug!(
      "BuilderType: {:?}, Project ID: 0x{:x}, Header version: {}, header_prefix: {:02x?}",
      msg_type, project_id, header_version, header_prefix,
    );

    Builder {
      msg_type,
      header_version,
      header_flag,
      header_prefix,
    }
  }

  pub fn build(&self, payload: &[u8]) -> Vec<u8> {
    self.build_msg(payload, 0, 0)
  }

  pub fn build_msg(&self, payload: &[u8], src_module: u8, dst_module: u8) -> Vec<u8> {
    self.wrap_message(payload, src_module, dst_module)
  }

  pub fn wrap_message(&self, payload: &[u8], src_module: u8, dst_module: u8) -> Vec<u8> {
    let mut msg = Vec::new();
    msg.extend_from_slice(&self.header_prefix);
    msg.extend_from_slice(&(payload.len() as u16).to_le_bytes());
    // info!("header_version: {}", self.header_version);
    if self.header_version == HEADER_VERSION_V2 {
      msg.push(src_module);
      msg.push(dst_module);
      msg.push(self.header_flag);
    }
    msg.extend_from_slice(payload);
    // let crc16 = calculate_crc16_modbus(&msg);
    let crc16 = calculate_crc16_xmodem(&msg);
    msg.extend_from_slice(&crc16.to_le_bytes());
    msg
  }
}
