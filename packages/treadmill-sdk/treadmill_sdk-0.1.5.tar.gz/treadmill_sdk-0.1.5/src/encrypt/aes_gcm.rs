use ring::aead::{self, Aad, LessSafeKey, Nonce, UnboundKey, NONCE_LEN};
use ring::hkdf;
use std::io::{Error, ErrorKind};
use uuid::Uuid; // 用于解析UUID

crate::cfg_import_logging!();

// 自定义KeyType实现，用于指定HKDF输出长度
pub struct HkdfKeyLength(pub usize);

impl hkdf::KeyType for HkdfKeyLength {
  fn len(&self) -> usize {
    self.0
  }
}

const KEY: &str = "BRNC-Treadmill-1"; // AES-128需要16字节密钥
/// default nonce for following user_id and sn_code
/// let user_id: &str = "550e8400-e29b-41d4-a716-446655440000";
/// let sn_code = "SN123456";
const NONCE_BYTES: [u8; NONCE_LEN] = [
  0x9d, 0x3f, 0x82, 0x68, 0x3c, 0x01, 0x66, 0x12, 0xb9, 0x19, 0xb4, 0x41,
];

const KEY_BYTE_SIZE: usize = 16; // AES-128需要16字节密钥
const ENC_KEY_INFO: &[u8] = b"BRNROBOTCS.Treadmill.EncKey.v1"; // 用于HKDF派生密钥的info
const NONCE_INFO: &[u8] = b"BRNROBOTCS.Treadmill.Nonce.v1"; // 用于HKDF派生Nonce的info

pub fn default_encrypt(plain_bytes: &[u8]) -> Result<Vec<u8>, Error> {
  encrypt_with_key_nonce(KEY, NONCE_BYTES, plain_bytes)
}

pub fn default_decrypt(cipher_bytes: &[u8]) -> Result<Vec<u8>, Error> {
  decrypt_with_key_nonce(KEY, NONCE_BYTES, cipher_bytes)
}

/// 从userid和SN_code派生Nonce
pub fn derive_nonce(user_id: &str, sn_code: &str) -> Result<[u8; NONCE_LEN], Error> {
  // 解析userid为UUID并获取其字节
  let uuid = Uuid::parse_str(user_id)
    .map_err(|_| Error::new(ErrorKind::InvalidInput, "Invalid UUID format for user_id"))?;
  let uuid_bytes = uuid.as_bytes(); // 16字节

  // 获取SN_code的字节
  let sn_code_bytes = sn_code.as_bytes();

  // 使用HKDF派生Nonce
  let salt: &[u8] = &[];
  let hkdf_key = hkdf::Salt::new(hkdf::HKDF_SHA256, salt);

  // 组合uuid_bytes和sn_code_bytes作为输入
  let mut input = Vec::new();
  input.extend_from_slice(uuid_bytes);
  input.extend_from_slice(sn_code_bytes);
  let prk = hkdf_key.extract(&input);

  // 派生12字节Nonce
  let mut nonce_bytes = [0u8; NONCE_LEN];
  let nonce_okm = prk
    .expand(&[NONCE_INFO], HkdfKeyLength(NONCE_LEN))
    .map_err(|_| Error::other("HKDF nonce derivation failed"))?;
  nonce_okm
    .fill(&mut nonce_bytes)
    .map_err(|_| Error::other("HKDF nonce fill failed"))?;

  Ok(nonce_bytes)
}

