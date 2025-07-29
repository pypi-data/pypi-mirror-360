use crate::proto::enums::*;
use crate::proto::msg_builder::Builder;
use crate::{generated::edu_proto::*, impl_enum_conversion};

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum EduMessage {
  App2Dongle(Box<AppDongle>),
  Dongle2App(Box<DongleApp>),
  App2Sensor(Box<AppSensor>),
  Sensor2App(Box<SensorApp>),
  AppToCtrlBox(Box<AppToControlBox>),
  CtrlBoxToApp(Box<ControlBoxToApp>),
}
impl_enum_conversion!(EduModuleId, APP = 1, DONGLE = 2, DEVICE = 3);

impl EduMessage {
  const PARSE_TYPE: MsgType = MsgType::Edu;
  pub fn parse_message(
    src_module: u8,
    dst_module: u8,
    payload: &[u8],
  ) -> Result<EduMessage, ParseError> {
    if EduModuleId::APP == src_module.into() {
      Self::parse_req_message(dst_module, payload)
    } else if EduModuleId::APP == dst_module.into() {
      Self::parse_resp_message(src_module, payload)
    } else {
      Err(ParseError::InvalidModule(
        Self::PARSE_TYPE,
        src_module,
        dst_module,
      ))
    }
  }

  fn parse_req_message(dst_module: u8, payload: &[u8]) -> Result<EduMessage, ParseError> {
    let module: EduModuleId = dst_module.into();
    match module {
      EduModuleId::DONGLE => {
        let req = decode::<AppDongle>(payload)?;
        Ok(EduMessage::App2Dongle(Box::new(req)))
      }
      EduModuleId::DEVICE => {
        if !edu_msg_builder::is_via_mcu() {
          let req = decode::<AppSensor>(payload)?;
          Ok(EduMessage::App2Sensor(Box::new(req)))
        } else {
          let req = decode::<AppToControlBox>(payload)?;
          Ok(EduMessage::AppToCtrlBox(Box::new(req)))
        }
      }
      _ => Err(ParseError::InvalidDestinationModule(
        Self::PARSE_TYPE,
        dst_module,
      )),
    }
  }

  fn parse_resp_message(src_module: u8, payload: &[u8]) -> Result<EduMessage, ParseError> {
    let module: EduModuleId = src_module.into();
    match module {
      EduModuleId::DONGLE => {
        let resp = decode::<DongleApp>(payload)?;
        Ok(EduMessage::Dongle2App(Box::new(resp)))
      }
      EduModuleId::DEVICE => {
        if !edu_msg_builder::is_via_mcu() {
          let resp = decode::<SensorApp>(payload)?;
          Ok(EduMessage::Sensor2App(Box::new(resp)))
        } else {
          let resp = decode::<ControlBoxToApp>(payload)?;
          Ok(EduMessage::CtrlBoxToApp(Box::new(resp)))
        }
      }
      _ => Err(ParseError::InvalidSourceModule(
        Self::PARSE_TYPE,
        src_module,
      )),
    }
  }
}

impl Builder {
  pub fn build_edu_to_dongle(&self, payload: &[u8]) -> Vec<u8> {
    self.build_msg(payload, EduModuleId::APP as u8, EduModuleId::DONGLE as u8)
  }

  pub fn build_edu_to_device(&self, payload: &[u8]) -> Vec<u8> {
    self.build_msg(payload, EduModuleId::APP as u8, EduModuleId::DEVICE as u8)
  }
}

pub mod edu_msg_builder {
  use crate::generated::edu_proto::*;
  use crate::proto::{enums::MsgType, msg_builder::Builder};
  use lazy_static::lazy_static;
  use prost::Message;
  use std::sync::atomic::{AtomicBool, AtomicU32, Ordering};
  crate::cfg_import_logging!();

  lazy_static! {
    static ref BUILDER: Builder = Builder::new(MsgType::Edu);
    static ref VIA_MCU: AtomicBool = AtomicBool::new(false);
    static ref MSG_ID: AtomicU32 = AtomicU32::new(1);
  }

  fn gen_msg_id() -> u32 {
    MSG_ID.fetch_add(1, Ordering::SeqCst)
  }

  pub fn set_via_mcu(via_mcu: bool) {
    VIA_MCU.store(via_mcu, Ordering::SeqCst);
  }

  pub fn is_via_mcu() -> bool {
    VIA_MCU.load(Ordering::SeqCst)
  }

