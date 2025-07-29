use std::{ffi::*, ptr};

use super::aes_gcm;
#[allow(unused_imports)]
use crate::utils::logging::LogLevel;
#[allow(unused_imports)]
use crate::utils::logging_desktop as logging;

crate::cfg_import_logging!();

/// AES-128 加密密钥（16 字节长度）
const KEY: &str = "BRNC-Treadmill-1";

/// 初始化日志记录功能
///
/// # 参数
/// - `level`: 日志级别
#[no_mangle]
pub extern "C" fn initialize_logging(level: LogLevel) {
  logging::initialize_logging(level);
}

/// AES-GCM 加密函数
///
/// # 参数
/// - `plaintext`: 指向待加密数据的指针
/// - `len`: 数据长度（字节）
/// - `user_id`: 用户 ID（C 字符串）
/// - `sn_code`: 设备序列号（C 字符串）
/// - `out_len`: 加密后的数据长度（字节）
///
/// # 返回值
/// - 成功: 返回加密后的密文
/// - 失败: 返回 `NULL`
///
/// # 注意
/// - 传入的指针必须有效，否则返回 `NULL`
/// - C 代码端需要在使用完返回的字符串后调用 `free_encrypted_or_decrypted` 释放内存
///
/// # Example
/// ```c
/// const char* plaintext = "Hello, Device!";
/// const char* user_id = "550e8400-e29b-41d4-a716-446655440000";
/// const char* sn_code = "SN123456";
/// size_t out_len = 0;
/// uint8_t* encrypted = tml_encrypt((const uint8_t*)plaintext, strlen(plaintext), user_id, sn_code, &out_len);
/// if (encrypted != NULL) {
///     free_encrypted_or_decrypted(encrypted);
/// }
/// ```
#[no_mangle]
pub extern "C" fn tml_encrypt(
  plaintext: *const u8,
  len: usize,
  user_id: *const c_char,
  sn_code: *const c_char,
  out_len: *mut usize,
) -> *mut u8 {
  // 确保所有指针有效
  if plaintext.is_null() || user_id.is_null() || sn_code.is_null() {
    error!("Invalid parameters");
    return ptr::null_mut();
  }

  let plaintext = unsafe { std::slice::from_raw_parts(plaintext, len) };
  let user_id = unsafe { CStr::from_ptr(user_id).to_str().unwrap() };
  let sn_code = unsafe { CStr::from_ptr(sn_code).to_str().unwrap() };

  // 执行 AES-GCM 加密
  match aes_gcm::encrypt(KEY, plaintext, user_id, sn_code) {
    Ok(encrypted) => {
      let encrypted_len = encrypted.len();
      let ptr = Box::into_raw(encrypted.into_boxed_slice()) as *mut u8; // 转换为 *mut u8
      unsafe {
        *out_len = encrypted_len;
      }
      ptr
    }
    Err(err) => {
      error!("Encrypt failed: {:?}", err);
      ptr::null_mut() // 加密失败返回 NULL
    }
  }
}

/// AES-GCM 解密函数
///
/// # 参数
/// - `ciphertext`: 指向待解密数据的指针
/// - `len`: 数据长度（字节）
/// - `user_id`: 用户 ID（C 字符串）
/// - `sn_code`: 设备序列号（C 字符串）
/// - `out_len`: 解密后的数据长度（字节）
///
/// # 返回值
/// - 成功: 返回解密后的`uint8_t` 指针
/// - 失败: 返回 `NULL`
///
/// # 注意
/// - 传入的指针必须有效，否则返回 `NULL`
/// - C 代码端需要在使用完返回的字符串后调用 `free_encrypted_or_decrypted` 释放内存
///
/// # Example
/// ```c
/// const char* ciphertext = "encrypted data";
/// const char* user_id = "550e8400-e29b-41d4-a716-446655440000";
/// const char* sn_code = "SN123456";
/// size_t out_len = 0;
/// uint8_t* decrypted = tml_decrypt((const uint8_t*)ciphertext, strlen(ciphertext), user_id, sn_code, &out_len);
/// if (decrypted != null) {
///     free_encrypted_or_decrypted(decrypted);
/// }
/// ```
#[no_mangle]
pub extern "C" fn tml_decrypt(
  ciphertext: *const u8,
  len: usize,
  user_id: *const c_char,
  sn_code: *const c_char,
  out_len: *mut usize,
) -> *mut u8 {
  // 确保所有指针有效
  if ciphertext.is_null() || user_id.is_null() || sn_code.is_null() {
    error!("Invalid parameters");
    return ptr::null_mut();
  }

  let ciphertext = unsafe { std::slice::from_raw_parts(ciphertext, len) };
  let user_id = unsafe { CStr::from_ptr(user_id).to_str().unwrap() };
  let sn_code = unsafe { CStr::from_ptr(sn_code).to_str().unwrap() };

  // 执行 AES-GCM 解密
  match aes_gcm::decrypt(KEY, ciphertext, user_id, sn_code) {
    Ok(decrypted) => {
      let decrypted_len = decrypted.len();
      let ptr = Box::into_raw(decrypted.into_boxed_slice()) as *mut u8; // 转换为 *mut u8
      unsafe {
        *out_len = decrypted_len;
      }
      ptr
    }
    Err(err) => {
      error!("Encrypt failed: {:?}", err);
      ptr::null_mut() // 加密失败返回 NULL
    }
  }
}

/// 释放由 `encrypt` 或 `decrypt` 生成的数据
///
/// # 参数
/// - `ptr`: 由 `encrypt` 或 `decrypt` 返回的 `uint8_t` 指针
/// - `len`: 数据长度，与 `out_len` 返回的值一致
///
/// # 注意
/// - 仅应释放由 `encrypt` 或 `decrypt` 分配的内存
/// - 传入 `NULL` 安全无副作用
#[no_mangle]
pub extern "C" fn free_encrypted_or_decrypted(ptr: *mut u8, len: usize) {
  if !ptr.is_null() && len > 0 {
    unsafe {
      let slice = std::slice::from_raw_parts_mut(ptr, len);
      let _ = Box::from_raw(slice); // 转换为 Box<[u8]> 并释放
    }
  }
}
