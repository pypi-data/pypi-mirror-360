use treadmill_sdk::encrypt::callback_c::*;
// use treadmill_sdk::generated::crc_bindings::calculateCRC16;
use treadmill_sdk::utils::crc::*;
use treadmill_sdk::utils::logging::LogLevel;

treadmill_sdk::cfg_import_logging!();

/// cargo run --example test_crc
#[tokio::main]
async fn main() -> anyhow::Result<(), anyhow::Error> {
  initialize_logging(LogLevel::Info);
  let str = b"Hello, Device!";
  // unsafe {
  //   let crc16_ef = calculateCRC16(str.as_ptr(), str.len() as u32);
  //   info!("crc16: {:04x}", crc16_ef);
  // }

  // let crc16_custom = calculate_crc16_custom(str);
  // info!("crc16_custom: {:04x}", crc16_custom);

  let crc16_xmodem = calculate_crc16_xmodem(str);
  info!("crc16_xmodem: {:04x}", crc16_xmodem);

  let crc16_ccitt = calculate_crc16_ccitt_false(str);
  info!("crc16_ccitt: {:04x}", crc16_ccitt);

  // let crc16_modbus = calculate_crc16_modbus(str);
  // info!("crc16_modbus: {:04x}", crc16_modbus);

  Ok(())
}