  pub fn encode_app_to_dongle(msg: AppDongle) -> (u32, Vec<u8>) {
    info!(
      "encode_app_to_dongle, msg: {:?}",
      serde_json::to_string(&msg).unwrap_or_else(|_| "".to_string())
    );
    (
      msg.msg_id,
      BUILDER.build_edu_to_dongle(&msg.encode_to_vec()),
    )
  }

  pub fn encode_app_to_mcu(msg: AppToControlBox) -> (u32, Vec<u8>) {
    info!(
      "encode_app_to_mcu, msg: {:?}",
      serde_json::to_string(&msg).unwrap_or_else(|_| "".to_string())
    );
    (
      msg.msg_id,
      BUILDER.build_edu_to_device(&msg.encode_to_vec()),
    )
  }

  pub fn encode_app_to_sensor(msg: AppSensor) -> (u32, Vec<u8>) {
    info!(
      "encode_app_to_sensor, {:?}",
      serde_json::to_string(&msg).unwrap_or_else(|_| "".to_string())
    );
    (
      msg.msg_id,
      BUILDER.build_edu_to_device(&msg.encode_to_vec()),
    )
  }

  pub fn get_dongle_info() -> (u32, Vec<u8>) {
    let msg_id = gen_msg_id();
    let msg_type = app_dongle::MsgType::ConfigGet as i32;
    let msg = AppDongle {
      msg_id,
      msg_type,
      ..Default::default()
    };
    encode_app_to_dongle(msg)
  }

  pub fn get_dongle_pair_cfg() -> (u32, Vec<u8>) {
    let msg_id = gen_msg_id();
    let msg_type = app_dongle::MsgType::PairGet as i32;
    let msg = AppDongle {
      msg_id,
      msg_type,
      ..Default::default()
    };
    encode_app_to_dongle(msg)
  }

  pub fn get_dongle_pair_stat() -> (u32, Vec<u8>) {
    let msg_id = gen_msg_id();
    let msg_type = app_dongle::MsgType::PairStat as i32;
    let msg = AppDongle {
      msg_id,
      msg_type,
      ..Default::default()
    };
    encode_app_to_dongle(msg)
  }

  pub fn get_device_info() -> (u32, Vec<u8>) {
    let msg_id = gen_msg_id();
    let msg_cmd = ConfigReqType::GetDeviceInfo as i32;
    if is_via_mcu() {
      let msg = AppToControlBox {
        msg_id,
        msg_cmd,
        ..Default::default()
      };
      encode_app_to_mcu(msg)
    } else {
      let msg = AppSensor {
        msg_id,
        msg_cmd,
        ..Default::default()
      };
      encode_app_to_sensor(msg)
    }
  }

  pub fn get_port_stat() -> (u32, Vec<u8>) {
    let msg_id = gen_msg_id();
    let msg_cmd = ConfigReqType::GetPortStat as i32;
    if is_via_mcu() {
      let msg = AppToControlBox {
        msg_id,
        msg_cmd,
        ..Default::default()
      };
      encode_app_to_mcu(msg)
    } else {
      let msg = AppSensor {
        msg_id,
        msg_cmd,
        ..Default::default()
      };
      encode_app_to_sensor(msg)
    }
  }

  pub fn get_sensor_cfg() -> (u32, Vec<u8>) {
    let msg_id = gen_msg_id();
    let msg_cmd = ConfigReqType::GetSensorConfig as i32;
    if is_via_mcu() {
      let msg = AppToControlBox {
        msg_id,
        msg_cmd,
        ..Default::default()
      };
      encode_app_to_mcu(msg)
    } else {
      let msg = AppSensor {
        msg_id,
        msg_cmd,
        ..Default::default()
      };
      encode_app_to_sensor(msg)
    }
  }

  pub fn start_data_stream() -> (u32, Vec<u8>) {
    let msg_id = gen_msg_id();
    let msg_cmd = ConfigReqType::StartDataStream as i32;
    if is_via_mcu() {
      let msg = AppToControlBox {
        msg_id,
        msg_cmd,
        ..Default::default()
      };
      encode_app_to_mcu(msg)
    } else {
      let msg = AppSensor {
        msg_id,
        msg_cmd,
        ..Default::default()
      };
      encode_app_to_sensor(msg)
    }
  }

