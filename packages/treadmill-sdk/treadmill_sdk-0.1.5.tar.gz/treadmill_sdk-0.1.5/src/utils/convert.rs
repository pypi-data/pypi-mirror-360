use byteorder::{BigEndian, ByteOrder};
use std::any::type_name;

pub fn bytes_to_u16_big_endian(bytes: &[u8], len: usize) -> Vec<u16> {
  let mut result = Vec::with_capacity(bytes.len() / 2);
  for chunk in bytes.chunks(2) {
    let value = if chunk.len() == 2 {
      BigEndian::read_u16(chunk)
    } else {
      BigEndian::read_u16(&[chunk[0], 0])
    };
    result.push(value);
  }
  while result.len() < len {
    result.push(0);
  }
  result
}

pub fn type_of<T>(_: &T) -> &'static str {
  type_name::<T>()
}

pub fn to_vec_u16(slice: &[u16]) -> Vec<u16> {
  slice.to_vec()
}

pub fn to_vec_i16(slice: &[u16]) -> Vec<i16> {
  slice.iter().map(|&v| v as i16).collect()
}
