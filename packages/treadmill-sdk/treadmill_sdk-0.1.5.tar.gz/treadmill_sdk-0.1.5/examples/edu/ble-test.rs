use async_std::task::sleep;
use treadmill_sdk::ble::constants::*;
use treadmill_sdk::ble::core::*;
use treadmill_sdk::ble::lib::*;
use treadmill_sdk::ble::structs::*;
#[allow(unused_imports)]
use treadmill_sdk::generated::edu_proto::*;
use treadmill_sdk::proto::edu::msg_builder::edu_msg_builder;
use treadmill_sdk::proto::enums::MsgType;
use treadmill_sdk::proto::msg_parser::Parser;
use treadmill_sdk::utils::logging_desktop::init_logging;
use btleplug::api::CentralState;
use std::error::Error;
use std::sync::Arc;
use std::sync::Mutex;
use std::time::Duration;
use tokio_stream::StreamExt;

// cargo run --no-default-features --example edu-ble-test --features="edu, examples, ble"

treadmill_sdk::cfg_import_logging!();

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
  init_logging(log::Level::Debug);

  initialize_central_adapter().await?;
  let is_ble_scanning = is_scanning();
  info!("is_ble_scanning, {:?}", is_ble_scanning);
  if is_ble_scanning {
    return Err("already scanning".into());
  }
  set_adapter_state_callback(Box::new(adapter_state_handler));
  set_device_discovered_callback(Box::new(scan_result_handler)); // 设备没有广播数据，所以使用设备发现回调
                                                                 // set_scan_result_callback(Box::new(scan_result_handler));
  set_battery_level_callback(Box::new(battery_level_handler));

  let parser = Parser::new("edu-ble".into(), MsgType::Edu);
  let mut stream = parser.message_stream();
  tokio::spawn(async move {
    debug!("Starting read");
    while let Some(result) = stream.next().await {
      match result {
        Ok((device_id, message)) => {
          trace!(
            "Received message, device_id: {:?}, message: {:?}",
            device_id,
            message
          );
        }
        Err(e) => {
          error!("Error receiving message: {:?}", e);
        }
      }
    }
    debug!("Finished read");
  });

  let parser_arc = Arc::new(Mutex::new(parser));
  set_received_data_callback(Box::new(move |_id: String, data: Vec<u8>| {
    trace!("id: {}, received_data: {:02x?}", _id, data);
    parser_arc.lock().unwrap().receive_data(&data);
  }));

  info!("prepare scan...");
  start_scan_with_uuids(vec![EDU_SERVICE_UUID])?;
  sleep(Duration::from_secs(50)).await;
  Ok(())
}

fn adapter_state_handler(state: CentralState) {
  info!("adapter state: {:?}", state);
}

fn battery_level_handler(id: String, battery_level: u8) {
  info!("id: {}, battery_level: {}", id, battery_level);
}

fn scan_result_handler(result: ScanResult) {
  info!("on_device_discovered: {:?}", result);
  // Zephyr [EMGPLUS-769C6]
  if result.name.contains("EMGPLUS-769C6") {
    tokio::spawn(async {
      info!("stop_scan...");
      let _ = stop_scan();
      info!("stop_scan done");
      let id = result.id;
      connect_ble(&id).await;
      info!("connect_ble done");

      let (_, cmd) = edu_msg_builder::get_device_info();
      ble_write_value(&id, &cmd, true).await;

      let (_, cmd) = edu_msg_builder::get_sensor_cfg();
      ble_write_value(&id, &cmd, true).await;
    });
  }
}
