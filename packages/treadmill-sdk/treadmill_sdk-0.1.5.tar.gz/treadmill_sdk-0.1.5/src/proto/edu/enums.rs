#![allow(non_camel_case_types)]

use crate::impl_enum_conversion;

// crate::cfg_import_logging!();

impl_enum_conversion!(
  SamplingRate,
  SAMPLING_RATE_NONE = 0,
  SAMPLING_RATE_OFF = 1,
  SAMPLING_RATE_25 = 2,
  SAMPLING_RATE_50 = 3,
  SAMPLING_RATE_100 = 4,
  SAMPLING_RATE_200 = 5
);

impl_enum_conversion!(
  AfeSampleRate,
  AFE_SR_INVALID = 0,
  AFE_SR_OFF = 1,
  AFE_SR_125 = 2,
  AFE_SR_250 = 3,
  AFE_SR_500 = 4,
  AFE_SR_1000 = 5,
  AFE_SR_2000 = 6
);

impl_enum_conversion!(
  EduImuSampleRate,
  IMU_SR_UNUSED = 0,
  IMU_SR_OFF = 1,
  IMU_SR_25 = 2,
  IMU_SR_50 = 3,
  IMU_SR_100 = 4,
  IMU_SR_400 = 5
);

impl_enum_conversion!(
  ImuMode,
  NOT_SET = 0,
  ACC = 1,
  GYRO = 2,
  ACC_GYRO = 3,
  EULER = 4
);

// enum UploadDataType {
//   TYPE_UNSPECIFIED = 0;
//   RAW_DATA         = 1;   // upload 16bit raw data
//   CALIBRATED_DATA  = 2;   // Upload physical values computed using calibration parameters
// }

// message ImuCalibration {
//   XYZ acc_correction  = 2;  // acceleration 3-asix offset
//   XYZ gyro_correction = 3;  // gyroscope 3-asix offset
// }

impl_enum_conversion!(
  MagSampleRate,
  MAG_SR_UNUSED = 0,
  MAG_SR_OFF = 1,
  MAG_SR_10 = 2,
  MAG_SR_20 = 3,
  MAG_SR_50 = 4,
  MAG_SR_100 = 5
);

impl_enum_conversion!(
  CtrlBoxPort,
  PORT_NONE = 0,
  PORT_A = 1,
  PORT_B = 2,
  PORT_C = 3,
  PORT_D = 4,
  PORT_E = 5,
  PORT_F = 6
);
