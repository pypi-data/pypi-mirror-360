use tracing_subscriber::filter::LevelFilter;

#[allow(dead_code)]
#[repr(u8)]
// #[cfg_attr(target_family = "wasm", wasm_bindgen::prelude::wasm_bindgen)]
#[cfg_attr(feature = "python", pyo3_stub_gen::derive::gen_stub_pyclass_enum)]
#[cfg_attr(feature = "python", pyo3::pyclass(eq, eq_int))]
#[derive(Debug, Clone, Copy, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
pub enum LogLevel {
  Error = 0,
  Warn = 1,
  Info = 2,
  Debug = 3,
  Trace = 4,
}

impl From<u8> for LogLevel {
  fn from(val: u8) -> Self {
    match val {
      0 => LogLevel::Error,
      1 => LogLevel::Warn,
      2 => LogLevel::Info,
      3 => LogLevel::Debug,
      4 => LogLevel::Trace,
      _ => LogLevel::Info,
    }
  }
}

impl From<LogLevel> for log::Level {
  fn from(val: LogLevel) -> Self {
    match val {
      LogLevel::Error => log::Level::Error,
      LogLevel::Warn => log::Level::Warn,
      LogLevel::Info => log::Level::Info,
      LogLevel::Debug => log::Level::Debug,
      LogLevel::Trace => log::Level::Trace,
    }
  }
}

impl From<LogLevel> for tracing::Level {
  fn from(val: LogLevel) -> Self {
    match val {
      LogLevel::Error => tracing::Level::ERROR,
      LogLevel::Warn => tracing::Level::WARN,
      LogLevel::Info => tracing::Level::INFO,
      LogLevel::Debug => tracing::Level::DEBUG,
      LogLevel::Trace => tracing::Level::TRACE,
    }
  }
}

impl From<LogLevel> for LevelFilter {
  fn from(val: LogLevel) -> Self {
    match val {
      LogLevel::Error => LevelFilter::ERROR,
      LogLevel::Warn => LevelFilter::WARN,
      LogLevel::Info => LevelFilter::INFO,
      LogLevel::Debug => LevelFilter::DEBUG,
      LogLevel::Trace => LevelFilter::TRACE,
    }
  }
}
