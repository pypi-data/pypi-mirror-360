use aes::Aes128;
use cbc::cipher::KeyIvInit;
use cipher::generic_array::GenericArray;
use cipher::BlockEncryptMut;
use ring::hkdf;
use ring::hmac;
use ring::rand::{SecureRandom, SystemRandom};
use std::io::{Error, ErrorKind};

use super::aes_gcm::HkdfKeyLength; // 引入GenericArray来构造块

crate::cfg_import_logging!();

const KEY_BYTE_SIZE: usize = 16;
const ENC_KEY_INFO: &[u8] = b"enc_key_info";
const AUTH_KEY_INFO: &[u8] = b"auth_key_info";

type Aes128CbcEncrypt = cbc::Encryptor<Aes128>;

/// AES-128-CBC加密（带PKCS7填充）
pub fn aes_cbc_encrypt(key: &[u8], iv: &[u8], plaintext: &[u8]) -> Result<Vec<u8>, Error> {
  let mut cipher = Aes128CbcEncrypt::new_from_slices(key, iv)
    .map_err(|_| Error::new(ErrorKind::InvalidInput, "Invalid key or IV"))?;

  let block_size = 16;
  let padded_len = ((plaintext.len() + block_size - 1) / block_size) * block_size;
  let mut padded = vec![0u8; padded_len];
  padded[..plaintext.len()].copy_from_slice(plaintext);

  // 手动PKCS7填充
  let padding_len = padded_len - plaintext.len();
  for i in plaintext.len()..padded_len {
    padded[i] = padding_len as u8;
  }

  let mut result = Vec::with_capacity(padded_len);
  let mut previous_block = iv.to_vec();

  for chunk in padded.chunks_exact(block_size) {
    // 使用GenericArray构造块
    let mut block = GenericArray::clone_from_slice(chunk);
    // CBC模式：当前块与前一密文XOR
    for (a, b) in block.iter_mut().zip(previous_block.iter()) {
      *a ^= *b;
    }
    // 加密当前块
    cipher.encrypt_block_mut(&mut block);
    result.extend_from_slice(block.as_slice());
    previous_block = block.as_slice().to_vec();
  }

  Ok(result)
}

/// AES-128-CBC加密与HMAC-SHA256签名
pub fn encrypt(key: &str, plaintext: &[u8]) -> Result<Vec<u8>, Error> {
  let rng = SystemRandom::new();
  let key_bytes = key.as_bytes();

  if key_bytes.len() != KEY_BYTE_SIZE {
    return Err(Error::new(
      ErrorKind::InvalidInput,
      "Key length size illegal",
    ));
  }

  let mut iv = [0u8; 16];
  rng
    .fill(&mut iv)
    .map_err(|_| Error::new(ErrorKind::Other, "Failed to generate IV"))?;

  let hkdf_key = hkdf::Salt::new(hkdf::HKDF_SHA256, &[]);
  let prk = hkdf_key.extract(key_bytes);

  // 派生enc_key_bytes，确保长度为16字节
  let mut enc_key_bytes = vec![0u8; 16];
  let enc_okm = prk
    .expand(&[ENC_KEY_INFO], HkdfKeyLength(16)) // 显式指定16字节
    .map_err(|_| Error::new(ErrorKind::Other, "HKDF enc_key derivation failed"))?;
  info!("enc_key_bytes before fill: {:?}", enc_key_bytes);
  enc_okm
    .fill(&mut enc_key_bytes)
    .map_err(|_| Error::new(ErrorKind::Other, "HKDF enc_key fill failed"))?;
  info!("enc_key_bytes after fill: {:?}", enc_key_bytes);

  // 派生auth_key_bytes，确保长度为32字节
  let mut auth_key_bytes = vec![0u8; 32];
  let auth_okm = prk
    .expand(&[AUTH_KEY_INFO], HkdfKeyLength(32))
    .map_err(|_| Error::new(ErrorKind::Other, "HKDF auth_key derivation failed"))?;
  auth_okm
    .fill(&mut auth_key_bytes)
    .map_err(|_| Error::new(ErrorKind::Other, "HKDF auth_key fill failed"))?;

  let cipher_text = aes_cbc_encrypt(&enc_key_bytes, &iv, plaintext)?;

  let signing_key = hmac::Key::new(hmac::HMAC_SHA256, &auth_key_bytes);
  let mut hmac_ctx = hmac::Context::with_key(&signing_key);
  hmac_ctx.update(&iv);
  hmac_ctx.update(&cipher_text);
  let mac = hmac_ctx.sign();

  let mut result = Vec::new();
  result.push(iv.len() as u8);
  result.extend_from_slice(&iv);
  result.push(mac.as_ref().len() as u8);
  result.extend_from_slice(mac.as_ref());
  result.extend_from_slice(&cipher_text);

  Ok(result)
}

