use std::fs::File;
use std::io::BufRead;
use std::io::BufReader;
use std::thread::sleep;
use std::time::Duration;
use treadmill_sdk::encrypt::callback::*;
use treadmill_sdk::encrypt::callback_c::*;
// use treadmill_sdk::generated::treadmill_proto::gait_analysis_result::GaitPattern;
// use treadmill_sdk::generated::treadmill_proto::AbnormalGait;
use treadmill_sdk::utils::logging::LogLevel;

treadmill_sdk::cfg_import_logging!();

/// cargo run --example test_mock_data
#[tokio::main]
async fn main() -> anyhow::Result<(), anyhow::Error> {
  initialize_logging(LogLevel::Debug);

  set_gait_data_callback(on_gait_analysis_result);
  set_abnormal_event_callback(on_abnormal_event);
  //   let hex_str_fw = "42 52 4E 43 02 13 1E 00 03 01 A5 5A ED A9 F1 8A E0 15 7C 0A FF E5 F3 3D 7F 59 28 BE 6C 53 7D EE 0C 40 94 B7 E6 72 26 56 D5 C4 9E
  // 42 52 4E 43 02 13 1F 00 03 01 A5 5A EC A9 E5 8A C0 B9 65 13 D6 25 1C 6A 2E 88 D7 B0 4F 5D 52 E9 E6 0D 4B 47 07 1B 0F DF 2A DC AC 73";
  //   let hex_str_fw = "42 52 4E 43 02 13 1C 00 03 01 A5 5A EB A9 C0 8A CC 84 67 3B D4 4D C6 F5 AD 58 EE 40 13 AF D3 3C 1A 4C 32 71 6A 6C 1F B2 A9";
  //   let hex_str_fw = "42 52 4E 43 02 13 1C 00 03 01 A5 5A EB A9 C6 8A FC 94 67 3B D4 4D C0 D7 84 96 93 09 81 33 CE 6E 39 12 6D 3E 62 63 64 CD 92";
  let hex_str_fw = "42 52 4E 43 02 13 36 00 03 01 A5 5A C5 A9 30 9B 64 C0 F4 00 CF 0C D4 6C 56 6A F3 71 8B F4 3A 0E 5A CD 62 23 5E EF 5F A4 7E EC DF 26 32 AF F1 6F B0 C5 51 B9 B3 F3 59 93 C9 E7 BC 56 43 74 56 60 02 DC 85
42 52 4E 43 02 13 34 00 03 01 A5 5A C3 A9 3D 9B 64 E2 D4 00 F7 0C DC D3 7A B9 D9 7B AA C3 35 03 6E 8E DF 60 0B D7 E1 41 43 F1 FF 66 C2 2A B0 82 D7 23 A9 80 1C D5 85 10 95 98 B0 9F 4A 14 CF C8 25
42 52 4E 43 02 13 36 00 03 01 A5 5A C5 A9 23 9B 64 B7 D1 00 CF 0C D4 6C 56 52 F3 71 8B F4 3A 0E 5A CD C2 23 5E EF DF EB 7E EC DF 26 42 AF F1 63 B0 57 E8 0E F7 3D C9 F0 25 1A 9C F0 F6 00 D4 AA 70 78 D9";
  // let hex_str_fw = "42 52 4E 43 02 13 32 00 03 01 A5 5A C1 A9 8E 8A E3 EA 67 13 D6 25 1C 6A 4E 8A CD 4E A8 CE 35 CB 1E D8 CA 60 CB D0 C2 C6 DA D0 9E 66 BC 20 12 A2 5B 84 F2 15 AA C6 D6 4D C2 86 43 75 F5 C6 38 42 52 4E 43 02 13 32 00 03 01 A5 5A C1 A9 8F 8A D7 EA 67 13 D6 25 1C 6A 4E 8A CD 4E A8 CE 35 CB 1E D8 CA 60 CB D0 C2 C6 DA D0 9E 66 BC 73 8D 28 28 A6 C5 1E D7 CC B6 F5 39 53 CC 4F 72 F7 68";
  // parse hex_str_fw to hex_str like "42524E4302131F000301A55AEC..."

  #[allow(unused_variables)]
// let mut hex_str_fw = hex_str_fw.replace(" ", "").replace("\n", "");
  // hex_str_fw = "42524e43021333000301002af2a96c88560adc0bd90d19834c8f64be2bcec0fce8ccc170d6fdfd5a7ef79c20c1963ef4d49e8b7178a032acc5dd7ba6ee28d959".to_string();
  // hex_str_fw = "42524e4302133a000301005ac9a9e38a8cd16513d62df545f58cc7e8a4f43a0e5acdf2235eef5f6e7decdf26cad0f1c0fc48273894df14576e29c344dbb3b49c8f8789baed0d84".to_string();
  // hex_str_fw = "42524e4302131d00030100bae0abfaf7640e7ce3d02d1c6a9344ad8ec45aee316ecb8c0a00feffa3481d".to_string();
  // hex_str_fw = "42524e43021333000301002af2a91194560a810b8f0dea824c8f66bed9cec0fce8ccc170a9e1fd5a8ef7d4217f967a0bca12be9c0a01e74b7637ac26a9b17b01".to_string();
  let payload = hex::decode(hex_str_fw)?;
  handle_receive_data(&payload);
  return Ok(());

  #[allow(unreachable_code)]
  let file_path = format!("examples/encrypt/tml_mock_data.dat");
  let f = File::open(file_path).unwrap();

  let result: Result<(), anyhow::Error> = async {
    let mut reader = BufReader::new(f);
    let mut buffer = String::new();
    let mut line_index = 1;
    while reader.read_line(&mut buffer).unwrap() > 0 {
      let hex_str = buffer.trim();
      // let hex_str = "42524E43020c19000301005AE6B103EF6C0D340A5B56AFC330B30D224FA497845294FE7887F9";
      if hex_str.len() % 2 != 0 {
        error!(
          "Error: Odd number of digits in line {}, buf: {:}",
          line_index, hex_str
        );
        buffer.clear();
        break;
      }
      let data: Vec<u8> = hex::decode(hex_str)?;
      handle_receive_data(&data);
      trace!(
        "line: {}, data: {:02x?}, len: {}",
        line_index,
        data,
        data.len()
      );
      line_index += 1;
      buffer.clear();
      // break;
    }
    Ok(())
  }
  .await;

  if let Err(e) = result {
    error!("Error: {}", e);
  }

  sleep(Duration::from_secs(1));

  Ok(())
}

extern "C" fn on_gait_analysis_result(
  timestamp: u32,
  sport_runtime: u32,
  sport_id: u32,
  foot: u8,
  pattern: u8,
  gait_duration: u32,
  step_load: f32,
) {
  info!(
    "on_gait_analysis_result, timestamp: {}, sport_runtime: {}, sport_id: {}, foot: {}, pattern: {}, gait_duration: {}, step_load: {}",
    timestamp, sport_runtime, sport_id, foot, pattern, gait_duration, step_load
  );
}

extern "C" fn on_abnormal_event(timestamp: u32, sport_runtime: u32, sport_id: u32, event_type: u8) {
  info!(
    "on_abnormal_event, timestamp: {}, sport_runtime: {}, sport_id: {}, event_type: {}",
    timestamp, sport_runtime, sport_id, event_type
  );
}
