use nom::{
  bytes::complete::take,
  combinator::{map, map_res, verify},
  error::context,
  number::complete::le_u16,
  IResult, Parser,
};
use serde::{Deserialize, Serialize};

use crate::dfu::model::*;

crate::cfg_import_logging!();

/// DFU 帧协议头标识
pub const FRAME_HEADER: u16 = 0x4744; // 'GD' 小端序

pub const FLASH_SAVE_ADDR: u32 = 0x1080000; // Load address for PROGRAM_START
                                            // FLASH_START_ADDR = 0x01000000
                                            // FLASH_SIZE = 0x00800000
                                            // FLASH_SAVE_ADDR = 0x01080000  # [cite: 15] Load address for PROGRAM_START
                                            // # Command Definitions (L2 - from dfu_master.c and PDF [cite: 9])
                                            // CMD_FRAME_HEADER_L = 0x44  # L2 Header Low Byte [cite: 8]
                                            // CMD_FRAME_HEADER_H = 0x47  # L2 Header High Byte [cite: 8]
                                            // GET_INFO = 0x01  # L2 Command [cite: 9]
                                            // PROGRAM_START = 0x23  # L2 Command [cite: 9]
                                            // PROGRAME_FLASH = 0x24  # L2 Command [cite: 9]
                                            // PROGRAME_END = 0x25  # L2 Command [cite: 9]
                                            // SYSTEM_INFO = 0x27  # L2 Command [cite: 9]
                                            // DFU_MODE_SET = 0x41  # (Not in PDF L2 commands, but in original script)
                                            // DFU_FW_INFO_GET = 0x42  # L2 Command [cite: 9]
                                            // ACK_SUCCESS = 0x01  # [cite: 18]
                                            // ACK_ERROR = 0x02  # [cite: 18]
                                            // DFU_VERSION = 0X02

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct DfuFrame {
  pub header: u16,              // 包头 (0x4744), 小端序
  pub cmd_type: DfuCommandType, // 控制命令类型
  pub length: u16,              // 数据长度
  pub data: Vec<u8>,            // 数据内容
  pub checksum: u16,            // 校验和
}

impl DfuFrame {
  /// 创建新的DFU帧
  pub fn new(cmd_type: DfuCommandType, data: Vec<u8>) -> Self {
    let length = data.len() as u16;
    trace!(
      "创建 DFU 帧: cmd_type = {:?}, length = {}, data = {:02x?}",
      cmd_type,
      length,
      data
    );
    let mut frame = DfuFrame {
      header: FRAME_HEADER,
      cmd_type,
      length,
      data,
      checksum: 0, // 暂时设为0
    };
    // 计算并设置校验和
    frame.checksum = frame.calculate_checksum();
    frame
  }

  pub fn get_firmware_info() -> Self {
    DfuFrame::new(DfuCommandType::GetFirmwareInfo, vec![])
  }

  // pub fn get_system_info() -> Self {
  //   let address: u32 = 0x1000000;
  //   let len: u16 = 0x0030;
  //   let mut data = vec![0x0];
  //   data.extend_from_slice(&address.to_le_bytes());
  //   data.extend_from_slice(&len.to_le_bytes());
  //   DfuFrame::new(DfuCommandType::GetSystemInfo, data)
  // }

  pub fn enter_dfu_mode() -> Self {
    DfuFrame::new(DfuCommandType::SetDfuMode, vec![0x01])
  }

  pub fn start_transfer(info: &StartUpdate) -> Self {
    DfuFrame::new(DfuCommandType::StartTransfer, info.to_bytes())
  }