  pub fn stop_data_stream() -> (u32, Vec<u8>) {
    let msg_id = gen_msg_id();
    let msg_cmd = ConfigReqType::StopDataStream as i32;
    if is_via_mcu() {
      let msg = AppToControlBox {
        msg_id,
        msg_cmd,
        ..Default::default()
      };
      encode_app_to_mcu(msg)
    } else {
      let msg = AppSensor {
        msg_id,
        msg_cmd,
        ..Default::default()
      };
      encode_app_to_sensor(msg)
    }
  }

  pub fn set_afe_config(sample_rate: i32, channel_bits: u32) -> (u32, Vec<u8>) {
    let afe_config = AfeConfig {
      sample_rate,
      channel_bits,
      ..Default::default()
    };
    let msg_id = gen_msg_id();
    if is_via_mcu() {
      let msg = AppToControlBox {
        msg_id,
        afe_config: Some(afe_config),
        ..Default::default()
      };
      encode_app_to_mcu(msg)
    } else {
      let msg = AppSensor {
        msg_id,
        afe_config: Some(afe_config),
        ..Default::default()
      };
      encode_app_to_sensor(msg)
    }
  }

  pub fn set_ppg_config(ppg_mode: i32, ppg_ur: i32) -> (u32, Vec<u8>) {
    let ppg_config = PpgConfig {
      ppg_mode,
      ppg_ur,
      ..Default::default()
    };

    let msg_id = gen_msg_id();
    // if is_via_mcu() {
    //   let msg = AppToControlBox {
    //     msg_id,
    //     ppg_config: Some(ppg_config),
    //     ..Default::default()
    //   };
    //   encode_app_to_mcu(msg)
    // } else {
    let msg = AppSensor {
      msg_id,
      ppg_config: Some(ppg_config),
      ..Default::default()
    };
    encode_app_to_sensor(msg)
    // }
  }

  pub fn set_imu_config(imu_mode: i32, imu_sr: i32, _port: i32, _data_type: i32) -> (u32, Vec<u8>) {
    let imu_config = ImuConfig {
      imu_mode,
      imu_sr,
      // port,
      // data_type,
      // imu_calibration
      ..Default::default()
    };

    let msg_id = gen_msg_id();
    if is_via_mcu() {
      let msg = AppToControlBox {
        msg_id,
        imu_config: Some(imu_config),
        ..Default::default()
      };
      encode_app_to_mcu(msg)
    } else {
      let msg = AppSensor {
        msg_id,
        imu_config: Some(imu_config),
        ..Default::default()
      };
      encode_app_to_sensor(msg)
    }
  }

  pub fn set_mag_config(mag_sr: i32, data_type: i32) -> (u32, Vec<u8>) {
    let mag_config = MagConfig {
      mag_sr,
      data_type,
      // mag_calibration
      ..Default::default()
    };
    let msg_id = gen_msg_id();
    if is_via_mcu() {
      let msg = AppToControlBox {
        msg_id,
        mag_config: Some(mag_config),
        ..Default::default()
      };
      encode_app_to_mcu(msg)
    } else {
      let msg = AppSensor {
        msg_id,
        mag_config: Some(mag_config),
        ..Default::default()
      };
      encode_app_to_sensor(msg)
    }
  }

  pub fn set_acc_config(acc_sr: i32, port: i32, data_type: i32) -> (u32, Vec<u8>) {
    let acc_config = AccConfig {
      acc_sr,
      port,
      data_type,
      // imu_calibration
      ..Default::default()
    };
    let msg_id = gen_msg_id();
    if is_via_mcu() {
      let msg = AppToControlBox {
        msg_id,
        acc_config: Some(acc_config),
        ..Default::default()
      };
      encode_app_to_mcu(msg)
    } else {
      let msg = AppSensor {
        msg_id,
        acc_config: Some(acc_config),
        ..Default::default()
      };
      encode_app_to_sensor(msg)
    }
  }

  pub fn set_flex_config(sample_rate: i32) -> (u32, Vec<u8>) {
    let flex_config = FlexConfig {
      sample_rate,
      ..Default::default()
    };
    let msg_id = gen_msg_id();
    if is_via_mcu() {
      let msg = AppToControlBox {
        msg_id,
        flex_config: Some(flex_config),
        ..Default::default()
      };
      encode_app_to_mcu(msg)
    } else {
      let msg = AppSensor {
        msg_id,
        flex_config: Some(flex_config),
        ..Default::default()
      };
      encode_app_to_sensor(msg)
    }
  }
}
