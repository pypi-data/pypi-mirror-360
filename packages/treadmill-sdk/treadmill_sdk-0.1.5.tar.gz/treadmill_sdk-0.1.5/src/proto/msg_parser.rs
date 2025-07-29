use super::treadmill::msg_builder::*;
use super::{constants::*, enums::*};
use crate::dfu::frame::*;
use crate::utils::crc::*;
use byteorder::{BigEndian, ByteOrder, LittleEndian};
use std::pin::Pin;
use std::sync::Arc;
use tokio::sync::{broadcast, Mutex};
use tokio_stream::wrappers::errors::BroadcastStreamRecvError;
use tokio_stream::wrappers::BroadcastStream;
use tokio_stream::Stream;

crate::cfg_import_logging!();

pub type StreamType =
  Pin<Box<dyn Stream<Item = Result<(String, ParsedMessage), BroadcastStreamRecvError>> + Send>>;

pub type ArcMutexStream = Arc<Mutex<StreamType>>;

pub type TcpStreamType =
  Pin<Box<dyn Stream<Item = Result<Vec<u8>, BroadcastStreamRecvError>> + Send>>;

pub type ArcMutexTcpStream = Arc<Mutex<TcpStreamType>>;

lazy_static::lazy_static! {
  static ref PREVIOUS_TIMESTAMP: std::sync::Mutex<Option<u32>> = std::sync::Mutex::new(None);
}
#[derive(Debug, Clone)]
pub struct Parser {
  pub device_id: String,
  pub msg_type: MsgType,
  pub tx: broadcast::Sender<(String, ParsedMessage)>,
  pub rx: Arc<broadcast::Receiver<(String, ParsedMessage)>>,

  header_version: u8,
  header_prefix: Vec<u8>,
  header_length: usize,

  buffer: Vec<u8>,
  expected_length: usize,
  padding_size: usize,

  // padding_size: u16,
  pub padding_4x: bool,
}

impl Parser {
  pub fn new(device_id: String, msg_type: MsgType) -> Self {
    let (project_id, header_version, header_length) = get_project_info(msg_type);
    let mut header_prefix = Vec::new();

    let mut padding_4x: bool = false;
    if msg_type == MsgType::Stark {
      header_prefix.extend_from_slice(&PROTO_HEADER_MAGIC_BNCP);
      padding_4x = true;
    } else {
      header_prefix.extend_from_slice(&PROTO_HEADER_MAGIC);
      header_prefix.push(header_version);
      header_prefix.push(project_id);
      let payload_version = 1;
      if header_version == HEADER_VERSION_V2 && header_length == 12 {
        header_prefix.push(payload_version);
      }
    }
    debug!(
      "ParserType: {:?}, Project ID: 0x{:x}, Header version: {}, header_prefix: {:02x?}",
      msg_type, project_id, header_version, header_prefix,
    );

    let (tx, rx) = broadcast::channel(10000); // 创建消息发送器和接收器
    Parser {
      device_id,
      msg_type,
      tx,
      rx: Arc::new(rx),
      header_version,
      header_prefix,
      header_length,
      buffer: Vec::with_capacity(BUFFER_MAX_SIZE),
      expected_length: 0,
      padding_size: 0,
      padding_4x,
    }
  }

  pub fn message_stream(&self) -> StreamType {
    let rx = self.tx.subscribe(); // 每次调用都创建一个新的 Receiver
    Box::pin(BroadcastStream::new(rx))
  }

  pub fn receive_data(&mut self, data: &[u8]) {
    if data.is_empty() {
      error!("Data should not be empty");
      return;
    }

    if self.buffer.len() + data.len() > BUFFER_MAX_SIZE {
      self.clear_buffer();
      error!(
        "Buffer is out of space. (BUFFER_MAX_SIZE = {}), buffer length: {}, data len: {}",
        BUFFER_MAX_SIZE,
        self.buffer.len(),
        data.len()
      );
      return;
    }
    self.buffer.extend_from_slice(data);
    self.process_buffer();
  }

