// use ring::aead::NONCE_LEN;
// use treadmill_sdk::encrypt::{self, aes_gcm::*};
use treadmill_sdk::encrypt::aes_gcm::*;
use treadmill_sdk::generated::treadmill_proto::SensorApp;
use treadmill_sdk::proto::enums::decode;
use treadmill_sdk::utils::logging_desktop::init_logging;

treadmill_sdk::cfg_import_logging!();

/// cargo run --example enc-aes-gcm
fn main() {
  init_logging(log::Level::Info);

  let plaintext = b"Hello, Device!";
  // let plaintext = [
  //   0x48, 0x65, 0x6c, 0x6c, 0x6f, 0x2c, 0x20, 0x44, 0x65, 0x76, 0x69, 0x63, 0x65, 0x21,
  // ];
  info!(
    "Plaintext: len: {}, hex: {}",
    plaintext.len(),
    hex::encode(plaintext)
  );
  test_default(plaintext);
  // return;

  // let user_id: &str = "550e8400-e29b-41d4-a716-446655440000";
  // let sn_code = "SN123456";
  // test_encrypt_c(plaintext, user_id, sn_code);
  return;

  // const KEY: &str = "BRNC-Treadmill-1"; // AES-128需要16字节密钥
  // info!("key len: {}", KEY.len());
  // let encrypted = encrypt(KEY, plaintext, &user_id, sn_code).unwrap();
  // info!(
  //   "Encrypted len: {}, hex: {}",
  //   encrypted.len(),
  //   hex::encode(&encrypted)
  // );

  // let decrypted = decrypt(KEY, &encrypted, user_id, sn_code).unwrap();
  // info!(
  //   "Decrypted: len: {}, hex: {}",
  //   decrypted.len(),
  //   hex::encode(&decrypted)
  // );

  // if decrypted == plaintext {
  //   info!("Decryption successful: plaintext restored correctly");
  // } else {
  //   error!("Decryption failed: plaintext not restored");
  // }
}

fn test_default(plaintext: &[u8]) {
  // let encrypted = default_encrypt(plaintext).unwrap();
  // info!(
  //   "Encrypted len: {}, hex: {}",
  //   encrypted.len(),
  //   hex::encode(&encrypted)
  // );
  let encrypt = "2af5a90d0f752e62d32833f4528ebbf140a5ce35fca57fcb6c5b124a5d61f7cd218197a7de23636864bc5017720c9914b3fe85414f";
  let encrypted = hex::decode(encrypt).unwrap();
  info!(
    "Encrypted len: {}, hex: {}",
    encrypted.len(),
    hex::encode(&encrypted)
  );

  let data = encrypted;
  // let data = encrypted[NONCE_LEN..].to_vec(); // 由于SN和UserId是固定的，所以nonce是一样的，remove nonce
  let decrypted = default_decrypt(&data).unwrap();
  info!(
    "Decrypted: len: {}, hex: {}",
    decrypted.len(),
    hex::encode(&decrypted)
  );
  let resp = decode::<SensorApp>(&decrypted).unwrap();
  info!(
    "SensorApp: {:?}",
    serde_json::to_string(&resp).unwrap_or("".to_string())
  );
  if decrypted == plaintext {
    info!("Decryption successful: plaintext restored correctly");
    info!("Decrypted: {}", String::from_utf8_lossy(&decrypted));
  } else {
    error!("Decryption failed: plaintext not restored");
  }
}

/*
// use treadmill_sdk::encrypt::encrypt_c;
// use treadmill_sdk::utils::c_utils::CStringExt;
fn test_encrypt_c(plaintext: &[u8], user_id: &str, sn_code: &str) {
  let mut enc_out_len: usize = 0;
  let encrypted_ptr = encrypt_c::tml_encrypt(
    plaintext.as_ptr(),
    plaintext.len(),
    user_id.to_string().to_cbytes(),
    sn_code.to_string().to_cbytes(),
    &mut enc_out_len,
  );
  if !encrypted_ptr.is_null() {
    info!(
      "Encrypted C, len: {}, hex: {}",
      enc_out_len,
      hex::encode(unsafe { std::slice::from_raw_parts(encrypted_ptr, enc_out_len) })
    );

    let mut dec_out_len: usize = 0;
    let decrypted_ptr = encrypt_c::tml_decrypt(
      encrypted_ptr,
      enc_out_len,
      user_id.to_string().to_cbytes(),
      sn_code.to_string().to_cbytes(),
      &mut dec_out_len,
    );
    assert!(!decrypted_ptr.is_null());
    info!(
      "Decrypted C, len: {}, hex: {}",
      dec_out_len,
      hex::encode(unsafe { std::slice::from_raw_parts(decrypted_ptr, dec_out_len) })
    );
    encrypt_c::free_encrypted_or_decrypted(encrypted_ptr, enc_out_len);
    encrypt_c::free_encrypted_or_decrypted(decrypted_ptr, dec_out_len);
  } else {
    error!("Encrypt C failed");
  }
}
*/
