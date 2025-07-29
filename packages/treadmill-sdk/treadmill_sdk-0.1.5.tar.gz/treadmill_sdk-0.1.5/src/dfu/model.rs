use crate::{dfu::dfu_manager::OTA_SEGMENT_SIZE, impl_enum_conversion};
use std::{
  fs::File,
  io::{Read, Seek, SeekFrom},
};

crate::cfg_import_logging!();

impl_enum_conversion!(
  DfuCommandType,
  // GetVersion = 0x01,
  StartTransfer = 0x23,
  TransferData = 0x24,
  FinishTransfer = 0x25,
  // GetSystemInfo = 0x27,
  SetDfuMode = 0x41,
  GetFirmwareInfo = 0x42
);

impl_enum_conversion!(
  DfuState,
  Idle = 0x00,
  AwaitingFirmwareInfo = 0x01,
  InDfuMode = 0x02,
  Transferring = 0x03,
  Finished = 0x04,
  Error = 0x05
);

#[derive(Debug, Clone, Copy)]
pub struct TransferProgress {
  pub total_size: usize,
  pub uploaded_size: usize,
  pub percentage: f32,
}

impl TransferProgress {
  pub fn new(total_size: usize, uploaded_size: usize) -> Self {
    let percentage = if total_size > 0 {
      (uploaded_size as f32 / total_size as f32) * 100.0
    } else {
      0.0
    };

    Self {
      total_size,
      uploaded_size,
      percentage,
    }
  }
}

#[derive(Debug, Clone, Copy)]
#[repr(C)]
pub struct FirmwareInfo {
  pub flag: u8,           // 成功返回0x01
  pub copy_address: u32,  // 拷贝地址，0x1080000
  pub firmware_flag: u8,  // 固件标志，固定值0x01
  pub info_type: u16,     // 信息类型，0x44 0x47，'GD' 小端序
  pub version_value: u16, // 版本值，0x00 0x01
  pub size: u32,          // 固件大小，单位为字节
  pub file_crc32: u32,    // 校验和
  pub load_address: u32,  // 加载地址，例如0x1080000，需根据实际硬件配置进行调整
  pub run_address: u32,   // 运行地址，例如0x1020000，需根据实际硬件配置进行调整
  pub xip_control: u32,   // XIP控制命令，固定值0x0000000B
  pub option: u32,        // 固定值
  pub name: [u8; 12],     // 固件名称，长度为12字节, 不足 12 字节时，用空字符（0x00）填充
}

impl FirmwareInfo {
  pub fn from_bytes(bytes: &[u8]) -> anyhow::Result<Self> {
    if bytes.len() < 46 {
      return Err(anyhow::anyhow!("FirmwareInfo data is too short"));
    }
    let mut name = [0u8; 12];
    name.copy_from_slice(&bytes[34..46]);
    Ok(Self {
      flag: bytes[0],
      copy_address: u32::from_le_bytes(bytes[1..5].try_into().unwrap()),
      firmware_flag: bytes[5],
      info_type: u16::from_le_bytes(bytes[6..8].try_into().unwrap()),
      version_value: u16::from_le_bytes(bytes[8..10].try_into().unwrap()),
      size: u32::from_le_bytes(bytes[10..14].try_into().unwrap()),
      file_crc32: u32::from_le_bytes(bytes[14..18].try_into().unwrap()),
      load_address: u32::from_le_bytes(bytes[18..22].try_into().unwrap()),
      run_address: u32::from_le_bytes(bytes[22..26].try_into().unwrap()),
      xip_control: u32::from_le_bytes(bytes[26..30].try_into().unwrap()),
      option: u32::from_le_bytes(bytes[30..34].try_into().unwrap()),
      name,
    })
  }
}

/// 升级开始结构 (命令类型 0x23), StartUpdate = 0x23
#[derive(Debug, Clone)]
pub struct StartUpdate {
  pub flag: u8,           // 固定值 0x00
  pub info_type: u16,     // 信息类型，0x44 0x47，'GD' 小端序
  pub version_value: u16, // 版本值，0x00 0x01
  pub file_size: u32,     // 固件大小，单位为字节
  pub file_crc32: u32,    // 文件的 CRC32 校验和
  pub load_address: u32,  // 加载地址，例如0x1080000，需根据实际硬件配置进行调整
  pub run_address: u32,   // 运行地址，例如0x1020000，需根据实际硬件配置进行调整
  pub xip_control: u32,   // XIP控制命令，固定值0x0000000B
  pub option: u32,        // 固定值
  pub name: [u8; 12],     // 固件名称，长度为12字节, 不足 12 字节时，用空字符（0x00）填充
}

impl From<FirmwareInfo> for StartUpdate {
  fn from(info: FirmwareInfo) -> Self {
    StartUpdate {
      flag: 0x00,
      info_type: info.info_type,
      version_value: info.version_value,
      file_size: info.size,
      file_crc32: info.file_crc32,
      load_address: info.load_address,
      run_address: info.run_address,
      xip_control: info.xip_control,
      option: info.option,
      name: info.name,
    }
  }
}

