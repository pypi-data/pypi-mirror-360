use chrono::{offset::LocalResult, Local, TimeZone};

pub fn calculate_millis(base_timestamp: u32, offset: u32) -> u64 {
  (base_timestamp + offset) as u64 * 1000
}

pub fn format_timestamp(secs: u64) -> String {
  match Local.timestamp_opt(secs.try_into().unwrap_or_default(), 0) {
    chrono::LocalResult::Single(t) => t.format("%Y-%m-%d %H:%M:%S").to_string(),
    _ => "Invalid Timestamp".to_string(),
  }
}

pub fn format_timestamp_millis(millis: u64) -> String {
  match Local.timestamp_millis_opt(millis.try_into().unwrap_or_default()) {
    LocalResult::Single(t) => t.format("%Y-%m-%d %H:%M:%S").to_string(),
    _ => "Invalid Timestamp".to_string(),
  }
}
