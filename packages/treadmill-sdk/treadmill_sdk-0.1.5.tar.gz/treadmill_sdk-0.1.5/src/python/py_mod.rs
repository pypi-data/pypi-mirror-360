use super::callback::*;
use crate::proto::enums::MsgType;
use crate::python::py_msg_parser::*;
use pyo3::prelude::*;
use pyo3::types::*;
use pyo3_stub_gen::derive::*;

crate::cfg_import_logging!();

// cfg_if::cfg_if! {
//   if #[cfg(feature = "edu")] {
//     use super::edu::py_mod_edu::*;
//     use super::edu::py_mod_armband::*;
//   }
// }

#[pymodule]
fn treadmill_sdk(m: &Bound<'_, PyModule>) -> PyResult<()> {
  pyo3_log::init();
  info!(
    "{} version: {}",
    env!("CARGO_PKG_NAME"),
    env!("CARGO_PKG_VERSION")
  );

  // enums
  m.add_class::<MsgType>()?;

  // structs
  m.add_class::<MessageParser>()?;
  m.add_class::<MessageStream>()?;

  // functions
  // m.add_function(wrap_pyfunction!(get_bytes, m)?)?;
  m.add_function(wrap_pyfunction!(get_sdk_version, m)?)?;
  m.add_function(wrap_pyfunction!(get_device_info, m)?)?;
  m.add_function(wrap_pyfunction!(did_receive_data, m)?)?;
  m.add_function(wrap_pyfunction!(encrypt, m)?)?;
  m.add_function(wrap_pyfunction!(decrypt, m)?)?;
  m.add_function(wrap_pyfunction!(wrap_message, m)?)?;

  m.add_function(wrap_pyfunction!(set_gait_data_callback, m)?)?;
  m.add_function(wrap_pyfunction!(set_abnormal_event_callback, m)?)?;
  m.add_function(wrap_pyfunction!(set_msg_resp_callback, m)?)?;

  // Register child module

  // cfg_if::cfg_if! {
  //   if #[cfg(feature = "ble")] {
  //     trace!("Registering child module BLE");
  //     let ble = PyModule::new(m.py(), "ble")?;
  //     register_child_module_ble(&ble)?;
  //     m.add_submodule(&ble)?;
  //   }
  // }

  // cfg_if::cfg_if! {
  //   if #[cfg(feature = "edu")] {
  //     trace!("Registering child module edu");
  //     let edu = PyModule::new(m.py(), "edu")?;
  //     register_child_module_edu(&edu)?;
  //     m.add_submodule(&edu)?;

  //     trace!("Registering child module armband");
  //     let armband = PyModule::new(m.py(), "armband")?;
  //     register_child_module_armband(&armband)?;
  //     m.add_submodule(&armband)?;
  //   }
  // }

  Ok(())
}

pyo3_stub_gen::define_stub_info_gatherer!(stub_info);

#[gen_stub_pyfunction]
#[pyfunction]
pub fn get_sdk_version() -> PyResult<String> {
  Ok(env!("CARGO_PKG_VERSION").to_string())
}

#[gen_stub_pyfunction]
#[pyfunction]
pub fn get_device_info() -> Vec<u8> {
  let (_, bytes) = tml_msg_builder::get_device_info();
  bytes
}

use crate::encrypt::aes_gcm;
use crate::proto::treadmill::msg_builder::tml_msg_builder;
// use crate::generated::treadmill_proto::GaitAnalysisResult;
// use prost::bytes::Bytes;
// use prost::Message;
// use pyo3::exceptions::PyValueError;
use crate::encrypt::callback::handle_receive_data;

#[gen_stub_pyfunction]
#[pyfunction]
pub fn did_receive_data(data: Vec<u8>) {
  handle_receive_data(&data);
}

#[gen_stub_pyfunction]
#[pyfunction]
pub fn wrap_message(py: Python, payload: Vec<u8>) -> PyResult<PyObject> {
  // match GaitAnalysisResult::decode(Bytes::from(payload.to_vec())) {
  //   Ok(msg) => {
  //   }
  //   Err(e) => Err(PyValueError::new_err(e.to_string())),
  // }
  let data = tml_msg_builder::build_to_app(&payload);
  let py_bytes = PyBytes::new(py, &data);
  Ok(py_bytes.into())
}

// #[gen_stub_pyfunction]
// #[pyfunction]
// pub fn encrypt(
//   py: Python,
//   key: &str,
//   plaintext: &[u8],
//   user_id: &str,
//   sn_code: &str,
// ) -> PyResult<PyObject> {
//   let encrypted = aes_gcm::encrypt(key, plaintext, user_id, sn_code);
//   match encrypted {
//     Ok(encrypted) => {
//       let py_bytes = PyBytes::new(py, &encrypted);
//       Ok(py_bytes.into())
//     }
//     Err(e) => Err(e.into()),
//   }
// }

// #[gen_stub_pyfunction]
// #[pyfunction]
// pub fn decrypt(
//   py: Python,
//   key: &str,
//   ciphertext: &[u8],
//   user_id: &str,
//   sn_code: &str,
// ) -> PyResult<PyObject> {
//   let decrypted = aes_gcm::decrypt(key, ciphertext, user_id, sn_code);
//   match decrypted {
//     Ok(decrypted) => {
//       let py_bytes = PyBytes::new(py, &decrypted);
//       Ok(py_bytes.into())
//     }
//     Err(e) => Err(e.into()),
//   }
// }

#[gen_stub_pyfunction]
#[pyfunction]
pub fn encrypt(py: Python, plaintext: Vec<u8>) -> PyResult<PyObject> {
  let encrypted = aes_gcm::default_encrypt(&plaintext);
  match encrypted {
    Ok(encrypted) => {
      let py_bytes = PyBytes::new(py, &encrypted);
      Ok(py_bytes.into())
    }
    Err(e) => Err(e.into()),
  }
}

#[gen_stub_pyfunction]
#[pyfunction]
pub fn decrypt(py: Python, ciphertext: Vec<u8>) -> PyResult<PyObject> {
  let decrypted = aes_gcm::default_decrypt(&ciphertext);
  match decrypted {
    Ok(decrypted) => {
      let py_bytes = PyBytes::new(py, &decrypted);
      Ok(py_bytes.into())
    }
    Err(e) => Err(e.into()),
  }
}