impl StartUpdate {
  pub fn from_bytes(bytes: &[u8]) -> anyhow::Result<Self> {
    if bytes.len() < 40 {
      return Err(anyhow::anyhow!("StartUpdate data is too short"));
    }
    let mut name = [0u8; 12];
    name.copy_from_slice(&bytes[28..40]);
    Ok(Self {
      flag: 0,
      info_type: u16::from_le_bytes(bytes[0..2].try_into().unwrap()),
      version_value: u16::from_le_bytes(bytes[2..4].try_into().unwrap()),
      file_size: u32::from_le_bytes(bytes[4..8].try_into().unwrap()),
      file_crc32: u32::from_le_bytes(bytes[8..12].try_into().unwrap()),
      load_address: super::frame::FLASH_SAVE_ADDR, // u32::from_le_bytes(bytes[12..16].try_into().unwrap()),
      run_address: u32::from_le_bytes(bytes[16..20].try_into().unwrap()),
      xip_control: u32::from_le_bytes(bytes[20..24].try_into().unwrap()),
      option: u32::from_le_bytes(bytes[24..28].try_into().unwrap()),
      name,
    })
  }

  pub fn to_bytes(&self) -> Vec<u8> {
    let mut bytes = Vec::with_capacity(41);
    bytes.push(self.flag);
    bytes.extend_from_slice(&self.info_type.to_le_bytes());
    bytes.extend_from_slice(&self.version_value.to_le_bytes());
    bytes.extend_from_slice(&self.file_size.to_le_bytes());
    bytes.extend_from_slice(&self.file_crc32.to_le_bytes());
    bytes.extend_from_slice(&self.load_address.to_le_bytes());
    bytes.extend_from_slice(&self.run_address.to_le_bytes());
    bytes.extend_from_slice(&self.xip_control.to_le_bytes());
    bytes.extend_from_slice(&self.option.to_le_bytes());
    bytes.extend_from_slice(&self.name);
    bytes
  }
}

/// 升级数据包结构 (命令类型 0x24)
#[derive(Debug, Clone)]
pub struct UpdateData {
  pub flag: u8,           // 固定值 0x01
  pub write_address: u32, // 写入地址, 0x1080000 + size
  pub data_length: u16,   // 数据包长度（字节）
  pub data: Vec<u8>,      // 数据内容
}

/// 升级完成结构 (命令类型 0x25)
#[derive(Debug, Clone)]
pub struct FinishUpdate {
  pub flag: u8,        // 固定值 0x01
  pub file_crc32: u32, // 校验和
}

/*
// 系统信息结构 (命令类型 0x27)
#[derive(Debug, Clone)]
pub struct SystemInfo {
  pub device_id: [u8; 16],
  pub hardware_version: u16,
  pub firmware_version: u32,
}

// 版本信息结构 (命令类型 0x01)
#[derive(Debug, Clone)]
pub struct VersionInfo {
  pub major: u8,
  pub minor: u8,
  pub patch: u8,
  pub build: u8,
}
*/

// 新增一个接受原始数据的函数
pub fn load_dfu_from_data(file_data: Vec<u8>) -> anyhow::Result<(Vec<u8>, StartUpdate)> {
  info!("load_dfu_from_data, data_size: {}", file_data.len());

  let file_size = file_data.len();
  if file_size <= OTA_SEGMENT_SIZE {
    log::error!("Error: data is too small, size: {}", file_size);
    return Err(anyhow::anyhow!(
      "Data is too small to contain a valid StartUpdate structure"
    ));
  }

  let end_index = file_size - 48; // Exclude the last 48 bytes
  let req = StartUpdate::from_bytes(&file_data[end_index..(end_index + 40)]).map_err(|e| {
    error!("Error parsing StartUpdate: {:?}", e);
    anyhow::anyhow!("Failed to parse StartUpdate: {}", e)
  })?;
  debug!("OTA FW Info: {:?}", req);

  if (req.file_size as usize) != file_data.len() - 48 {
    error!(
      "File size mismatch: expected {}, got {}",
      req.file_size,
      file_data.len() - 48
    );
    return Err(anyhow::anyhow!(
      "File size mismatch: expected {}, got {}",
      req.file_size,
      file_data.len() - 48
    ));
  }

  Ok((file_data, req))
}

pub fn load_dfu_file(file_path: &str) -> anyhow::Result<(Vec<u8>, StartUpdate)> {
  info!("load_dfu_file, file_path: {}", file_path);
  let mut file = match File::open(file_path) {
    Ok(file) => file,
    Err(e) => {
      error!("Error opening ota file: {:?}", e);
      return Err(anyhow::anyhow!("Failed to open file: {}", e));
    }
  };

  // Seek to the end of the file to get the file size
  let file_size = file.seek(SeekFrom::End(0))?;
  info!("load_dfu_file, file_size: {}", file_size);
  if file_size <= OTA_SEGMENT_SIZE.try_into().unwrap() {
    log::error!("Error reading ota file, file_size: {}", file_size);
    return Err(anyhow::anyhow!(
      "File is too small to contain a valid StartUpdate structure"
    ));
  }

  let mut file_data = Vec::new();
  file.seek(SeekFrom::Start(0))?;
  file.read_to_end(&mut file_data)?;
  load_dfu_from_data(file_data)
}
