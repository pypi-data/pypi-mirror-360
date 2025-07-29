#[allow(dead_code)]
#[repr(u8)]
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum LogLevel {
  Error = 0,
  Warn = 1,
  Info = 2,
  Debug = 3,
  Trace = 4,
}

#[repr(u8)]
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum GaitPattern {
  Unspecified = 0,
  Walk = 1,
  Run = 2,
}

#[repr(u8)]
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum FootStrike {
  Unspecified = 0,
  LeftFoot,
  RightFoot,
}

#[repr(u8)]
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum AbnormalGait {
  /// Default value per Protobuf convention
  Unspecified = 0,
  /// No load detected
  NoLoad = 1,
  /// Support phase detected
  HandrailSupported = 2,
  /// Unilateral dragging detected
  UnilateralDragging = 3,
}