  fn process_buffer(&mut self) {
    if self.buffer.len() <= self.header_length {
      trace!("Buffer length: {}", self.buffer.len());
      return;
    }

    if self.expected_length == 0 {
      match self.find_header_index() {
        Some(index) => {
          if index > 0 {
            warn!(
              "Found header at index: {}, unexpected_data: {:?}",
              index,
              &self.buffer[..index]
            );
            self.trim_buffer(index);
          }
        }
        None => {
          warn!(
            "Proto header is mismatch, drop the message, buffer: {:02x?}",
            self.buffer
          );
          warn!("header_prefix: {:02x?}", self.header_prefix);
          self.handle_unexpected_data();
          return;
        }
      }

      if let Ok((expected_length, padding_size)) = self.get_expected_length() {
        self.expected_length = expected_length;
        self.padding_size = padding_size;
      } else {
        error!(
          "Failed to calculate expected length, buffer: {:02x?}",
          self.buffer
        );
        self.handle_unexpected_data();
        return;
      }
    }

    // info!(
    //   "Expected length: {}, buffer length: {}",
    //   self.expected_length,
    //   self.buffer.len()
    // );
    if self.expected_length > self.buffer.len() {
      trace!(
        "Expected length: {}, buffer length: {}",
        self.expected_length,
        self.buffer.len()
      );
      return;
    }

    if self.verify_crc_footer() {
      trace!(
        "CRC verification passed, buffer: {:02x?}",
        &self.buffer[..self.expected_length]
      );
      let footer_len = if self.header_version == HEADER_VERSION_STARK {
        PROTO_FOOTER_CRC32
      } else {
        PROTO_FOOTER_CRC16
      };
      let begin_idx = self.header_length;
      let end_idx = self.expected_length - self.padding_size - footer_len;
      let payload = &self.buffer[begin_idx..end_idx];
      // trace!(
      //   "Payload: {:02x?}, begin_idx: {}, end_idx: {}, expected_length: {}, padding_size: {}",
      //   payload, begin_idx, end_idx, self.expected_length, self.padding_size
      // );
      // trace!(
      //   "header_length: {}, footer_len: {}, padding_size: {}",
      //   self.header_length, footer_len, self.padding_size
      // );
      if let Err(e) = self.parse_message(payload) {
        error!("Failed to parse message, error: {:?}", e);
        self.handle_unexpected_data();
        return;
      }
    } else {
      error!("CRC verification failed");
      self.handle_unexpected_data();
      return;
    }

    self.handle_complete_message();
  }

  fn parse_next_message(&mut self) {
    if self.find_header_index().is_some() {
      trace!("parsing next message");
      self.process_buffer();
    }
  }

  fn handle_complete_message(&mut self) {
    self.trim_buffer(self.expected_length);
    self.expected_length = 0;
    self.padding_size = 0;
    self.parse_next_message();
  }

  fn handle_unexpected_data(&mut self) {
    self.trim_buffer(self.header_prefix.len());
    match self.find_header_index() {
      Some(index) => {
        if index > 0 {
          self.trim_buffer(index);
        }
        self.expected_length = 0;
        self.padding_size = 0;
        self.parse_next_message();
      }
      _ => {
        self.clear_buffer();
      }
    }
  }

  fn trim_buffer(&mut self, shift_amount: usize) {
    self.buffer.drain(..shift_amount);
  }

  fn clear_buffer(&mut self) {
    self.buffer.clear();
    self.expected_length = 0;
  }

  fn find_header_index(&self) -> Option<usize> {
    let prefix_len = self.header_prefix.len();

    if self.buffer.len() < prefix_len {
      return None;
    }

    (0..=(self.buffer.len() - prefix_len))
      .find(|&i| self.buffer[i..i + prefix_len] == self.header_prefix[..])
  }

  fn get_expected_length(&self) -> Result<(usize, usize), ()> {
    if self.buffer.len() < self.header_length {
      return Err(());
    }

    let len = self.header_prefix.len();
    let mut padding_size: usize = 0;
    let expected_length = if self.header_version == HEADER_VERSION_STARK {
      let pkt_size = usize::from(self.buffer[6]) * 256
        + usize::from(self.buffer[7])
        + self.header_length
        + PROTO_FOOTER_CRC32;
      // info!("self.header_length: {}", self.header_length);
      // info!("Packet size: {}", pkt_size);
      padding_size = (4 - (pkt_size % 4)) % 4;
      // info!("Padding size: {}", padding_size);
      pkt_size + padding_size
    } else {
      usize::from(self.buffer[len])
        + usize::from(self.buffer[len + 1]) * 256
        + self.header_length
        + PROTO_FOOTER_CRC16
    };

    // if self.padding_4x {
    //   let padding_size = (4 - (expected_length % 4)) % 4;
    //   return Ok(expected_length + padding_size);
    // }

    Ok((expected_length, padding_size))
  }