// TODO: decrypt还原，由于使用了GCM模式，先忽略CBC模式的问题
// 解密函数（验证HMAC并解密）
pub fn decrypt(key: &str, cipher_message: &[u8]) -> Result<Vec<u8>, Error> {
  let key_bytes = key.as_bytes();

  if key_bytes.len() != KEY_BYTE_SIZE {
    return Err(Error::new(
      ErrorKind::InvalidInput,
      "Key length size illegal",
    ));
  }

  // 解析cipher_message: IV长度(1字节) || IV || MAC长度(1字节) || MAC || 密文
  if cipher_message.len() < 2 + 16 + 32 {
    // 最短长度：IV长度 + IV + MAC长度 + MAC
    return Err(Error::new(
      ErrorKind::InvalidInput,
      "Cipher message too short",
    ));
  }

  let iv_len = cipher_message[0] as usize;
  if iv_len != 16 {
    return Err(Error::new(ErrorKind::InvalidInput, "Invalid IV length"));
  }
  let iv = &cipher_message[1..1 + iv_len];
  let mac_len_offset = 1 + iv_len;
  let mac_len = cipher_message[mac_len_offset] as usize;
  let mac_offset = mac_len_offset + 1;
  let mac = &cipher_message[mac_offset..mac_offset + mac_len];
  let cipher_text = &cipher_message[mac_offset + mac_len..];

  let hkdf_key = hkdf::Salt::new(hkdf::HKDF_SHA256, &[]);
  let prk = hkdf_key.extract(key_bytes);

  let mut enc_key_bytes = vec![0u8; 16];
  let enc_okm = prk
    .expand(&[ENC_KEY_INFO], HkdfKeyLength(16))
    .map_err(|_| Error::new(ErrorKind::Other, "HKDF enc_key derivation failed"))?;
  enc_okm
    .fill(&mut enc_key_bytes)
    .map_err(|_| Error::new(ErrorKind::Other, "HKDF enc_key fill failed"))?;

  // 派生auth_key_bytes，确保长度为32字节
  let mut auth_key_bytes = vec![0u8; 32];
  let auth_okm = prk
    .expand(&[AUTH_KEY_INFO], HkdfKeyLength(32))
    .map_err(|_| Error::new(ErrorKind::Other, "HKDF auth_key derivation failed"))?;
  auth_okm
    .fill(&mut auth_key_bytes)
    .map_err(|_| Error::new(ErrorKind::Other, "HKDF auth_key fill failed"))?;

  // 验证HMAC
  let signing_key = hmac::Key::new(hmac::HMAC_SHA256, &auth_key_bytes);
  let mut hmac_ctx = hmac::Context::with_key(&signing_key);
  hmac_ctx.update(iv);
  hmac_ctx.update(cipher_text);
  let computed_mac = hmac_ctx.sign();
  if computed_mac.as_ref() != mac {
    return Err(Error::new(ErrorKind::Other, "HMAC verification failed"));
  }

  // 解密
  aes_cbc_decrypt(&enc_key_bytes, iv, cipher_text)
}

/// AES-128-CBC解密（带PKCS7填充移除）
pub fn aes_cbc_decrypt(key: &[u8], iv: &[u8], ciphertext: &[u8]) -> Result<Vec<u8>, Error> {
  let mut cipher = Aes128CbcEncrypt::new_from_slices(key, iv)
    .map_err(|_| Error::new(ErrorKind::InvalidInput, "Invalid key or IV"))?;

  let block_size = 16;
  if ciphertext.len() % block_size != 0 {
    return Err(Error::new(
      ErrorKind::InvalidInput,
      "Ciphertext length invalid",
    ));
  }

  let mut result = Vec::with_capacity(ciphertext.len());
  let mut previous_block = iv.to_vec();

  for chunk in ciphertext.chunks_exact(block_size) {
    // 使用GenericArray构造块
    let mut block = GenericArray::clone_from_slice(chunk);
    // 解密当前块
    cipher.encrypt_block_mut(&mut block);
    // CBC模式：当前块与前一密文XOR
    for (a, b) in block.iter_mut().zip(previous_block.iter()) {
      *a ^= *b;
    }
    result.extend_from_slice(block.as_slice());
    previous_block = chunk.to_vec();
  }

  // 移除PKCS7填充
  let padding_len = *result
    .last()
    .ok_or_else(|| Error::new(ErrorKind::InvalidData, "Invalid padding"))?
    as usize;
  info!("padding_len: {:?}", padding_len);
  info!("result: {:?}", result);
  if padding_len == 0 || padding_len > block_size {
    return Err(Error::new(ErrorKind::InvalidData, "Invalid padding length"));
  }
  let plaintext_len = result.len() - padding_len;
  result.truncate(plaintext_len);

  Ok(result)
}
