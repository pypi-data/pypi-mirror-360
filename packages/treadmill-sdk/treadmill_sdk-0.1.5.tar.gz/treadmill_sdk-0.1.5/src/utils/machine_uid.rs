use tracing::trace;

use crate::utils::string_utils;

pub fn get_machine_uid(desired_length: usize) -> Option<String> {
  // Get the UUID from the machine_uid crate
  let uuid: String = machine_uid::get().ok()?; // Handle possible errors from get()

  // Remove dashes from the UUID
  let uuid_no_dashes = uuid.replace("-", "").to_uppercase();

  trace!("machine_uid: {:?}", uuid_no_dashes);

  // Pad or truncate the UUID to the desired length
  let padded_uuid = string_utils::pad_or_truncate(uuid_no_dashes, desired_length);

  trace!("padded uuid: {:?}", padded_uuid);

  // Return the processed UUID
  Some(padded_uuid)
}

#[cfg(test)]
mod tests {
  use crate::utils::logging_desktop::init_logging;

  use super::get_machine_uid;
  crate::cfg_import_logging!();

  #[test]
  fn get_machine_uid_test() {
    init_logging(log::Level::Debug);
    let serial = get_machine_uid(16);
    match serial {
      Some(s) => trace!("System UUID: {}", s),
      None => trace!("Failed to get System UUID"),
    }
  }
}
