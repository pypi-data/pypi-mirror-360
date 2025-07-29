#[cfg(not(feature = "python"))]
fn main() {
  eprintln!("This example is only supported for the 'python' feature.");
}

cfg_if::cfg_if! {
  if #[cfg(feature = "python")] {
    use pyo3_stub_gen::Result;
    use treadmill_sdk::utils::logging_desktop::initialize_logging;
    use treadmill_sdk::utils::logging::LogLevel;
    treadmill_sdk::cfg_import_logging!();
  }
}

// export PYO3_PYTHON=/opt/homebrew/Caskroom/miniconda/base/envs/py310/bin/python
// export DYLD_LIBRARY_PATH=/opt/homebrew/Caskroom/miniconda/base/envs/py310/lib:$DYLD_LIBRARY_PATH
// cargo run --bin stub_gen --features "python"
#[cfg(feature = "python")]
fn main() -> Result<()> {
  initialize_logging(LogLevel::Info);
  // `stub_info` is a function defined by `define_stub_info_gatherer!` macro.
  // let stub = treadmill_sdk::stub_info()?;
  let stub = treadmill_sdk::python::py_mod::stub_info()?;
  stub.generate()?;
  Ok(())
}
