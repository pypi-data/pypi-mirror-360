use std::sync::Once;

#[allow(unused_imports)]
use super::logging::LogLevel;
use tracing_subscriber::{filter::LevelFilter, layer::SubscriberExt, *};

crate::cfg_import_logging!();

pub fn initialize_logging(level: LogLevel) {
  let level: log::Level = level.into();
  init_logging(level);
  info!(
    "{} version: {}",
    env!("CARGO_PKG_NAME"),
    env!("CARGO_PKG_VERSION")
  );
}

pub fn init_logging(level: log::Level) {
  cfg_if::cfg_if! {
    if #[cfg(target_os = "android")] {
      let filter = to_log_filter(level);
      android_logger::init_once(
          android_logger::Config::default()
              .with_max_level(filter) // limit log level
              .with_tag("EvoRun-SDK")
      );
      // android_logger::Config::default().with_max_level(filter);
      debug!("Android log level: {:?}", level);
      return;
    }
  };

  static INIT: Once = Once::new();
  #[allow(unreachable_code)]
  INIT.call_once(|| {
    let console_layer = fmt::Layer::new()
      .with_file(true)
      .with_line_number(true)
      .with_filter(to_log_level_filter(level));

    let subscriber: layer::Layered<
      filter::Filtered<fmt::Layer<Registry>, LevelFilter, Registry>,
      Registry,
    > = Registry::default().with(console_layer);

    tracing::subscriber::set_global_default(subscriber).expect("Failed to set subscriber");
  });
}

#[allow(dead_code)]
fn to_log_filter(level: log::Level) -> log::LevelFilter {
  match level {
    log::Level::Error => log::LevelFilter::Error,
    log::Level::Warn => log::LevelFilter::Warn,
    log::Level::Info => log::LevelFilter::Info,
    log::Level::Debug => log::LevelFilter::Debug,
    log::Level::Trace => log::LevelFilter::Trace,
  }
}

fn to_log_level_filter(level: log::Level) -> tracing_subscriber::filter::LevelFilter {
  match level {
    log::Level::Error => LevelFilter::ERROR,
    log::Level::Warn => LevelFilter::WARN,
    log::Level::Info => LevelFilter::INFO,
    log::Level::Debug => LevelFilter::DEBUG,
    log::Level::Trace => LevelFilter::TRACE,
  }
}
