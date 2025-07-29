use treadmill_sdk::encrypt::aes_cbc::{decrypt, encrypt};
use treadmill_sdk::utils::logging_desktop::init_logging;

treadmill_sdk::cfg_import_logging!();

/// cargo run --example enc-aes-cbc
fn main() {
  // 初始化日志系统，设置为Info级别
  init_logging(log::Level::Info);

  let key = "BRNC-Treadmill-1";
  let plaintext = b"Hello, Device!";

  // 加密并记录结果
  let cipher_message = match encrypt(key, plaintext) {
    Ok(cipher_message) => {
      info!("Encrypted message: {:?}", hex::encode(&cipher_message));
      cipher_message
    }
    Err(e) => {
      error!("Encryption failed: {}", e);
      return; // 如果加密失败，退出main
    }
  };

  // 解密并检查是否还原明文
  let decrypted = match decrypt(key, &cipher_message) {
    Ok(decrypted) => {
      info!("Decrypted: {}", String::from_utf8_lossy(&decrypted));
      decrypted
    }
    Err(e) => {
      error!("Decryption failed: {}", e);
      return; // 如果解密失败，退出main
    }
  };

  if decrypted == plaintext {
    info!("Decryption successful: plaintext restored correctly");
  } else {
    error!("Decryption failed: plaintext not restored");
  }
}