  pub fn transfer_data(offset: usize, data: &[u8]) -> Self {
    let mut bytes = Vec::with_capacity(7 + data.len());
    bytes.push(0x01);
    // bytes.extend_from_slice(&((FLASH_SAVE_ADDR + offset) as u64).to_le_bytes()); // test exception
    bytes.extend_from_slice(&(FLASH_SAVE_ADDR + offset as u32).to_le_bytes());
    bytes.extend_from_slice(&(data.len() as u16).to_le_bytes());
    bytes.extend_from_slice(data);
    debug!(
      "build transfer_data frame, offset = {}, data_len = {}, bytes_len = {}",
      offset,
      data.len(),
      bytes.len()
    );
    DfuFrame::new(DfuCommandType::TransferData, bytes)
  }

  pub fn finish_transfer(file_crc32: u32) -> Self {
    let mut bytes = Vec::with_capacity(5);
    bytes.push(0x01);
    bytes.extend_from_slice(&file_crc32.to_le_bytes());
    DfuFrame::new(DfuCommandType::FinishTransfer, bytes)
  }

  /// 计算校验和
  pub fn calculate_checksum(&self) -> u16 {
    let mut sum: u16 = 0;

    // 累加包头
    // sum = sum.wrapping_add(self.header);

    // 累加命令类型
    let cmd_type_value: u16 = self.cmd_type as u16;
    sum = sum.wrapping_add(cmd_type_value);

    // 累加长度
    sum = sum.wrapping_add(self.length);

    // 累加数据
    for &byte in &self.data {
      sum = sum.wrapping_add(byte as u16);
    }

    sum
  }

  /// 验证校验和是否正确
  pub fn verify_checksum(&self) -> bool {
    self.calculate_checksum() == self.checksum
  }

  /// 序列化为字节数组
  pub fn encode(&self) -> Vec<u8> {
    let mut buffer = Vec::with_capacity(8 + self.data.len());

    // 写入包头 (小端序)
    buffer.extend_from_slice(&self.header.to_le_bytes());

    // 写入命令类型
    buffer.extend_from_slice(&(self.cmd_type as u16).to_le_bytes());

    // 写入数据长度
    buffer.extend_from_slice(&self.length.to_le_bytes());

    // 写入数据
    buffer.extend_from_slice(&self.data);

    // 写入校验和
    buffer.extend_from_slice(&self.checksum.to_le_bytes());

    buffer
  }
}

pub fn parse_dfu_frame(input: &[u8]) -> IResult<&[u8], DfuFrame> {
  let (input, header) = context("验证帧头", verify(le_u16, |&h| h == FRAME_HEADER)).parse(input)?;

  #[allow(clippy::unnecessary_fallible_conversions)]
  let (input, cmd_type) = context(
    "解析命令类型",
    map_res(le_u16, |val| DfuCommandType::try_from(val as u8)),
  )
  .parse(input)?;

  let (input, length) = context("解析数据长度", le_u16).parse(input)?;

  // 确保有足够的字节用于数据和校验和
  if input.len() < length as usize + 2 {
    return Err(nom::Err::Incomplete(nom::Needed::new(
      length as usize + 2 - input.len(),
    )));
  }

  let (input, data) =
    context("解析数据内容", map(take(length), |d: &[u8]| d.to_vec())).parse(input)?;

  let (input, checksum) = context("解析校验和", le_u16).parse(input)?;

  // 构建帧
  let frame = DfuFrame {
    header,
    cmd_type,
    length,
    data,
    checksum,
  };

  // 验证校验和
  if !frame.verify_checksum() {
    return Err(nom::Err::Error(nom::error::Error::new(
      input,
      nom::error::ErrorKind::Verify,
    )));
  }

  Ok((input, frame))
}

/// 解析多个连续帧
pub fn parse_multiple_frames(
  mut input: &[u8],
) -> Vec<Result<DfuFrame, nom::Err<nom::error::Error<&[u8]>>>> {
  let mut frames = Vec::new();

  while !input.is_empty() {
    match parse_dfu_frame(input) {
      Ok((rest, frame)) => {
        frames.push(Ok(frame));
        input = rest;
      }
      Err(e) => {
        frames.push(Err(e));
        break;
      }
    }
  }

  frames
}