pub fn encrypt_with_key_nonce(
  key: &str,
  nonce_bytes: [u8; NONCE_LEN],
  plain_bytes: &[u8],
) -> Result<Vec<u8>, Error> {
  let key_bytes = key.as_bytes();

  // 检查密钥长度
  if key_bytes.len() != KEY_BYTE_SIZE {
    return Err(Error::new(
      ErrorKind::InvalidInput,
      "Key length size illegal",
    ));
  }

  // 使用HKDF从key_bytes派生加密密钥（encKey）
  let hkdf_key = hkdf::Salt::new(hkdf::HKDF_SHA256, &[]);
  let prk = hkdf_key.extract(key_bytes);

  // 派生enc_key_bytes，确保长度为16字节
  let mut enc_key_bytes = vec![0u8; 16];
  let enc_okm = prk
    .expand(&[ENC_KEY_INFO], HkdfKeyLength(16)) // 显式指定16字节
    .map_err(|_| Error::other("HKDF enc_key derivation failed"))?;
  // trace!("enc_key_bytes before fill: {:?}", enc_key_bytes);
  enc_okm
    .fill(&mut enc_key_bytes)
    .map_err(|_| Error::other("HKDF enc_key fill failed"))?;
  // trace!("enc_key_bytes after fill: {:?}", enc_key_bytes);

  // 创建AES-GCM密钥
  let unbound_key = UnboundKey::new(&aead::AES_128_GCM, &enc_key_bytes)
    .map_err(|_| Error::new(ErrorKind::InvalidInput, "Failed to create AES-GCM key"))?;
  let less_safe_key = LessSafeKey::new(unbound_key);

  let nonce = Nonce::assume_unique_for_key(nonce_bytes);

  // 加密数据
  let mut in_out = plain_bytes.to_vec();
  let tag = less_safe_key
    .seal_in_place_separate_tag(nonce, Aad::empty(), &mut in_out)
    .map_err(|_| Error::other("AES-GCM encryption failed"))?;

  // 组合Nonce、密文和认证标签
  let mut result = Vec::new();
  result.extend_from_slice(&nonce_bytes); // Nonce（12字节）
  result.extend_from_slice(&in_out); // 密文
  result.extend_from_slice(tag.as_ref()); // 认证标签（16字节）

  Ok(result)
}

/// AES-128-GCM加密，使用userid和SN_code派生Nonce
pub fn encrypt(
  key: &str,
  plain_bytes: &[u8],
  user_id: &str,
  sn_code: &str,
) -> Result<Vec<u8>, Error> {
  let nonce_bytes = derive_nonce(user_id, sn_code)?;
  // info!("nonce_bytes: {:02x?}", nonce_bytes);
  encrypt_with_key_nonce(key, nonce_bytes, plain_bytes)
}

/// 解密函数
pub fn decrypt(
  key: &str,
  cipher_bytes: &[u8],
  user_id: &str,
  sn_code: &str,
) -> Result<Vec<u8>, Error> {
  let nonce_bytes = derive_nonce(user_id, sn_code)?;
  decrypt_with_key_nonce(key, nonce_bytes, cipher_bytes)
}

pub fn decrypt_with_key_nonce(
  key: &str,
  nonce_bytes: [u8; NONCE_LEN],
  cipher_bytes: &[u8],
) -> Result<Vec<u8>, Error> {
  let key_bytes = key.as_bytes();

  if key_bytes.len() != KEY_BYTE_SIZE {
    return Err(Error::new(
      ErrorKind::InvalidInput,
      "Key length size illegal",
    ));
  }

  if cipher_bytes.len() <= aead::AES_128_GCM.tag_len() {
    return Err(Error::new(
      ErrorKind::InvalidInput,
      "cipher_bytes too short",
    ));
  }

  // 使用HKDF派生相同的加密密钥
  let hkdf_key = hkdf::Salt::new(hkdf::HKDF_SHA256, &[]);
  let prk = hkdf_key.extract(key_bytes);
  let mut enc_key_bytes = vec![0u8; 16];
  let enc_okm = prk
    .expand(&[ENC_KEY_INFO], HkdfKeyLength(16))
    .map_err(|_| Error::other("HKDF enc_key derivation failed"))?;
  enc_okm
    .fill(&mut enc_key_bytes)
    .map_err(|_| Error::other("HKDF enc_key fill failed"))?;

  let unbound_key = UnboundKey::new(&aead::AES_128_GCM, &enc_key_bytes)
    .map_err(|_| Error::new(ErrorKind::InvalidInput, "Failed to create AES-GCM key"))?;
  let less_safe_key = LessSafeKey::new(unbound_key);

  // 解析密文
  let mut in_out = cipher_bytes.to_vec();
  // let mut in_out = cipher_bytes[NONCE_LEN..].to_vec();

  // 解密并验证
  let nonce = Nonce::assume_unique_for_key(nonce_bytes);
  less_safe_key
    .open_in_place(nonce, Aad::empty(), &mut in_out)
    .map_err(|_| Error::other("AES-GCM decryption or verification failed"))?;

  // 获取真实明文长度
  let len = in_out.len() - aead::AES_128_GCM.tag_len();
  // info!("plain_bytes_len: {}", len);

  // 仅保留有效的明文部分
  in_out.truncate(len);

  Ok(in_out)
}
