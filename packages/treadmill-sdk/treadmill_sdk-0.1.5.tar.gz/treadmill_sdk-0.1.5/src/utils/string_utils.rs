// use byteorder::{BigEndian, ByteOrder};
// use std::any::type_name;

#[allow(dead_code)]
pub(crate) fn pad_or_truncate(mut serial: String, length: usize) -> String {
  if serial.len() > length {
    serial.truncate(length);
  } else {
    while serial.len() < length {
      serial.push('0');
    }
  }
  serial
}

pub fn to_big_endian_u16_ascii_string(value: u16) -> String {
  value
    .to_be_bytes()
    .iter()
    .map(|&b| b as char)
    .collect::<String>()
}

pub fn u16_array_to_be_ascii_string(values: &[u16]) -> String {
  let mut result = values
    .iter()
    .map(|&value| to_big_endian_u16_ascii_string(value))
    .collect::<String>();

  // 去除末尾的所有 '\0'
  result = result.trim_end_matches('\0').to_string();
  result
}
