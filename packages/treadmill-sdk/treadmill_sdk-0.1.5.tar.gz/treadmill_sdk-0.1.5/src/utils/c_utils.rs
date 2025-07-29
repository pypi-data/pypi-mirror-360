use std::{ffi::*, ptr};

/// A trait to copy the contents of a Vec<u8> to a raw buffer.
pub trait VecCopyToBuffer {
  /// Copies the contents of the Vec to the provided buffer.
  ///
  /// # Safety
  ///
  /// This function is unsafe because it dereferences a raw pointer.
  /// The caller must ensure that the buffer is valid for writes and
  /// has enough space to hold the contents of the Vec.
  unsafe fn copy_to_buffer(self, buffer: *mut u8) -> i32;
}

impl VecCopyToBuffer for Vec<u8> {
  unsafe fn copy_to_buffer(self, buffer: *mut u8) -> i32 {
    let len = self.len();
    unsafe {
      ptr::copy_nonoverlapping(self.as_ptr(), buffer, len);
    }
    len as i32
  }
}

pub trait CStringExt {
  fn to_c_string(&self) -> CString;
  fn to_cbytes(&self) -> *const c_char;
}

impl CStringExt for String {
  fn to_c_string(&self) -> CString {
    CString::new(self.as_str()).unwrap()
  }
  fn to_cbytes(&self) -> *const c_char {
    let cstring = self.to_c_string();
    cstring.into_raw()
  }
}