  fn verify_crc_footer(&self) -> bool {
    let end_idx = self.expected_length;
    if self.header_version == HEADER_VERSION_STARK {
      let begin_idx = self.expected_length - PROTO_FOOTER_CRC32;
      // info!("CRC32: {:02X?}", &self.buffer[begin_idx..end_idx]);
      // info!("CRC32: {:02X?}", &self.buffer);
      // info!("begin_idx: {}, end_idx: {}", begin_idx, end_idx);
      let crc32 = BigEndian::read_u32(&self.buffer[begin_idx..end_idx]);
      let crc_calc = calculate_crc32(&self.buffer[..begin_idx]);
      if crc32 == crc_calc {
        true
      } else {
        error!(
          "CRC32 verification failed, expected: {:08X}, calculated: {:08X}",
          crc32, crc_calc
        );
        false
      }
    } else {
      let begin_idx = self.expected_length - PROTO_FOOTER_CRC16;
      let crc16 = LittleEndian::read_u16(&self.buffer[begin_idx..end_idx]);
      // let crc_calc = calculate_crc16_modbus(&self.buffer[..begin_idx]);
      let crc_calc = calculate_crc16_xmodem(&self.buffer[..begin_idx]);
      // let crc_calc = unsafe { calculateCRC16(self.buffer[..begin_idx].as_ptr(), begin_idx as u32) };
      // info!(
      //   "CRC16: {:04X}, calculated: {:04X}, expected_length: {:?}, buffer: {:02x?}",
      //   crc16,
      //   crc_calc,
      //   self.expected_length,
      //   &self.buffer[..end_idx]
      // );
      if crc16 == crc_calc {
        true
      } else {
        error!(
          "CRC16 verification failed, expected: {:04X}, calculated: {:04X}, expected_length: {:?}, buffer: {:02x?}",
          crc16, crc_calc, self.expected_length, &self.buffer[..end_idx]
        );
        false
      }
    }
  }

  fn parse_message(&self, payload: &[u8]) -> Result<(), ParseError> {
    match self.header_version {
      HEADER_VERSION_V1 => self.parse_message_for_header_v1(payload),
      HEADER_VERSION_V2 => {
        let src_module = self.buffer[self.header_length - 3];
        let dst_module = self.buffer[self.header_length - 2];
        trace!(
          "Source module: {}, Destination module: {}, payload: {:?}",
          src_module,
          dst_module,
          payload
        );
        self.parse_message_for_header_v2(src_module, dst_module, payload)
      }
      _ => Err(ParseError::UnsupportedHeaderVersion(
        self.msg_type,
        self.header_version,
      )),
    }
  }

  #[allow(unused_variables)]
  fn parse_message_for_header_v1(&self, payload: &[u8]) -> Result<(), ParseError> {
    Ok(())
  }

  #[allow(unused_variables, unreachable_code)]
  fn parse_message_for_header_v2(
    &self,
    src_module: u8,
    dst_module: u8,
    payload: &[u8],
  ) -> Result<(), ParseError> {
    // trace!(
    //   "Message type: {:?}, Source module: {}, Destination module: {}, payload: {:02x?}",
    //   self.msg_type,
    //   src_module,
    //   dst_module,
    //   payload
    // );
    let result = match self.msg_type {
      // #[cfg(feature = "edu")]
      // MsgType::Edu => {
      //   let message = EduMessage::parse_message(src_module, dst_module, payload)?;
      //   // info!("EduMessage: {:?}", message);
      //   ParsedMessage::Edu(message)
      // }
      MsgType::Treadmill => {
        if dst_module == TreadmillModuleId::DFU as u8 {
          let (_, frame) = parse_dfu_frame(payload)
            .map_err(|e| ParseError::ContentError(anyhow::Error::msg("parse_dfu_frame error")))?;
          let message = TreadmillMessage::DfuFrame(Box::new(frame));
          // info!("TreadmillMessage: {:?}", message);
          ParsedMessage::Treadmill(message)
        } else {
          let message = TreadmillMessage::parse_message(payload)?;
          // info!("TreadmillMessage: {:?}", message);
          ParsedMessage::Treadmill(message)
        }
      }
      #[allow(unreachable_patterns)]
      _ => return Err(ParseError::UnknownProtoType(self.msg_type)),
    };

    #[cfg(feature = "examples")]
    match serde_json::to_string(&result) {
      Ok(json) => debug!("Decoded message: {:?}", json),
      Err(e) => return Err(ParseError::JsonError(e)),
    }

    // 通知消息
    self.notify_message(result);
    Ok(())
  }

  pub fn notify_message(&self, result: ParsedMessage) {
    let device_id = self.device_id.clone();
    let tx = self.tx.clone();
    let _ = tx.send((device_id, result));
  }
}

#[cfg(not(target_family = "wasm"))]
#[cfg(test)]
mod tests {
  use futures::StreamExt;
  crate::cfg_import_logging!();

  use super::StreamType;
  use crate::proto::{enums::MsgType, msg_parser::Parser};
  use crate::utils::logging_desktop::init_logging;

  fn _test() {
    init_logging(log::Level::Debug);
    let parser = Parser::new("test-device".into(), MsgType::EEGCap);
    let stream: StreamType = parser.message_stream();
    read_data(stream);
  }

  #[allow(dead_code)]
  fn read_data(mut stream: StreamType) {
    // 处理流中的消息
    tokio::spawn(async move {
      while let Some(result) = stream.next().await {
        match result {
          Ok(message) => {
            info!("Received message: {:?}", message);
          }
          Err(e) => {
            error!("Error receiving message: {:?}", e);
          }
        }
      }
      info!("Stream finished");
    });
  }
}
