use parking_lot::RwLock;
type MsgRespCallback = Box<dyn Fn(String, String) + Send + Sync>;

lazy_static::lazy_static! {
  static ref MSG_RESP_CB: RwLock<Option<MsgRespCallback>> = RwLock::new(None);
}

pub fn set_msg_resp_callback(callback: MsgRespCallback) {
  let mut cb = MSG_RESP_CB.write();
  *cb = Some(callback);
}

pub fn run_msg_resp_callback(device_id: String, msg: String) {
  let cb = MSG_RESP_CB.read();
  if let Some(ref callback) = *cb {
    callback(device_id, msg);
  }
}
