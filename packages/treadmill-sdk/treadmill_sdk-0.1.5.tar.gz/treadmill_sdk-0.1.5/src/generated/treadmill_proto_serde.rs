use crate::generated::treadmill_proto::*;
impl serde::Serialize for AbnormalGait {
    #[allow(deprecated)]
    fn serialize<S>(&self, serializer: S) -> std::result::Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        let variant = match self {
            Self::Unspecified => "ABNORMAL_GAIT_UNSPECIFIED",
            Self::NoLoad => "NO_LOAD",
            Self::HandrailSupported => "HANDRAIL_SUPPORTED",
            Self::UnilateralDragging => "UNILATERAL_DRAGGING",
        };
        serializer.serialize_str(variant)
    }
}
impl<'de> serde::Deserialize<'de> for AbnormalGait {
    #[allow(deprecated)]
    fn deserialize<D>(deserializer: D) -> std::result::Result<Self, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        const FIELDS: &[&str] = &[
            "ABNORMAL_GAIT_UNSPECIFIED",
            "NO_LOAD",
            "HANDRAIL_SUPPORTED",
            "UNILATERAL_DRAGGING",
        ];

        struct GeneratedVisitor;

        impl<'de> serde::de::Visitor<'de> for GeneratedVisitor {
            type Value = AbnormalGait;

            fn expecting(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(formatter, "expected one of: {:?}", &FIELDS)
            }

            fn visit_i64<E>(self, v: i64) -> std::result::Result<Self::Value, E>
            where
                E: serde::de::Error,
            {
                i32::try_from(v)
                    .ok()
                    .and_then(|x| x.try_into().ok())
                    .ok_or_else(|| {
                        serde::de::Error::invalid_value(serde::de::Unexpected::Signed(v), &self)
                    })
            }

            fn visit_u64<E>(self, v: u64) -> std::result::Result<Self::Value, E>
            where
                E: serde::de::Error,
            {
                i32::try_from(v)
                    .ok()
                    .and_then(|x| x.try_into().ok())
                    .ok_or_else(|| {
                        serde::de::Error::invalid_value(serde::de::Unexpected::Unsigned(v), &self)
                    })
            }

            fn visit_str<E>(self, value: &str) -> std::result::Result<Self::Value, E>
            where
                E: serde::de::Error,
            {
                match value {
                    "ABNORMAL_GAIT_UNSPECIFIED" => Ok(AbnormalGait::Unspecified),
                    "NO_LOAD" => Ok(AbnormalGait::NoLoad),
                    "HANDRAIL_SUPPORTED" => Ok(AbnormalGait::HandrailSupported),
                    "UNILATERAL_DRAGGING" => Ok(AbnormalGait::UnilateralDragging),
                    _ => Err(serde::de::Error::unknown_variant(value, FIELDS)),
                }
            }
        }
        deserializer.deserialize_any(GeneratedVisitor)
    }
}
impl serde::Serialize for AmpsData {
    #[allow(deprecated)]
    fn serialize<S>(&self, serializer: S) -> std::result::Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        use serde::ser::SerializeStruct;
        let mut len = 0;
        if self.error != 0 {
            len += 1;
        }
        if self.seq_num != 0 {
            len += 1;
        }
        if !self.amps_value.is_empty() {
            len += 1;
        }
        let mut struct_ser = serializer.serialize_struct("tech.brainco.treadmill.AmpsData", len)?;
        if self.error != 0 {
            let v = ConfigRespError::try_from(self.error)
                .map_err(|_| serde::ser::Error::custom(format!("Invalid variant {}", self.error)))?;
            struct_ser.serialize_field("error", &v)?;
        }
        if self.seq_num != 0 {
            struct_ser.serialize_field("seqNum", &self.seq_num)?;
        }
        if !self.amps_value.is_empty() {
            struct_ser.serialize_field("ampsValue", &self.amps_value.iter().map(pbjson::private::base64::encode).collect::<Vec<_>>())?;
        }
        struct_ser.end()
    }
}
impl<'de> serde::Deserialize<'de> for AmpsData {
    #[allow(deprecated)]
    fn deserialize<D>(deserializer: D) -> std::result::Result<Self, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        const FIELDS: &[&str] = &[
            "error",
            "seq_num",
            "seqNum",
            "amps_value",
            "ampsValue",
        ];

        #[allow(clippy::enum_variant_names)]
        enum GeneratedField {
            Error,
            SeqNum,
            AmpsValue,
        }
        impl<'de> serde::Deserialize<'de> for GeneratedField {
            fn deserialize<D>(deserializer: D) -> std::result::Result<GeneratedField, D::Error>
            where
                D: serde::Deserializer<'de>,
            {
                struct GeneratedVisitor;

                impl<'de> serde::de::Visitor<'de> for GeneratedVisitor {
                    type Value = GeneratedField;

                    fn expecting(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                        write!(formatter, "expected one of: {:?}", &FIELDS)
                    }

                    #[allow(unused_variables)]
                    fn visit_str<E>(self, value: &str) -> std::result::Result<GeneratedField, E>
                    where
                        E: serde::de::Error,
                    {
                        match value {
                            "error" => Ok(GeneratedField::Error),
                            "seqNum" | "seq_num" => Ok(GeneratedField::SeqNum),
                            "ampsValue" | "amps_value" => Ok(GeneratedField::AmpsValue),
                            _ => Err(serde::de::Error::unknown_field(value, FIELDS)),
                        }
                    }
                }
                deserializer.deserialize_identifier(GeneratedVisitor)
            }
        }
        struct GeneratedVisitor;
        impl<'de> serde::de::Visitor<'de> for GeneratedVisitor {
            type Value = AmpsData;

            fn expecting(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                formatter.write_str("struct tech.brainco.treadmill.AmpsData")
            }

            fn visit_map<V>(self, mut map_: V) -> std::result::Result<AmpsData, V::Error>
                where
                    V: serde::de::MapAccess<'de>,
            {
                let mut error__ = None;
                let mut seq_num__ = None;
                let mut amps_value__ = None;
                while let Some(k) = map_.next_key()? {
                    match k {
                        GeneratedField::Error => {
                            if error__.is_some() {
                                return Err(serde::de::Error::duplicate_field("error"));
                            }
                            error__ = Some(map_.next_value::<ConfigRespError>()? as i32);
                        }
                        GeneratedField::SeqNum => {
                            if seq_num__.is_some() {
                                return Err(serde::de::Error::duplicate_field("seqNum"));
                            }
                            seq_num__ = 
                                Some(map_.next_value::<::pbjson::private::NumberDeserialize<_>>()?.0)
                            ;
                        }
                        GeneratedField::AmpsValue => {
                            if amps_value__.is_some() {
                                return Err(serde::de::Error::duplicate_field("ampsValue"));
                            }
                            amps_value__ = 
                                Some(map_.next_value::<Vec<::pbjson::private::BytesDeserialize<_>>>()?
                                    .into_iter().map(|x| x.0).collect())
                            ;
                        }
                    }
                }
                Ok(AmpsData {
                    error: error__.unwrap_or_default(),
                    seq_num: seq_num__.unwrap_or_default(),
                    amps_value: amps_value__.unwrap_or_default(),
                })
            }
        }
        deserializer.deserialize_struct("tech.brainco.treadmill.AmpsData", FIELDS, GeneratedVisitor)
    }
}
impl serde::Serialize for AppSensor {
    #[allow(deprecated)]
    fn serialize<S>(&self, serializer: S) -> std::result::Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        use serde::ser::SerializeStruct;
        let mut len = 0;
        if self.msg_id != 0 {
            len += 1;
        }
        if self.msg_cmd != 0 {
            len += 1;
        }
        if self.ota_cfg.is_some() {
            len += 1;
        }
        let mut struct_ser = serializer.serialize_struct("tech.brainco.treadmill.AppSensor", len)?;
        if self.msg_id != 0 {
            struct_ser.serialize_field("msgId", &self.msg_id)?;
        }
        if self.msg_cmd != 0 {
            let v = ConfigReqType::try_from(self.msg_cmd)
                .map_err(|_| serde::ser::Error::custom(format!("Invalid variant {}", self.msg_cmd)))?;
            struct_ser.serialize_field("msgCmd", &v)?;
        }
        if let Some(v) = self.ota_cfg.as_ref() {
            struct_ser.serialize_field("otaCfg", v)?;
        }
        struct_ser.end()
    }
}
impl<'de> serde::Deserialize<'de> for AppSensor {
    #[allow(deprecated)]
    fn deserialize<D>(deserializer: D) -> std::result::Result<Self, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        const FIELDS: &[&str] = &[
            "msg_id",
            "msgId",
            "msg_cmd",
            "msgCmd",
            "ota_cfg",
            "otaCfg",
        ];

        #[allow(clippy::enum_variant_names)]
        enum GeneratedField {
            MsgId,
            MsgCmd,
            OtaCfg,
        }
        impl<'de> serde::Deserialize<'de> for GeneratedField {
            fn deserialize<D>(deserializer: D) -> std::result::Result<GeneratedField, D::Error>
            where
                D: serde::Deserializer<'de>,
            {
                struct GeneratedVisitor;

                impl<'de> serde::de::Visitor<'de> for GeneratedVisitor {
                    type Value = GeneratedField;

                    fn expecting(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                        write!(formatter, "expected one of: {:?}", &FIELDS)
                    }

                    #[allow(unused_variables)]
                    fn visit_str<E>(self, value: &str) -> std::result::Result<GeneratedField, E>
                    where
                        E: serde::de::Error,
                    {
                        match value {
                            "msgId" | "msg_id" => Ok(GeneratedField::MsgId),
                            "msgCmd" | "msg_cmd" => Ok(GeneratedField::MsgCmd),
                            "otaCfg" | "ota_cfg" => Ok(GeneratedField::OtaCfg),
                            _ => Err(serde::de::Error::unknown_field(value, FIELDS)),
                        }
                    }
                }
                deserializer.deserialize_identifier(GeneratedVisitor)
            }
        }
        struct GeneratedVisitor;
        impl<'de> serde::de::Visitor<'de> for GeneratedVisitor {
            type Value = AppSensor;

            fn expecting(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                formatter.write_str("struct tech.brainco.treadmill.AppSensor")
            }

            fn visit_map<V>(self, mut map_: V) -> std::result::Result<AppSensor, V::Error>
                where
                    V: serde::de::MapAccess<'de>,
            {
                let mut msg_id__ = None;
                let mut msg_cmd__ = None;
                let mut ota_cfg__ = None;
                while let Some(k) = map_.next_key()? {
                    match k {
                        GeneratedField::MsgId => {
                            if msg_id__.is_some() {
                                return Err(serde::de::Error::duplicate_field("msgId"));
                            }
                            msg_id__ = 
                                Some(map_.next_value::<::pbjson::private::NumberDeserialize<_>>()?.0)
                            ;
                        }
                        GeneratedField::MsgCmd => {
                            if msg_cmd__.is_some() {
                                return Err(serde::de::Error::duplicate_field("msgCmd"));
                            }
                            msg_cmd__ = Some(map_.next_value::<ConfigReqType>()? as i32);
                        }
                        GeneratedField::OtaCfg => {
                            if ota_cfg__.is_some() {
                                return Err(serde::de::Error::duplicate_field("otaCfg"));
                            }
                            ota_cfg__ = map_.next_value()?;
                        }
                    }
                }
                Ok(AppSensor {
                    msg_id: msg_id__.unwrap_or_default(),
                    msg_cmd: msg_cmd__.unwrap_or_default(),
                    ota_cfg: ota_cfg__,
                })
            }
        }
        deserializer.deserialize_struct("tech.brainco.treadmill.AppSensor", FIELDS, GeneratedVisitor)
    }
}
impl serde::Serialize for ConfigReqType {
    #[allow(deprecated)]
    fn serialize<S>(&self, serializer: S) -> std::result::Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        let variant = match self {
            Self::ReqNone => "REQ_NONE",
            Self::GetDeviceInfo => "GET_DEVICE_INFO",
            Self::SetDeviceInfo => "SET_DEVICE_INFO",
            Self::GetSensorConfig => "GET_SENSOR_CONFIG",
            Self::StartDataStream => "START_DATA_STREAM",
            Self::StopDataStream => "STOP_DATA_STREAM",
            Self::StartEvorun => "START_EVORUN",
            Self::StopEvorun => "STOP_EVORUN",
            Self::CalibrateImu => "CALIBRATE_IMU",
        };
        serializer.serialize_str(variant)
    }
}
impl<'de> serde::Deserialize<'de> for ConfigReqType {
    #[allow(deprecated)]
    fn deserialize<D>(deserializer: D) -> std::result::Result<Self, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        const FIELDS: &[&str] = &[
            "REQ_NONE",
            "GET_DEVICE_INFO",
            "SET_DEVICE_INFO",
            "GET_SENSOR_CONFIG",
            "START_DATA_STREAM",
            "STOP_DATA_STREAM",
            "START_EVORUN",
            "STOP_EVORUN",
            "CALIBRATE_IMU",
        ];

        struct GeneratedVisitor;

        impl<'de> serde::de::Visitor<'de> for GeneratedVisitor {
            type Value = ConfigReqType;

            fn expecting(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(formatter, "expected one of: {:?}", &FIELDS)
            }

            fn visit_i64<E>(self, v: i64) -> std::result::Result<Self::Value, E>
            where
                E: serde::de::Error,
            {
                i32::try_from(v)
                    .ok()
                    .and_then(|x| x.try_into().ok())
                    .ok_or_else(|| {
                        serde::de::Error::invalid_value(serde::de::Unexpected::Signed(v), &self)
                    })
            }

            fn visit_u64<E>(self, v: u64) -> std::result::Result<Self::Value, E>
            where
                E: serde::de::Error,
            {
                i32::try_from(v)
                    .ok()
                    .and_then(|x| x.try_into().ok())
                    .ok_or_else(|| {
                        serde::de::Error::invalid_value(serde::de::Unexpected::Unsigned(v), &self)
                    })
            }

            fn visit_str<E>(self, value: &str) -> std::result::Result<Self::Value, E>
            where
                E: serde::de::Error,
            {
                match value {
                    "REQ_NONE" => Ok(ConfigReqType::ReqNone),
                    "GET_DEVICE_INFO" => Ok(ConfigReqType::GetDeviceInfo),
                    "SET_DEVICE_INFO" => Ok(ConfigReqType::SetDeviceInfo),
                    "GET_SENSOR_CONFIG" => Ok(ConfigReqType::GetSensorConfig),
                    "START_DATA_STREAM" => Ok(ConfigReqType::StartDataStream),
                    "STOP_DATA_STREAM" => Ok(ConfigReqType::StopDataStream),
                    "START_EVORUN" => Ok(ConfigReqType::StartEvorun),
                    "STOP_EVORUN" => Ok(ConfigReqType::StopEvorun),
                    "CALIBRATE_IMU" => Ok(ConfigReqType::CalibrateImu),
                    _ => Err(serde::de::Error::unknown_variant(value, FIELDS)),
                }
            }
        }
        deserializer.deserialize_any(GeneratedVisitor)
    }
}
impl serde::Serialize for ConfigRespError {
    #[allow(deprecated)]
    fn serialize<S>(&self, serializer: S) -> std::result::Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        let variant = match self {
            Self::ConfigErrSuccess => "CONFIG_ERR_SUCCESS",
            Self::ConfigErrHardware => "CONFIG_ERR_HARDWARE",
            Self::ConfigErrParameter => "CONFIG_ERR_PARAMETER",
            Self::ConfigErrUnknown => "CONFIG_ERR_UNKNOWN",
        };
        serializer.serialize_str(variant)
    }
}
impl<'de> serde::Deserialize<'de> for ConfigRespError {
    #[allow(deprecated)]
    fn deserialize<D>(deserializer: D) -> std::result::Result<Self, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        const FIELDS: &[&str] = &[
            "CONFIG_ERR_SUCCESS",
            "CONFIG_ERR_HARDWARE",
            "CONFIG_ERR_PARAMETER",
            "CONFIG_ERR_UNKNOWN",
        ];

        struct GeneratedVisitor;

        impl<'de> serde::de::Visitor<'de> for GeneratedVisitor {
            type Value = ConfigRespError;

            fn expecting(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(formatter, "expected one of: {:?}", &FIELDS)
            }

            fn visit_i64<E>(self, v: i64) -> std::result::Result<Self::Value, E>
            where
                E: serde::de::Error,
            {
                i32::try_from(v)
                    .ok()
                    .and_then(|x| x.try_into().ok())
                    .ok_or_else(|| {
                        serde::de::Error::invalid_value(serde::de::Unexpected::Signed(v), &self)
                    })
            }

            fn visit_u64<E>(self, v: u64) -> std::result::Result<Self::Value, E>
            where
                E: serde::de::Error,
            {
                i32::try_from(v)
                    .ok()
                    .and_then(|x| x.try_into().ok())
                    .ok_or_else(|| {
                        serde::de::Error::invalid_value(serde::de::Unexpected::Unsigned(v), &self)
                    })
            }

            fn visit_str<E>(self, value: &str) -> std::result::Result<Self::Value, E>
            where
                E: serde::de::Error,
            {
                match value {
                    "CONFIG_ERR_SUCCESS" => Ok(ConfigRespError::ConfigErrSuccess),
                    "CONFIG_ERR_HARDWARE" => Ok(ConfigRespError::ConfigErrHardware),
                    "CONFIG_ERR_PARAMETER" => Ok(ConfigRespError::ConfigErrParameter),
                    "CONFIG_ERR_UNKNOWN" => Ok(ConfigRespError::ConfigErrUnknown),
                    _ => Err(serde::de::Error::unknown_variant(value, FIELDS)),
                }
            }
        }
        deserializer.deserialize_any(GeneratedVisitor)
    }
}
impl serde::Serialize for DebugInfo {
    #[allow(deprecated)]
    fn serialize<S>(&self, serializer: S) -> std::result::Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        use serde::ser::SerializeStruct;
        let mut len = 0;
        if self.current_range != 0. {
            len += 1;
        }
        if self.acc_range != 0. {
            len += 1;
        }
        if self.gyro_range != 0. {
            len += 1;
        }
        let mut struct_ser = serializer.serialize_struct("tech.brainco.treadmill.DebugInfo", len)?;
        if self.current_range != 0. {
            struct_ser.serialize_field("currentRange", &self.current_range)?;
        }
        if self.acc_range != 0. {
            struct_ser.serialize_field("accRange", &self.acc_range)?;
        }
        if self.gyro_range != 0. {
            struct_ser.serialize_field("gyroRange", &self.gyro_range)?;
        }
        struct_ser.end()
    }
}
impl<'de> serde::Deserialize<'de> for DebugInfo {
    #[allow(deprecated)]
    fn deserialize<D>(deserializer: D) -> std::result::Result<Self, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        const FIELDS: &[&str] = &[
            "current_range",
            "currentRange",
            "acc_range",
            "accRange",
            "gyro_range",
            "gyroRange",
        ];

        #[allow(clippy::enum_variant_names)]
        enum GeneratedField {
            CurrentRange,
            AccRange,
            GyroRange,
        }
        impl<'de> serde::Deserialize<'de> for GeneratedField {
            fn deserialize<D>(deserializer: D) -> std::result::Result<GeneratedField, D::Error>
            where
                D: serde::Deserializer<'de>,
            {
                struct GeneratedVisitor;

                impl<'de> serde::de::Visitor<'de> for GeneratedVisitor {
                    type Value = GeneratedField;

                    fn expecting(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                        write!(formatter, "expected one of: {:?}", &FIELDS)
                    }

                    #[allow(unused_variables)]
                    fn visit_str<E>(self, value: &str) -> std::result::Result<GeneratedField, E>
                    where
                        E: serde::de::Error,
                    {
                        match value {
                            "currentRange" | "current_range" => Ok(GeneratedField::CurrentRange),
                            "accRange" | "acc_range" => Ok(GeneratedField::AccRange),
                            "gyroRange" | "gyro_range" => Ok(GeneratedField::GyroRange),
                            _ => Err(serde::de::Error::unknown_field(value, FIELDS)),
                        }
                    }
                }
                deserializer.deserialize_identifier(GeneratedVisitor)
            }
        }
        struct GeneratedVisitor;
        impl<'de> serde::de::Visitor<'de> for GeneratedVisitor {
            type Value = DebugInfo;

            fn expecting(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                formatter.write_str("struct tech.brainco.treadmill.DebugInfo")
            }

            fn visit_map<V>(self, mut map_: V) -> std::result::Result<DebugInfo, V::Error>
                where
                    V: serde::de::MapAccess<'de>,
            {
                let mut current_range__ = None;
                let mut acc_range__ = None;
                let mut gyro_range__ = None;
                while let Some(k) = map_.next_key()? {
                    match k {
                        GeneratedField::CurrentRange => {
                            if current_range__.is_some() {
                                return Err(serde::de::Error::duplicate_field("currentRange"));
                            }
                            current_range__ = 
                                Some(map_.next_value::<::pbjson::private::NumberDeserialize<_>>()?.0)
                            ;
                        }
                        GeneratedField::AccRange => {
                            if acc_range__.is_some() {
                                return Err(serde::de::Error::duplicate_field("accRange"));
                            }
                            acc_range__ = 
                                Some(map_.next_value::<::pbjson::private::NumberDeserialize<_>>()?.0)
                            ;
                        }
                        GeneratedField::GyroRange => {
                            if gyro_range__.is_some() {
                                return Err(serde::de::Error::duplicate_field("gyroRange"));
                            }
                            gyro_range__ = 
                                Some(map_.next_value::<::pbjson::private::NumberDeserialize<_>>()?.0)
                            ;
                        }
                    }
                }
                Ok(DebugInfo {
                    current_range: current_range__.unwrap_or_default(),
                    acc_range: acc_range__.unwrap_or_default(),
                    gyro_range: gyro_range__.unwrap_or_default(),
                })
            }
        }
        deserializer.deserialize_struct("tech.brainco.treadmill.DebugInfo", FIELDS, GeneratedVisitor)
    }
}
impl serde::Serialize for DeviceEvent {
    #[allow(deprecated)]
    fn serialize<S>(&self, serializer: S) -> std::result::Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        let variant = match self {
            Self::EventUnspecified => "EVENT_UNSPECIFIED",
            Self::HardwareErr => "HARDWARE_ERR",
            Self::CalibrateImuOk => "CALIBRATE_IMU_OK",
            Self::CalibrateImuFail => "CALIBRATE_IMU_FAIL",
        };
        serializer.serialize_str(variant)
    }
}
impl<'de> serde::Deserialize<'de> for DeviceEvent {
    #[allow(deprecated)]
    fn deserialize<D>(deserializer: D) -> std::result::Result<Self, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        const FIELDS: &[&str] = &[
            "EVENT_UNSPECIFIED",
            "HARDWARE_ERR",
            "CALIBRATE_IMU_OK",
            "CALIBRATE_IMU_FAIL",
        ];

        struct GeneratedVisitor;

        impl<'de> serde::de::Visitor<'de> for GeneratedVisitor {
            type Value = DeviceEvent;

            fn expecting(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(formatter, "expected one of: {:?}", &FIELDS)
            }

            fn visit_i64<E>(self, v: i64) -> std::result::Result<Self::Value, E>
            where
                E: serde::de::Error,
            {
                i32::try_from(v)
                    .ok()
                    .and_then(|x| x.try_into().ok())
                    .ok_or_else(|| {
                        serde::de::Error::invalid_value(serde::de::Unexpected::Signed(v), &self)
                    })
            }

            fn visit_u64<E>(self, v: u64) -> std::result::Result<Self::Value, E>
            where
                E: serde::de::Error,
            {
                i32::try_from(v)
                    .ok()
                    .and_then(|x| x.try_into().ok())
                    .ok_or_else(|| {
                        serde::de::Error::invalid_value(serde::de::Unexpected::Unsigned(v), &self)
                    })
            }

            fn visit_str<E>(self, value: &str) -> std::result::Result<Self::Value, E>
            where
                E: serde::de::Error,
            {
                match value {
                    "EVENT_UNSPECIFIED" => Ok(DeviceEvent::EventUnspecified),
                    "HARDWARE_ERR" => Ok(DeviceEvent::HardwareErr),
                    "CALIBRATE_IMU_OK" => Ok(DeviceEvent::CalibrateImuOk),
                    "CALIBRATE_IMU_FAIL" => Ok(DeviceEvent::CalibrateImuFail),
                    _ => Err(serde::de::Error::unknown_variant(value, FIELDS)),
                }
            }
        }
        deserializer.deserialize_any(GeneratedVisitor)
    }
}
impl serde::Serialize for DeviceInfo {
    #[allow(deprecated)]
    fn serialize<S>(&self, serializer: S) -> std::result::Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        use serde::ser::SerializeStruct;
        let mut len = 0;
        if !self.serial_number.is_empty() {
            len += 1;
        }
        if !self.firmware_revision.is_empty() {
            len += 1;
        }
        let mut struct_ser = serializer.serialize_struct("tech.brainco.treadmill.DeviceInfo", len)?;
        if !self.serial_number.is_empty() {
            struct_ser.serialize_field("serialNumber", &self.serial_number)?;
        }
        if !self.firmware_revision.is_empty() {
            struct_ser.serialize_field("firmwareRevision", &self.firmware_revision)?;
        }
        struct_ser.end()
    }
}
impl<'de> serde::Deserialize<'de> for DeviceInfo {
    #[allow(deprecated)]
    fn deserialize<D>(deserializer: D) -> std::result::Result<Self, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        const FIELDS: &[&str] = &[
            "serial_number",
            "serialNumber",
            "firmware_revision",
            "firmwareRevision",
        ];

        #[allow(clippy::enum_variant_names)]
        enum GeneratedField {
            SerialNumber,
            FirmwareRevision,
        }
        impl<'de> serde::Deserialize<'de> for GeneratedField {
            fn deserialize<D>(deserializer: D) -> std::result::Result<GeneratedField, D::Error>
            where
                D: serde::Deserializer<'de>,
            {
                struct GeneratedVisitor;

                impl<'de> serde::de::Visitor<'de> for GeneratedVisitor {
                    type Value = GeneratedField;

                    fn expecting(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                        write!(formatter, "expected one of: {:?}", &FIELDS)
                    }

                    #[allow(unused_variables)]
                    fn visit_str<E>(self, value: &str) -> std::result::Result<GeneratedField, E>
                    where
                        E: serde::de::Error,
                    {
                        match value {
                            "serialNumber" | "serial_number" => Ok(GeneratedField::SerialNumber),
                            "firmwareRevision" | "firmware_revision" => Ok(GeneratedField::FirmwareRevision),
                            _ => Err(serde::de::Error::unknown_field(value, FIELDS)),
                        }
                    }
                }
                deserializer.deserialize_identifier(GeneratedVisitor)
            }
        }
        struct GeneratedVisitor;
        impl<'de> serde::de::Visitor<'de> for GeneratedVisitor {
            type Value = DeviceInfo;

            fn expecting(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                formatter.write_str("struct tech.brainco.treadmill.DeviceInfo")
            }

            fn visit_map<V>(self, mut map_: V) -> std::result::Result<DeviceInfo, V::Error>
                where
                    V: serde::de::MapAccess<'de>,
            {
                let mut serial_number__ = None;
                let mut firmware_revision__ = None;
                while let Some(k) = map_.next_key()? {
                    match k {
                        GeneratedField::SerialNumber => {
                            if serial_number__.is_some() {
                                return Err(serde::de::Error::duplicate_field("serialNumber"));
                            }
                            serial_number__ = Some(map_.next_value()?);
                        }
                        GeneratedField::FirmwareRevision => {
                            if firmware_revision__.is_some() {
                                return Err(serde::de::Error::duplicate_field("firmwareRevision"));
                            }
                            firmware_revision__ = Some(map_.next_value()?);
                        }
                    }
                }
                Ok(DeviceInfo {
                    serial_number: serial_number__.unwrap_or_default(),
                    firmware_revision: firmware_revision__.unwrap_or_default(),
                })
            }
        }
        deserializer.deserialize_struct("tech.brainco.treadmill.DeviceInfo", FIELDS, GeneratedVisitor)
    }
}
impl serde::Serialize for FlexConfResp {
    #[allow(deprecated)]
    fn serialize<S>(&self, serializer: S) -> std::result::Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        use serde::ser::SerializeStruct;
        let mut len = 0;
        if self.error != 0 {
            len += 1;
        }
        if self.config.is_some() {
            len += 1;
        }
        let mut struct_ser = serializer.serialize_struct("tech.brainco.treadmill.FlexConfResp", len)?;
        if self.error != 0 {
            let v = ConfigRespError::try_from(self.error)
                .map_err(|_| serde::ser::Error::custom(format!("Invalid variant {}", self.error)))?;
            struct_ser.serialize_field("error", &v)?;
        }
        if let Some(v) = self.config.as_ref() {
            struct_ser.serialize_field("config", v)?;
        }
        struct_ser.end()
    }
}
impl<'de> serde::Deserialize<'de> for FlexConfResp {
    #[allow(deprecated)]
    fn deserialize<D>(deserializer: D) -> std::result::Result<Self, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        const FIELDS: &[&str] = &[
            "error",
            "config",
        ];

        #[allow(clippy::enum_variant_names)]
        enum GeneratedField {
            Error,
            Config,
        }
        impl<'de> serde::Deserialize<'de> for GeneratedField {
            fn deserialize<D>(deserializer: D) -> std::result::Result<GeneratedField, D::Error>
            where
                D: serde::Deserializer<'de>,
            {
                struct GeneratedVisitor;

                impl<'de> serde::de::Visitor<'de> for GeneratedVisitor {
                    type Value = GeneratedField;

                    fn expecting(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                        write!(formatter, "expected one of: {:?}", &FIELDS)
                    }

                    #[allow(unused_variables)]
                    fn visit_str<E>(self, value: &str) -> std::result::Result<GeneratedField, E>
                    where
                        E: serde::de::Error,
                    {
                        match value {
                            "error" => Ok(GeneratedField::Error),
                            "config" => Ok(GeneratedField::Config),
                            _ => Err(serde::de::Error::unknown_field(value, FIELDS)),
                        }
                    }
                }
                deserializer.deserialize_identifier(GeneratedVisitor)
            }
        }
        struct GeneratedVisitor;
        impl<'de> serde::de::Visitor<'de> for GeneratedVisitor {
            type Value = FlexConfResp;

            fn expecting(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                formatter.write_str("struct tech.brainco.treadmill.FlexConfResp")
            }

            fn visit_map<V>(self, mut map_: V) -> std::result::Result<FlexConfResp, V::Error>
                where
                    V: serde::de::MapAccess<'de>,
            {
                let mut error__ = None;
                let mut config__ = None;
                while let Some(k) = map_.next_key()? {
                    match k {
                        GeneratedField::Error => {
                            if error__.is_some() {
                                return Err(serde::de::Error::duplicate_field("error"));
                            }
                            error__ = Some(map_.next_value::<ConfigRespError>()? as i32);
                        }
                        GeneratedField::Config => {
                            if config__.is_some() {
                                return Err(serde::de::Error::duplicate_field("config"));
                            }
                            config__ = map_.next_value()?;
                        }
                    }
                }
                Ok(FlexConfResp {
                    error: error__.unwrap_or_default(),
                    config: config__,
                })
            }
        }
        deserializer.deserialize_struct("tech.brainco.treadmill.FlexConfResp", FIELDS, GeneratedVisitor)
    }
}
impl serde::Serialize for FlexConfig {
    #[allow(deprecated)]
    fn serialize<S>(&self, serializer: S) -> std::result::Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        use serde::ser::SerializeStruct;
        let mut len = 0;
        if self.sample_rate != 0 {
            len += 1;
        }
        let mut struct_ser = serializer.serialize_struct("tech.brainco.treadmill.FlexConfig", len)?;
        if self.sample_rate != 0 {
            let v = SamplingRate::try_from(self.sample_rate)
                .map_err(|_| serde::ser::Error::custom(format!("Invalid variant {}", self.sample_rate)))?;
            struct_ser.serialize_field("sampleRate", &v)?;
        }
        struct_ser.end()
    }
}
impl<'de> serde::Deserialize<'de> for FlexConfig {
    #[allow(deprecated)]
    fn deserialize<D>(deserializer: D) -> std::result::Result<Self, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        const FIELDS: &[&str] = &[
            "sample_rate",
            "sampleRate",
        ];

        #[allow(clippy::enum_variant_names)]
        enum GeneratedField {
            SampleRate,
        }
        impl<'de> serde::Deserialize<'de> for GeneratedField {
            fn deserialize<D>(deserializer: D) -> std::result::Result<GeneratedField, D::Error>
            where
                D: serde::Deserializer<'de>,
            {
                struct GeneratedVisitor;

                impl<'de> serde::de::Visitor<'de> for GeneratedVisitor {
                    type Value = GeneratedField;

                    fn expecting(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                        write!(formatter, "expected one of: {:?}", &FIELDS)
                    }

                    #[allow(unused_variables)]
                    fn visit_str<E>(self, value: &str) -> std::result::Result<GeneratedField, E>
                    where
                        E: serde::de::Error,
                    {
                        match value {
                            "sampleRate" | "sample_rate" => Ok(GeneratedField::SampleRate),
                            _ => Err(serde::de::Error::unknown_field(value, FIELDS)),
                        }
                    }
                }
                deserializer.deserialize_identifier(GeneratedVisitor)
            }
        }
        struct GeneratedVisitor;
        impl<'de> serde::de::Visitor<'de> for GeneratedVisitor {
            type Value = FlexConfig;

            fn expecting(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                formatter.write_str("struct tech.brainco.treadmill.FlexConfig")
            }

            fn visit_map<V>(self, mut map_: V) -> std::result::Result<FlexConfig, V::Error>
                where
                    V: serde::de::MapAccess<'de>,
            {
                let mut sample_rate__ = None;
                while let Some(k) = map_.next_key()? {
                    match k {
                        GeneratedField::SampleRate => {
                            if sample_rate__.is_some() {
                                return Err(serde::de::Error::duplicate_field("sampleRate"));
                            }
                            sample_rate__ = Some(map_.next_value::<SamplingRate>()? as i32);
                        }
                    }
                }
                Ok(FlexConfig {
                    sample_rate: sample_rate__.unwrap_or_default(),
                })
            }
        }
        deserializer.deserialize_struct("tech.brainco.treadmill.FlexConfig", FIELDS, GeneratedVisitor)
    }
}
impl serde::Serialize for FlexData {
    #[allow(deprecated)]
    fn serialize<S>(&self, serializer: S) -> std::result::Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        use serde::ser::SerializeStruct;
        let mut len = 0;
        if self.error != 0 {
            len += 1;
        }
        if self.seq_num != 0 {
            len += 1;
        }
        if !self.channel_adc_value.is_empty() {
            len += 1;
        }
        let mut struct_ser = serializer.serialize_struct("tech.brainco.treadmill.FlexData", len)?;
        if self.error != 0 {
            let v = ConfigRespError::try_from(self.error)
                .map_err(|_| serde::ser::Error::custom(format!("Invalid variant {}", self.error)))?;
            struct_ser.serialize_field("error", &v)?;
        }
        if self.seq_num != 0 {
            struct_ser.serialize_field("seqNum", &self.seq_num)?;
        }
        if !self.channel_adc_value.is_empty() {
            struct_ser.serialize_field("channelAdcValue", &self.channel_adc_value.iter().map(pbjson::private::base64::encode).collect::<Vec<_>>())?;
        }
        struct_ser.end()
    }
}
impl<'de> serde::Deserialize<'de> for FlexData {
    #[allow(deprecated)]
    fn deserialize<D>(deserializer: D) -> std::result::Result<Self, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        const FIELDS: &[&str] = &[
            "error",
            "seq_num",
            "seqNum",
            "channel_adc_value",
            "channelAdcValue",
        ];

        #[allow(clippy::enum_variant_names)]
        enum GeneratedField {
            Error,
            SeqNum,
            ChannelAdcValue,
        }
        impl<'de> serde::Deserialize<'de> for GeneratedField {
            fn deserialize<D>(deserializer: D) -> std::result::Result<GeneratedField, D::Error>
            where
                D: serde::Deserializer<'de>,
            {
                struct GeneratedVisitor;

                impl<'de> serde::de::Visitor<'de> for GeneratedVisitor {
                    type Value = GeneratedField;

                    fn expecting(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                        write!(formatter, "expected one of: {:?}", &FIELDS)
                    }

                    #[allow(unused_variables)]
                    fn visit_str<E>(self, value: &str) -> std::result::Result<GeneratedField, E>
                    where
                        E: serde::de::Error,
                    {
                        match value {
                            "error" => Ok(GeneratedField::Error),
                            "seqNum" | "seq_num" => Ok(GeneratedField::SeqNum),
                            "channelAdcValue" | "channel_adc_value" => Ok(GeneratedField::ChannelAdcValue),
                            _ => Err(serde::de::Error::unknown_field(value, FIELDS)),
                        }
                    }
                }
                deserializer.deserialize_identifier(GeneratedVisitor)
            }
        }
        struct GeneratedVisitor;
        impl<'de> serde::de::Visitor<'de> for GeneratedVisitor {
            type Value = FlexData;

            fn expecting(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                formatter.write_str("struct tech.brainco.treadmill.FlexData")
            }

            fn visit_map<V>(self, mut map_: V) -> std::result::Result<FlexData, V::Error>
                where
                    V: serde::de::MapAccess<'de>,
            {
                let mut error__ = None;
                let mut seq_num__ = None;
                let mut channel_adc_value__ = None;
                while let Some(k) = map_.next_key()? {
                    match k {
                        GeneratedField::Error => {
                            if error__.is_some() {
                                return Err(serde::de::Error::duplicate_field("error"));
                            }
                            error__ = Some(map_.next_value::<ConfigRespError>()? as i32);
                        }
                        GeneratedField::SeqNum => {
                            if seq_num__.is_some() {
                                return Err(serde::de::Error::duplicate_field("seqNum"));
                            }
                            seq_num__ = 
                                Some(map_.next_value::<::pbjson::private::NumberDeserialize<_>>()?.0)
                            ;
                        }
                        GeneratedField::ChannelAdcValue => {
                            if channel_adc_value__.is_some() {
                                return Err(serde::de::Error::duplicate_field("channelAdcValue"));
                            }
                            channel_adc_value__ = 
                                Some(map_.next_value::<Vec<::pbjson::private::BytesDeserialize<_>>>()?
                                    .into_iter().map(|x| x.0).collect())
                            ;
                        }
                    }
                }
                Ok(FlexData {
                    error: error__.unwrap_or_default(),
                    seq_num: seq_num__.unwrap_or_default(),
                    channel_adc_value: channel_adc_value__.unwrap_or_default(),
                })
            }
        }
        deserializer.deserialize_struct("tech.brainco.treadmill.FlexData", FIELDS, GeneratedVisitor)
    }
}
impl serde::Serialize for GaitAnalysisResult {
    #[allow(deprecated)]
    fn serialize<S>(&self, serializer: S) -> std::result::Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        use serde::ser::SerializeStruct;
        let mut len = 0;
        if self.msg_id != 0 {
            len += 1;
        }
        if self.timestamp != 0 {
            len += 1;
        }
        if self.foot != 0 {
            len += 1;
        }
        if self.pattern != 0 {
            len += 1;
        }
        if self.gait_duration != 0 {
            len += 1;
        }
        if self.sport_id != 0 {
            len += 1;
        }
        if self.dbg_data.is_some() {
            len += 1;
        }
        if self.sport_runtime != 0 {
            len += 1;
        }
        if self.step_load != 0. {
            len += 1;
        }
        if self.abnormal_gait != 0 {
            len += 1;
        }
        let mut struct_ser = serializer.serialize_struct("tech.brainco.treadmill.GaitAnalysisResult", len)?;
        if self.msg_id != 0 {
            struct_ser.serialize_field("msgId", &self.msg_id)?;
        }
        if self.timestamp != 0 {
            struct_ser.serialize_field("timestamp", &self.timestamp)?;
        }
        if self.foot != 0 {
            let v = gait_analysis_result::FootStrike::try_from(self.foot)
                .map_err(|_| serde::ser::Error::custom(format!("Invalid variant {}", self.foot)))?;
            struct_ser.serialize_field("foot", &v)?;
        }
        if self.pattern != 0 {
            let v = gait_analysis_result::GaitPattern::try_from(self.pattern)
                .map_err(|_| serde::ser::Error::custom(format!("Invalid variant {}", self.pattern)))?;
            struct_ser.serialize_field("pattern", &v)?;
        }
        if self.gait_duration != 0 {
            struct_ser.serialize_field("gaitDuration", &self.gait_duration)?;
        }
        if self.sport_id != 0 {
            struct_ser.serialize_field("sportId", &self.sport_id)?;
        }
        if let Some(v) = self.dbg_data.as_ref() {
            struct_ser.serialize_field("dbgData", v)?;
        }
        if self.sport_runtime != 0 {
            struct_ser.serialize_field("sportRuntime", &self.sport_runtime)?;
        }
        if self.step_load != 0. {
            struct_ser.serialize_field("stepLoad", &self.step_load)?;
        }
        if self.abnormal_gait != 0 {
            let v = AbnormalGait::try_from(self.abnormal_gait)
                .map_err(|_| serde::ser::Error::custom(format!("Invalid variant {}", self.abnormal_gait)))?;
            struct_ser.serialize_field("abnormalGait", &v)?;
        }
        struct_ser.end()
    }
}
impl<'de> serde::Deserialize<'de> for GaitAnalysisResult {
    #[allow(deprecated)]
    fn deserialize<D>(deserializer: D) -> std::result::Result<Self, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        const FIELDS: &[&str] = &[
            "msg_id",
            "msgId",
            "timestamp",
            "foot",
            "pattern",
            "gait_duration",
            "gaitDuration",
            "sport_id",
            "sportId",
            "dbg_data",
            "dbgData",
            "sport_runtime",
            "sportRuntime",
            "step_load",
            "stepLoad",
            "abnormal_gait",
            "abnormalGait",
        ];

        #[allow(clippy::enum_variant_names)]
        enum GeneratedField {
            MsgId,
            Timestamp,
            Foot,
            Pattern,
            GaitDuration,
            SportId,
            DbgData,
            SportRuntime,
            StepLoad,
            AbnormalGait,
        }
        impl<'de> serde::Deserialize<'de> for GeneratedField {
            fn deserialize<D>(deserializer: D) -> std::result::Result<GeneratedField, D::Error>
            where
                D: serde::Deserializer<'de>,
            {
                struct GeneratedVisitor;

                impl<'de> serde::de::Visitor<'de> for GeneratedVisitor {
                    type Value = GeneratedField;

                    fn expecting(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                        write!(formatter, "expected one of: {:?}", &FIELDS)
                    }

                    #[allow(unused_variables)]
                    fn visit_str<E>(self, value: &str) -> std::result::Result<GeneratedField, E>
                    where
                        E: serde::de::Error,
                    {
                        match value {
                            "msgId" | "msg_id" => Ok(GeneratedField::MsgId),
                            "timestamp" => Ok(GeneratedField::Timestamp),
                            "foot" => Ok(GeneratedField::Foot),
                            "pattern" => Ok(GeneratedField::Pattern),
                            "gaitDuration" | "gait_duration" => Ok(GeneratedField::GaitDuration),
                            "sportId" | "sport_id" => Ok(GeneratedField::SportId),
                            "dbgData" | "dbg_data" => Ok(GeneratedField::DbgData),
                            "sportRuntime" | "sport_runtime" => Ok(GeneratedField::SportRuntime),
                            "stepLoad" | "step_load" => Ok(GeneratedField::StepLoad),
                            "abnormalGait" | "abnormal_gait" => Ok(GeneratedField::AbnormalGait),
                            _ => Err(serde::de::Error::unknown_field(value, FIELDS)),
                        }
                    }
                }
                deserializer.deserialize_identifier(GeneratedVisitor)
            }
        }
        struct GeneratedVisitor;
        impl<'de> serde::de::Visitor<'de> for GeneratedVisitor {
            type Value = GaitAnalysisResult;

            fn expecting(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                formatter.write_str("struct tech.brainco.treadmill.GaitAnalysisResult")
            }

            fn visit_map<V>(self, mut map_: V) -> std::result::Result<GaitAnalysisResult, V::Error>
                where
                    V: serde::de::MapAccess<'de>,
            {
                let mut msg_id__ = None;
                let mut timestamp__ = None;
                let mut foot__ = None;
                let mut pattern__ = None;
                let mut gait_duration__ = None;
                let mut sport_id__ = None;
                let mut dbg_data__ = None;
                let mut sport_runtime__ = None;
                let mut step_load__ = None;
                let mut abnormal_gait__ = None;
                while let Some(k) = map_.next_key()? {
                    match k {
                        GeneratedField::MsgId => {
                            if msg_id__.is_some() {
                                return Err(serde::de::Error::duplicate_field("msgId"));
                            }
                            msg_id__ = 
                                Some(map_.next_value::<::pbjson::private::NumberDeserialize<_>>()?.0)
                            ;
                        }
                        GeneratedField::Timestamp => {
                            if timestamp__.is_some() {
                                return Err(serde::de::Error::duplicate_field("timestamp"));
                            }
                            timestamp__ = 
                                Some(map_.next_value::<::pbjson::private::NumberDeserialize<_>>()?.0)
                            ;
                        }
                        GeneratedField::Foot => {
                            if foot__.is_some() {
                                return Err(serde::de::Error::duplicate_field("foot"));
                            }
                            foot__ = Some(map_.next_value::<gait_analysis_result::FootStrike>()? as i32);
                        }
                        GeneratedField::Pattern => {
                            if pattern__.is_some() {
                                return Err(serde::de::Error::duplicate_field("pattern"));
                            }
                            pattern__ = Some(map_.next_value::<gait_analysis_result::GaitPattern>()? as i32);
                        }
                        GeneratedField::GaitDuration => {
                            if gait_duration__.is_some() {
                                return Err(serde::de::Error::duplicate_field("gaitDuration"));
                            }
                            gait_duration__ = 
                                Some(map_.next_value::<::pbjson::private::NumberDeserialize<_>>()?.0)
                            ;
                        }
                        GeneratedField::SportId => {
                            if sport_id__.is_some() {
                                return Err(serde::de::Error::duplicate_field("sportId"));
                            }
                            sport_id__ = 
                                Some(map_.next_value::<::pbjson::private::NumberDeserialize<_>>()?.0)
                            ;
                        }
                        GeneratedField::DbgData => {
                            if dbg_data__.is_some() {
                                return Err(serde::de::Error::duplicate_field("dbgData"));
                            }
                            dbg_data__ = map_.next_value()?;
                        }
                        GeneratedField::SportRuntime => {
                            if sport_runtime__.is_some() {
                                return Err(serde::de::Error::duplicate_field("sportRuntime"));
                            }
                            sport_runtime__ = 
                                Some(map_.next_value::<::pbjson::private::NumberDeserialize<_>>()?.0)
                            ;
                        }
                        GeneratedField::StepLoad => {
                            if step_load__.is_some() {
                                return Err(serde::de::Error::duplicate_field("stepLoad"));
                            }
                            step_load__ = 
                                Some(map_.next_value::<::pbjson::private::NumberDeserialize<_>>()?.0)
                            ;
                        }
                        GeneratedField::AbnormalGait => {
                            if abnormal_gait__.is_some() {
                                return Err(serde::de::Error::duplicate_field("abnormalGait"));
                            }
                            abnormal_gait__ = Some(map_.next_value::<AbnormalGait>()? as i32);
                        }
                    }
                }
                Ok(GaitAnalysisResult {
                    msg_id: msg_id__.unwrap_or_default(),
                    timestamp: timestamp__.unwrap_or_default(),
                    foot: foot__.unwrap_or_default(),
                    pattern: pattern__.unwrap_or_default(),
                    gait_duration: gait_duration__.unwrap_or_default(),
                    sport_id: sport_id__.unwrap_or_default(),
                    dbg_data: dbg_data__,
                    sport_runtime: sport_runtime__.unwrap_or_default(),
                    step_load: step_load__.unwrap_or_default(),
                    abnormal_gait: abnormal_gait__.unwrap_or_default(),
                })
            }
        }
        deserializer.deserialize_struct("tech.brainco.treadmill.GaitAnalysisResult", FIELDS, GeneratedVisitor)
    }
}
impl serde::Serialize for gait_analysis_result::FootStrike {
    #[allow(deprecated)]
    fn serialize<S>(&self, serializer: S) -> std::result::Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        let variant = match self {
            Self::Unspecified => "FOOT_STRIKE_UNSPECIFIED",
            Self::LeftFoot => "LEFT_FOOT",
            Self::RightFoot => "RIGHT_FOOT",
        };
        serializer.serialize_str(variant)
    }
}
impl<'de> serde::Deserialize<'de> for gait_analysis_result::FootStrike {
    #[allow(deprecated)]
    fn deserialize<D>(deserializer: D) -> std::result::Result<Self, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        const FIELDS: &[&str] = &[
            "FOOT_STRIKE_UNSPECIFIED",
            "LEFT_FOOT",
            "RIGHT_FOOT",
        ];

        struct GeneratedVisitor;

        impl<'de> serde::de::Visitor<'de> for GeneratedVisitor {
            type Value = gait_analysis_result::FootStrike;

            fn expecting(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(formatter, "expected one of: {:?}", &FIELDS)
            }

            fn visit_i64<E>(self, v: i64) -> std::result::Result<Self::Value, E>
            where
                E: serde::de::Error,
            {
                i32::try_from(v)
                    .ok()
                    .and_then(|x| x.try_into().ok())
                    .ok_or_else(|| {
                        serde::de::Error::invalid_value(serde::de::Unexpected::Signed(v), &self)
                    })
            }

            fn visit_u64<E>(self, v: u64) -> std::result::Result<Self::Value, E>
            where
                E: serde::de::Error,
            {
                i32::try_from(v)
                    .ok()
                    .and_then(|x| x.try_into().ok())
                    .ok_or_else(|| {
                        serde::de::Error::invalid_value(serde::de::Unexpected::Unsigned(v), &self)
                    })
            }

            fn visit_str<E>(self, value: &str) -> std::result::Result<Self::Value, E>
            where
                E: serde::de::Error,
            {
                match value {
                    "FOOT_STRIKE_UNSPECIFIED" => Ok(gait_analysis_result::FootStrike::Unspecified),
                    "LEFT_FOOT" => Ok(gait_analysis_result::FootStrike::LeftFoot),
                    "RIGHT_FOOT" => Ok(gait_analysis_result::FootStrike::RightFoot),
                    _ => Err(serde::de::Error::unknown_variant(value, FIELDS)),
                }
            }
        }
        deserializer.deserialize_any(GeneratedVisitor)
    }
}
impl serde::Serialize for gait_analysis_result::GaitPattern {
    #[allow(deprecated)]
    fn serialize<S>(&self, serializer: S) -> std::result::Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        let variant = match self {
            Self::Unspecified => "GAIT_PATTERN_UNSPECIFIED",
            Self::Walk => "WALK",
            Self::Run => "RUN",
        };
        serializer.serialize_str(variant)
    }
}
impl<'de> serde::Deserialize<'de> for gait_analysis_result::GaitPattern {
    #[allow(deprecated)]
    fn deserialize<D>(deserializer: D) -> std::result::Result<Self, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        const FIELDS: &[&str] = &[
            "GAIT_PATTERN_UNSPECIFIED",
            "WALK",
            "RUN",
        ];

        struct GeneratedVisitor;

        impl<'de> serde::de::Visitor<'de> for GeneratedVisitor {
            type Value = gait_analysis_result::GaitPattern;

            fn expecting(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(formatter, "expected one of: {:?}", &FIELDS)
            }

            fn visit_i64<E>(self, v: i64) -> std::result::Result<Self::Value, E>
            where
                E: serde::de::Error,
            {
                i32::try_from(v)
                    .ok()
                    .and_then(|x| x.try_into().ok())
                    .ok_or_else(|| {
                        serde::de::Error::invalid_value(serde::de::Unexpected::Signed(v), &self)
                    })
            }

            fn visit_u64<E>(self, v: u64) -> std::result::Result<Self::Value, E>
            where
                E: serde::de::Error,
            {
                i32::try_from(v)
                    .ok()
                    .and_then(|x| x.try_into().ok())
                    .ok_or_else(|| {
                        serde::de::Error::invalid_value(serde::de::Unexpected::Unsigned(v), &self)
                    })
            }

            fn visit_str<E>(self, value: &str) -> std::result::Result<Self::Value, E>
            where
                E: serde::de::Error,
            {
                match value {
                    "GAIT_PATTERN_UNSPECIFIED" => Ok(gait_analysis_result::GaitPattern::Unspecified),
                    "WALK" => Ok(gait_analysis_result::GaitPattern::Walk),
                    "RUN" => Ok(gait_analysis_result::GaitPattern::Run),
                    _ => Err(serde::de::Error::unknown_variant(value, FIELDS)),
                }
            }
        }
        deserializer.deserialize_any(GeneratedVisitor)
    }
}
impl serde::Serialize for ImuConfResp {
    #[allow(deprecated)]
    fn serialize<S>(&self, serializer: S) -> std::result::Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        use serde::ser::SerializeStruct;
        let mut len = 0;
        if self.error != 0 {
            len += 1;
        }
        if self.config.is_some() {
            len += 1;
        }
        if self.acc_coefficient != 0. {
            len += 1;
        }
        if self.gyro_coefficient != 0. {
            len += 1;
        }
        let mut struct_ser = serializer.serialize_struct("tech.brainco.treadmill.ImuConfResp", len)?;
        if self.error != 0 {
            let v = ConfigRespError::try_from(self.error)
                .map_err(|_| serde::ser::Error::custom(format!("Invalid variant {}", self.error)))?;
            struct_ser.serialize_field("error", &v)?;
        }
        if let Some(v) = self.config.as_ref() {
            struct_ser.serialize_field("config", v)?;
        }
        if self.acc_coefficient != 0. {
            struct_ser.serialize_field("accCoefficient", &self.acc_coefficient)?;
        }
        if self.gyro_coefficient != 0. {
            struct_ser.serialize_field("gyroCoefficient", &self.gyro_coefficient)?;
        }
        struct_ser.end()
    }
}
impl<'de> serde::Deserialize<'de> for ImuConfResp {
    #[allow(deprecated)]
    fn deserialize<D>(deserializer: D) -> std::result::Result<Self, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        const FIELDS: &[&str] = &[
            "error",
            "config",
            "acc_coefficient",
            "accCoefficient",
            "gyro_coefficient",
            "gyroCoefficient",
        ];

        #[allow(clippy::enum_variant_names)]
        enum GeneratedField {
            Error,
            Config,
            AccCoefficient,
            GyroCoefficient,
        }
        impl<'de> serde::Deserialize<'de> for GeneratedField {
            fn deserialize<D>(deserializer: D) -> std::result::Result<GeneratedField, D::Error>
            where
                D: serde::Deserializer<'de>,
            {
                struct GeneratedVisitor;

                impl<'de> serde::de::Visitor<'de> for GeneratedVisitor {
                    type Value = GeneratedField;

                    fn expecting(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                        write!(formatter, "expected one of: {:?}", &FIELDS)
                    }

                    #[allow(unused_variables)]
                    fn visit_str<E>(self, value: &str) -> std::result::Result<GeneratedField, E>
                    where
                        E: serde::de::Error,
                    {
                        match value {
                            "error" => Ok(GeneratedField::Error),
                            "config" => Ok(GeneratedField::Config),
                            "accCoefficient" | "acc_coefficient" => Ok(GeneratedField::AccCoefficient),
                            "gyroCoefficient" | "gyro_coefficient" => Ok(GeneratedField::GyroCoefficient),
                            _ => Err(serde::de::Error::unknown_field(value, FIELDS)),
                        }
                    }
                }
                deserializer.deserialize_identifier(GeneratedVisitor)
            }
        }
        struct GeneratedVisitor;
        impl<'de> serde::de::Visitor<'de> for GeneratedVisitor {
            type Value = ImuConfResp;

            fn expecting(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                formatter.write_str("struct tech.brainco.treadmill.ImuConfResp")
            }

            fn visit_map<V>(self, mut map_: V) -> std::result::Result<ImuConfResp, V::Error>
                where
                    V: serde::de::MapAccess<'de>,
            {
                let mut error__ = None;
                let mut config__ = None;
                let mut acc_coefficient__ = None;
                let mut gyro_coefficient__ = None;
                while let Some(k) = map_.next_key()? {
                    match k {
                        GeneratedField::Error => {
                            if error__.is_some() {
                                return Err(serde::de::Error::duplicate_field("error"));
                            }
                            error__ = Some(map_.next_value::<ConfigRespError>()? as i32);
                        }
                        GeneratedField::Config => {
                            if config__.is_some() {
                                return Err(serde::de::Error::duplicate_field("config"));
                            }
                            config__ = map_.next_value()?;
                        }
                        GeneratedField::AccCoefficient => {
                            if acc_coefficient__.is_some() {
                                return Err(serde::de::Error::duplicate_field("accCoefficient"));
                            }
                            acc_coefficient__ = 
                                Some(map_.next_value::<::pbjson::private::NumberDeserialize<_>>()?.0)
                            ;
                        }
                        GeneratedField::GyroCoefficient => {
                            if gyro_coefficient__.is_some() {
                                return Err(serde::de::Error::duplicate_field("gyroCoefficient"));
                            }
                            gyro_coefficient__ = 
                                Some(map_.next_value::<::pbjson::private::NumberDeserialize<_>>()?.0)
                            ;
                        }
                    }
                }
                Ok(ImuConfResp {
                    error: error__.unwrap_or_default(),
                    config: config__,
                    acc_coefficient: acc_coefficient__.unwrap_or_default(),
                    gyro_coefficient: gyro_coefficient__.unwrap_or_default(),
                })
            }
        }
        deserializer.deserialize_struct("tech.brainco.treadmill.ImuConfResp", FIELDS, GeneratedVisitor)
    }
}
impl serde::Serialize for ImuConfig {
    #[allow(deprecated)]
    fn serialize<S>(&self, serializer: S) -> std::result::Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        use serde::ser::SerializeStruct;
        let mut len = 0;
        if self.imu_mode != 0 {
            len += 1;
        }
        if self.imu_sr != 0 {
            len += 1;
        }
        let mut struct_ser = serializer.serialize_struct("tech.brainco.treadmill.ImuConfig", len)?;
        if self.imu_mode != 0 {
            let v = imu_config::ImuMode::try_from(self.imu_mode)
                .map_err(|_| serde::ser::Error::custom(format!("Invalid variant {}", self.imu_mode)))?;
            struct_ser.serialize_field("imuMode", &v)?;
        }
        if self.imu_sr != 0 {
            let v = ImuSampleRate::try_from(self.imu_sr)
                .map_err(|_| serde::ser::Error::custom(format!("Invalid variant {}", self.imu_sr)))?;
            struct_ser.serialize_field("imuSr", &v)?;
        }
        struct_ser.end()
    }
}
impl<'de> serde::Deserialize<'de> for ImuConfig {
    #[allow(deprecated)]
    fn deserialize<D>(deserializer: D) -> std::result::Result<Self, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        const FIELDS: &[&str] = &[
            "imu_mode",
            "imuMode",
            "imu_sr",
            "imuSr",
        ];

        #[allow(clippy::enum_variant_names)]
        enum GeneratedField {
            ImuMode,
            ImuSr,
        }
        impl<'de> serde::Deserialize<'de> for GeneratedField {
            fn deserialize<D>(deserializer: D) -> std::result::Result<GeneratedField, D::Error>
            where
                D: serde::Deserializer<'de>,
            {
                struct GeneratedVisitor;

                impl<'de> serde::de::Visitor<'de> for GeneratedVisitor {
                    type Value = GeneratedField;

                    fn expecting(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                        write!(formatter, "expected one of: {:?}", &FIELDS)
                    }

                    #[allow(unused_variables)]
                    fn visit_str<E>(self, value: &str) -> std::result::Result<GeneratedField, E>
                    where
                        E: serde::de::Error,
                    {
                        match value {
                            "imuMode" | "imu_mode" => Ok(GeneratedField::ImuMode),
                            "imuSr" | "imu_sr" => Ok(GeneratedField::ImuSr),
                            _ => Err(serde::de::Error::unknown_field(value, FIELDS)),
                        }
                    }
                }
                deserializer.deserialize_identifier(GeneratedVisitor)
            }
        }
        struct GeneratedVisitor;
        impl<'de> serde::de::Visitor<'de> for GeneratedVisitor {
            type Value = ImuConfig;

            fn expecting(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                formatter.write_str("struct tech.brainco.treadmill.ImuConfig")
            }

            fn visit_map<V>(self, mut map_: V) -> std::result::Result<ImuConfig, V::Error>
                where
                    V: serde::de::MapAccess<'de>,
            {
                let mut imu_mode__ = None;
                let mut imu_sr__ = None;
                while let Some(k) = map_.next_key()? {
                    match k {
                        GeneratedField::ImuMode => {
                            if imu_mode__.is_some() {
                                return Err(serde::de::Error::duplicate_field("imuMode"));
                            }
                            imu_mode__ = Some(map_.next_value::<imu_config::ImuMode>()? as i32);
                        }
                        GeneratedField::ImuSr => {
                            if imu_sr__.is_some() {
                                return Err(serde::de::Error::duplicate_field("imuSr"));
                            }
                            imu_sr__ = Some(map_.next_value::<ImuSampleRate>()? as i32);
                        }
                    }
                }
                Ok(ImuConfig {
                    imu_mode: imu_mode__.unwrap_or_default(),
                    imu_sr: imu_sr__.unwrap_or_default(),
                })
            }
        }
        deserializer.deserialize_struct("tech.brainco.treadmill.ImuConfig", FIELDS, GeneratedVisitor)
    }
}
impl serde::Serialize for imu_config::ImuMode {
    #[allow(deprecated)]
    fn serialize<S>(&self, serializer: S) -> std::result::Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        let variant = match self {
            Self::NotSet => "NOT_SET",
            Self::Acc => "ACC",
            Self::Gyro => "GYRO",
            Self::AccGyro => "ACC_GYRO",
            Self::Euler => "EULER",
        };
        serializer.serialize_str(variant)
    }
}
impl<'de> serde::Deserialize<'de> for imu_config::ImuMode {
    #[allow(deprecated)]
    fn deserialize<D>(deserializer: D) -> std::result::Result<Self, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        const FIELDS: &[&str] = &[
            "NOT_SET",
            "ACC",
            "GYRO",
            "ACC_GYRO",
            "EULER",
        ];

        struct GeneratedVisitor;

        impl<'de> serde::de::Visitor<'de> for GeneratedVisitor {
            type Value = imu_config::ImuMode;

            fn expecting(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(formatter, "expected one of: {:?}", &FIELDS)
            }

            fn visit_i64<E>(self, v: i64) -> std::result::Result<Self::Value, E>
            where
                E: serde::de::Error,
            {
                i32::try_from(v)
                    .ok()
                    .and_then(|x| x.try_into().ok())
                    .ok_or_else(|| {
                        serde::de::Error::invalid_value(serde::de::Unexpected::Signed(v), &self)
                    })
            }

            fn visit_u64<E>(self, v: u64) -> std::result::Result<Self::Value, E>
            where
                E: serde::de::Error,
            {
                i32::try_from(v)
                    .ok()
                    .and_then(|x| x.try_into().ok())
                    .ok_or_else(|| {
                        serde::de::Error::invalid_value(serde::de::Unexpected::Unsigned(v), &self)
                    })
            }

            fn visit_str<E>(self, value: &str) -> std::result::Result<Self::Value, E>
            where
                E: serde::de::Error,
            {
                match value {
                    "NOT_SET" => Ok(imu_config::ImuMode::NotSet),
                    "ACC" => Ok(imu_config::ImuMode::Acc),
                    "GYRO" => Ok(imu_config::ImuMode::Gyro),
                    "ACC_GYRO" => Ok(imu_config::ImuMode::AccGyro),
                    "EULER" => Ok(imu_config::ImuMode::Euler),
                    _ => Err(serde::de::Error::unknown_variant(value, FIELDS)),
                }
            }
        }
        deserializer.deserialize_any(GeneratedVisitor)
    }
}
impl serde::Serialize for ImuData {
    #[allow(deprecated)]
    fn serialize<S>(&self, serializer: S) -> std::result::Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        use serde::ser::SerializeStruct;
        let mut len = 0;
        if self.seq_num != 0 {
            len += 1;
        }
        if !self.acc_raw_data.is_empty() {
            len += 1;
        }
        if !self.gyro_raw_data.is_empty() {
            len += 1;
        }
        if !self.eular_raw_data.is_empty() {
            len += 1;
        }
        if !self.acc_correction_data.is_empty() {
            len += 1;
        }
        if !self.gyro_correction_data.is_empty() {
            len += 1;
        }
        let mut struct_ser = serializer.serialize_struct("tech.brainco.treadmill.ImuData", len)?;
        if self.seq_num != 0 {
            struct_ser.serialize_field("seqNum", &self.seq_num)?;
        }
        if !self.acc_raw_data.is_empty() {
            #[allow(clippy::needless_borrow)]
            #[allow(clippy::needless_borrows_for_generic_args)]
            struct_ser.serialize_field("accRawData", pbjson::private::base64::encode(&self.acc_raw_data).as_str())?;
        }
        if !self.gyro_raw_data.is_empty() {
            #[allow(clippy::needless_borrow)]
            #[allow(clippy::needless_borrows_for_generic_args)]
            struct_ser.serialize_field("gyroRawData", pbjson::private::base64::encode(&self.gyro_raw_data).as_str())?;
        }
        if !self.eular_raw_data.is_empty() {
            struct_ser.serialize_field("eularRawData", &self.eular_raw_data)?;
        }
        if !self.acc_correction_data.is_empty() {
            struct_ser.serialize_field("accCorrectionData", &self.acc_correction_data)?;
        }
        if !self.gyro_correction_data.is_empty() {
            struct_ser.serialize_field("gyroCorrectionData", &self.gyro_correction_data)?;
        }
        struct_ser.end()
    }
}
impl<'de> serde::Deserialize<'de> for ImuData {
    #[allow(deprecated)]
    fn deserialize<D>(deserializer: D) -> std::result::Result<Self, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        const FIELDS: &[&str] = &[
            "seq_num",
            "seqNum",
            "acc_raw_data",
            "accRawData",
            "gyro_raw_data",
            "gyroRawData",
            "eular_raw_data",
            "eularRawData",
            "acc_correction_data",
            "accCorrectionData",
            "gyro_correction_data",
            "gyroCorrectionData",
        ];

        #[allow(clippy::enum_variant_names)]
        enum GeneratedField {
            SeqNum,
            AccRawData,
            GyroRawData,
            EularRawData,
            AccCorrectionData,
            GyroCorrectionData,
        }
        impl<'de> serde::Deserialize<'de> for GeneratedField {
            fn deserialize<D>(deserializer: D) -> std::result::Result<GeneratedField, D::Error>
            where
                D: serde::Deserializer<'de>,
            {
                struct GeneratedVisitor;

                impl<'de> serde::de::Visitor<'de> for GeneratedVisitor {
                    type Value = GeneratedField;

                    fn expecting(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                        write!(formatter, "expected one of: {:?}", &FIELDS)
                    }

                    #[allow(unused_variables)]
                    fn visit_str<E>(self, value: &str) -> std::result::Result<GeneratedField, E>
                    where
                        E: serde::de::Error,
                    {
                        match value {
                            "seqNum" | "seq_num" => Ok(GeneratedField::SeqNum),
                            "accRawData" | "acc_raw_data" => Ok(GeneratedField::AccRawData),
                            "gyroRawData" | "gyro_raw_data" => Ok(GeneratedField::GyroRawData),
                            "eularRawData" | "eular_raw_data" => Ok(GeneratedField::EularRawData),
                            "accCorrectionData" | "acc_correction_data" => Ok(GeneratedField::AccCorrectionData),
                            "gyroCorrectionData" | "gyro_correction_data" => Ok(GeneratedField::GyroCorrectionData),
                            _ => Err(serde::de::Error::unknown_field(value, FIELDS)),
                        }
                    }
                }
                deserializer.deserialize_identifier(GeneratedVisitor)
            }
        }
        struct GeneratedVisitor;
        impl<'de> serde::de::Visitor<'de> for GeneratedVisitor {
            type Value = ImuData;

            fn expecting(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                formatter.write_str("struct tech.brainco.treadmill.ImuData")
            }

            fn visit_map<V>(self, mut map_: V) -> std::result::Result<ImuData, V::Error>
                where
                    V: serde::de::MapAccess<'de>,
            {
                let mut seq_num__ = None;
                let mut acc_raw_data__ = None;
                let mut gyro_raw_data__ = None;
                let mut eular_raw_data__ = None;
                let mut acc_correction_data__ = None;
                let mut gyro_correction_data__ = None;
                while let Some(k) = map_.next_key()? {
                    match k {
                        GeneratedField::SeqNum => {
                            if seq_num__.is_some() {
                                return Err(serde::de::Error::duplicate_field("seqNum"));
                            }
                            seq_num__ = 
                                Some(map_.next_value::<::pbjson::private::NumberDeserialize<_>>()?.0)
                            ;
                        }
                        GeneratedField::AccRawData => {
                            if acc_raw_data__.is_some() {
                                return Err(serde::de::Error::duplicate_field("accRawData"));
                            }
                            acc_raw_data__ = 
                                Some(map_.next_value::<::pbjson::private::BytesDeserialize<_>>()?.0)
                            ;
                        }
                        GeneratedField::GyroRawData => {
                            if gyro_raw_data__.is_some() {
                                return Err(serde::de::Error::duplicate_field("gyroRawData"));
                            }
                            gyro_raw_data__ = 
                                Some(map_.next_value::<::pbjson::private::BytesDeserialize<_>>()?.0)
                            ;
                        }
                        GeneratedField::EularRawData => {
                            if eular_raw_data__.is_some() {
                                return Err(serde::de::Error::duplicate_field("eularRawData"));
                            }
                            eular_raw_data__ = 
                                Some(map_.next_value::<Vec<::pbjson::private::NumberDeserialize<_>>>()?
                                    .into_iter().map(|x| x.0).collect())
                            ;
                        }
                        GeneratedField::AccCorrectionData => {
                            if acc_correction_data__.is_some() {
                                return Err(serde::de::Error::duplicate_field("accCorrectionData"));
                            }
                            acc_correction_data__ = 
                                Some(map_.next_value::<Vec<::pbjson::private::NumberDeserialize<_>>>()?
                                    .into_iter().map(|x| x.0).collect())
                            ;
                        }
                        GeneratedField::GyroCorrectionData => {
                            if gyro_correction_data__.is_some() {
                                return Err(serde::de::Error::duplicate_field("gyroCorrectionData"));
                            }
                            gyro_correction_data__ = 
                                Some(map_.next_value::<Vec<::pbjson::private::NumberDeserialize<_>>>()?
                                    .into_iter().map(|x| x.0).collect())
                            ;
                        }
                    }
                }
                Ok(ImuData {
                    seq_num: seq_num__.unwrap_or_default(),
                    acc_raw_data: acc_raw_data__.unwrap_or_default(),
                    gyro_raw_data: gyro_raw_data__.unwrap_or_default(),
                    eular_raw_data: eular_raw_data__.unwrap_or_default(),
                    acc_correction_data: acc_correction_data__.unwrap_or_default(),
                    gyro_correction_data: gyro_correction_data__.unwrap_or_default(),
                })
            }
        }
        deserializer.deserialize_struct("tech.brainco.treadmill.ImuData", FIELDS, GeneratedVisitor)
    }
}
impl serde::Serialize for ImuSampleRate {
    #[allow(deprecated)]
    fn serialize<S>(&self, serializer: S) -> std::result::Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        let variant = match self {
            Self::ImuSrUnspecified => "IMU_SR_UNSPECIFIED",
            Self::ImuSrOff => "IMU_SR_OFF",
            Self::ImuSr25 => "IMU_SR_25",
            Self::ImuSr50 => "IMU_SR_50",
            Self::ImuSr100 => "IMU_SR_100",
            Self::ImuSr90 => "IMU_SR_90",
            Self::ImuSr200 => "IMU_SR_200",
            Self::ImuSr400 => "IMU_SR_400",
        };
        serializer.serialize_str(variant)
    }
}
impl<'de> serde::Deserialize<'de> for ImuSampleRate {
    #[allow(deprecated)]
    fn deserialize<D>(deserializer: D) -> std::result::Result<Self, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        const FIELDS: &[&str] = &[
            "IMU_SR_UNSPECIFIED",
            "IMU_SR_OFF",
            "IMU_SR_25",
            "IMU_SR_50",
            "IMU_SR_100",
            "IMU_SR_90",
            "IMU_SR_200",
            "IMU_SR_400",
        ];

        struct GeneratedVisitor;

        impl<'de> serde::de::Visitor<'de> for GeneratedVisitor {
            type Value = ImuSampleRate;

            fn expecting(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(formatter, "expected one of: {:?}", &FIELDS)
            }

            fn visit_i64<E>(self, v: i64) -> std::result::Result<Self::Value, E>
            where
                E: serde::de::Error,
            {
                i32::try_from(v)
                    .ok()
                    .and_then(|x| x.try_into().ok())
                    .ok_or_else(|| {
                        serde::de::Error::invalid_value(serde::de::Unexpected::Signed(v), &self)
                    })
            }

            fn visit_u64<E>(self, v: u64) -> std::result::Result<Self::Value, E>
            where
                E: serde::de::Error,
            {
                i32::try_from(v)
                    .ok()
                    .and_then(|x| x.try_into().ok())
                    .ok_or_else(|| {
                        serde::de::Error::invalid_value(serde::de::Unexpected::Unsigned(v), &self)
                    })
            }

            fn visit_str<E>(self, value: &str) -> std::result::Result<Self::Value, E>
            where
                E: serde::de::Error,
            {
                match value {
                    "IMU_SR_UNSPECIFIED" => Ok(ImuSampleRate::ImuSrUnspecified),
                    "IMU_SR_OFF" => Ok(ImuSampleRate::ImuSrOff),
                    "IMU_SR_25" => Ok(ImuSampleRate::ImuSr25),
                    "IMU_SR_50" => Ok(ImuSampleRate::ImuSr50),
                    "IMU_SR_100" => Ok(ImuSampleRate::ImuSr100),
                    "IMU_SR_90" => Ok(ImuSampleRate::ImuSr90),
                    "IMU_SR_200" => Ok(ImuSampleRate::ImuSr200),
                    "IMU_SR_400" => Ok(ImuSampleRate::ImuSr400),
                    _ => Err(serde::de::Error::unknown_variant(value, FIELDS)),
                }
            }
        }
        deserializer.deserialize_any(GeneratedVisitor)
    }
}
impl serde::Serialize for OtaData {
    #[allow(deprecated)]
    fn serialize<S>(&self, serializer: S) -> std::result::Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        use serde::ser::SerializeStruct;
        let mut len = 0;
        if self.offset != 0 {
            len += 1;
        }
        if !self.data.is_empty() {
            len += 1;
        }
        if self.finished {
            len += 1;
        }
        let mut struct_ser = serializer.serialize_struct("tech.brainco.treadmill.OTAData", len)?;
        if self.offset != 0 {
            struct_ser.serialize_field("offset", &self.offset)?;
        }
        if !self.data.is_empty() {
            #[allow(clippy::needless_borrow)]
            #[allow(clippy::needless_borrows_for_generic_args)]
            struct_ser.serialize_field("data", pbjson::private::base64::encode(&self.data).as_str())?;
        }
        if self.finished {
            struct_ser.serialize_field("finished", &self.finished)?;
        }
        struct_ser.end()
    }
}
impl<'de> serde::Deserialize<'de> for OtaData {
    #[allow(deprecated)]
    fn deserialize<D>(deserializer: D) -> std::result::Result<Self, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        const FIELDS: &[&str] = &[
            "offset",
            "data",
            "finished",
        ];

        #[allow(clippy::enum_variant_names)]
        enum GeneratedField {
            Offset,
            Data,
            Finished,
        }
        impl<'de> serde::Deserialize<'de> for GeneratedField {
            fn deserialize<D>(deserializer: D) -> std::result::Result<GeneratedField, D::Error>
            where
                D: serde::Deserializer<'de>,
            {
                struct GeneratedVisitor;

                impl<'de> serde::de::Visitor<'de> for GeneratedVisitor {
                    type Value = GeneratedField;

                    fn expecting(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                        write!(formatter, "expected one of: {:?}", &FIELDS)
                    }

                    #[allow(unused_variables)]
                    fn visit_str<E>(self, value: &str) -> std::result::Result<GeneratedField, E>
                    where
                        E: serde::de::Error,
                    {
                        match value {
                            "offset" => Ok(GeneratedField::Offset),
                            "data" => Ok(GeneratedField::Data),
                            "finished" => Ok(GeneratedField::Finished),
                            _ => Err(serde::de::Error::unknown_field(value, FIELDS)),
                        }
                    }
                }
                deserializer.deserialize_identifier(GeneratedVisitor)
            }
        }
        struct GeneratedVisitor;
        impl<'de> serde::de::Visitor<'de> for GeneratedVisitor {
            type Value = OtaData;

            fn expecting(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                formatter.write_str("struct tech.brainco.treadmill.OTAData")
            }

            fn visit_map<V>(self, mut map_: V) -> std::result::Result<OtaData, V::Error>
                where
                    V: serde::de::MapAccess<'de>,
            {
                let mut offset__ = None;
                let mut data__ = None;
                let mut finished__ = None;
                while let Some(k) = map_.next_key()? {
                    match k {
                        GeneratedField::Offset => {
                            if offset__.is_some() {
                                return Err(serde::de::Error::duplicate_field("offset"));
                            }
                            offset__ = 
                                Some(map_.next_value::<::pbjson::private::NumberDeserialize<_>>()?.0)
                            ;
                        }
                        GeneratedField::Data => {
                            if data__.is_some() {
                                return Err(serde::de::Error::duplicate_field("data"));
                            }
                            data__ = 
                                Some(map_.next_value::<::pbjson::private::BytesDeserialize<_>>()?.0)
                            ;
                        }
                        GeneratedField::Finished => {
                            if finished__.is_some() {
                                return Err(serde::de::Error::duplicate_field("finished"));
                            }
                            finished__ = Some(map_.next_value()?);
                        }
                    }
                }
                Ok(OtaData {
                    offset: offset__.unwrap_or_default(),
                    data: data__.unwrap_or_default(),
                    finished: finished__.unwrap_or_default(),
                })
            }
        }
        deserializer.deserialize_struct("tech.brainco.treadmill.OTAData", FIELDS, GeneratedVisitor)
    }
}
impl serde::Serialize for OtaConfig {
    #[allow(deprecated)]
    fn serialize<S>(&self, serializer: S) -> std::result::Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        use serde::ser::SerializeStruct;
        let mut len = 0;
        if self.cmd != 0 {
            len += 1;
        }
        if self.ota_data.is_some() {
            len += 1;
        }
        if self.file_size != 0 {
            len += 1;
        }
        if !self.file_md5.is_empty() {
            len += 1;
        }
        if !self.file_sha256.is_empty() {
            len += 1;
        }
        let mut struct_ser = serializer.serialize_struct("tech.brainco.treadmill.OtaConfig", len)?;
        if self.cmd != 0 {
            let v = ota_config::Cmd::try_from(self.cmd)
                .map_err(|_| serde::ser::Error::custom(format!("Invalid variant {}", self.cmd)))?;
            struct_ser.serialize_field("cmd", &v)?;
        }
        if let Some(v) = self.ota_data.as_ref() {
            struct_ser.serialize_field("otaData", v)?;
        }
        if self.file_size != 0 {
            struct_ser.serialize_field("fileSize", &self.file_size)?;
        }
        if !self.file_md5.is_empty() {
            struct_ser.serialize_field("fileMd5", &self.file_md5)?;
        }
        if !self.file_sha256.is_empty() {
            struct_ser.serialize_field("fileSha256", &self.file_sha256)?;
        }
        struct_ser.end()
    }
}
impl<'de> serde::Deserialize<'de> for OtaConfig {
    #[allow(deprecated)]
    fn deserialize<D>(deserializer: D) -> std::result::Result<Self, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        const FIELDS: &[&str] = &[
            "cmd",
            "ota_data",
            "otaData",
            "file_size",
            "fileSize",
            "file_md5",
            "fileMd5",
            "file_sha256",
            "fileSha256",
        ];

        #[allow(clippy::enum_variant_names)]
        enum GeneratedField {
            Cmd,
            OtaData,
            FileSize,
            FileMd5,
            FileSha256,
        }
        impl<'de> serde::Deserialize<'de> for GeneratedField {
            fn deserialize<D>(deserializer: D) -> std::result::Result<GeneratedField, D::Error>
            where
                D: serde::Deserializer<'de>,
            {
                struct GeneratedVisitor;

                impl<'de> serde::de::Visitor<'de> for GeneratedVisitor {
                    type Value = GeneratedField;

                    fn expecting(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                        write!(formatter, "expected one of: {:?}", &FIELDS)
                    }

                    #[allow(unused_variables)]
                    fn visit_str<E>(self, value: &str) -> std::result::Result<GeneratedField, E>
                    where
                        E: serde::de::Error,
                    {
                        match value {
                            "cmd" => Ok(GeneratedField::Cmd),
                            "otaData" | "ota_data" => Ok(GeneratedField::OtaData),
                            "fileSize" | "file_size" => Ok(GeneratedField::FileSize),
                            "fileMd5" | "file_md5" => Ok(GeneratedField::FileMd5),
                            "fileSha256" | "file_sha256" => Ok(GeneratedField::FileSha256),
                            _ => Err(serde::de::Error::unknown_field(value, FIELDS)),
                        }
                    }
                }
                deserializer.deserialize_identifier(GeneratedVisitor)
            }
        }
        struct GeneratedVisitor;
        impl<'de> serde::de::Visitor<'de> for GeneratedVisitor {
            type Value = OtaConfig;

            fn expecting(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                formatter.write_str("struct tech.brainco.treadmill.OtaConfig")
            }

            fn visit_map<V>(self, mut map_: V) -> std::result::Result<OtaConfig, V::Error>
                where
                    V: serde::de::MapAccess<'de>,
            {
                let mut cmd__ = None;
                let mut ota_data__ = None;
                let mut file_size__ = None;
                let mut file_md5__ = None;
                let mut file_sha256__ = None;
                while let Some(k) = map_.next_key()? {
                    match k {
                        GeneratedField::Cmd => {
                            if cmd__.is_some() {
                                return Err(serde::de::Error::duplicate_field("cmd"));
                            }
                            cmd__ = Some(map_.next_value::<ota_config::Cmd>()? as i32);
                        }
                        GeneratedField::OtaData => {
                            if ota_data__.is_some() {
                                return Err(serde::de::Error::duplicate_field("otaData"));
                            }
                            ota_data__ = map_.next_value()?;
                        }
                        GeneratedField::FileSize => {
                            if file_size__.is_some() {
                                return Err(serde::de::Error::duplicate_field("fileSize"));
                            }
                            file_size__ = 
                                Some(map_.next_value::<::pbjson::private::NumberDeserialize<_>>()?.0)
                            ;
                        }
                        GeneratedField::FileMd5 => {
                            if file_md5__.is_some() {
                                return Err(serde::de::Error::duplicate_field("fileMd5"));
                            }
                            file_md5__ = Some(map_.next_value()?);
                        }
                        GeneratedField::FileSha256 => {
                            if file_sha256__.is_some() {
                                return Err(serde::de::Error::duplicate_field("fileSha256"));
                            }
                            file_sha256__ = Some(map_.next_value()?);
                        }
                    }
                }
                Ok(OtaConfig {
                    cmd: cmd__.unwrap_or_default(),
                    ota_data: ota_data__,
                    file_size: file_size__.unwrap_or_default(),
                    file_md5: file_md5__.unwrap_or_default(),
                    file_sha256: file_sha256__.unwrap_or_default(),
                })
            }
        }
        deserializer.deserialize_struct("tech.brainco.treadmill.OtaConfig", FIELDS, GeneratedVisitor)
    }
}
impl serde::Serialize for ota_config::Cmd {
    #[allow(deprecated)]
    fn serialize<S>(&self, serializer: S) -> std::result::Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        let variant = match self {
            Self::None => "NONE",
            Self::OtaStart => "OTA_START",
            Self::OtaReboot => "OTA_REBOOT",
        };
        serializer.serialize_str(variant)
    }
}
impl<'de> serde::Deserialize<'de> for ota_config::Cmd {
    #[allow(deprecated)]
    fn deserialize<D>(deserializer: D) -> std::result::Result<Self, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        const FIELDS: &[&str] = &[
            "NONE",
            "OTA_START",
            "OTA_REBOOT",
        ];

        struct GeneratedVisitor;

        impl<'de> serde::de::Visitor<'de> for GeneratedVisitor {
            type Value = ota_config::Cmd;

            fn expecting(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(formatter, "expected one of: {:?}", &FIELDS)
            }

            fn visit_i64<E>(self, v: i64) -> std::result::Result<Self::Value, E>
            where
                E: serde::de::Error,
            {
                i32::try_from(v)
                    .ok()
                    .and_then(|x| x.try_into().ok())
                    .ok_or_else(|| {
                        serde::de::Error::invalid_value(serde::de::Unexpected::Signed(v), &self)
                    })
            }

            fn visit_u64<E>(self, v: u64) -> std::result::Result<Self::Value, E>
            where
                E: serde::de::Error,
            {
                i32::try_from(v)
                    .ok()
                    .and_then(|x| x.try_into().ok())
                    .ok_or_else(|| {
                        serde::de::Error::invalid_value(serde::de::Unexpected::Unsigned(v), &self)
                    })
            }

            fn visit_str<E>(self, value: &str) -> std::result::Result<Self::Value, E>
            where
                E: serde::de::Error,
            {
                match value {
                    "NONE" => Ok(ota_config::Cmd::None),
                    "OTA_START" => Ok(ota_config::Cmd::OtaStart),
                    "OTA_REBOOT" => Ok(ota_config::Cmd::OtaReboot),
                    _ => Err(serde::de::Error::unknown_variant(value, FIELDS)),
                }
            }
        }
        deserializer.deserialize_any(GeneratedVisitor)
    }
}
impl serde::Serialize for OtaConfigResp {
    #[allow(deprecated)]
    fn serialize<S>(&self, serializer: S) -> std::result::Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        use serde::ser::SerializeStruct;
        let mut len = 0;
        if self.state != 0 {
            len += 1;
        }
        if self.offset != 0 {
            len += 1;
        }
        let mut struct_ser = serializer.serialize_struct("tech.brainco.treadmill.OtaConfigResp", len)?;
        if self.state != 0 {
            let v = ota_config_resp::State::try_from(self.state)
                .map_err(|_| serde::ser::Error::custom(format!("Invalid variant {}", self.state)))?;
            struct_ser.serialize_field("state", &v)?;
        }
        if self.offset != 0 {
            struct_ser.serialize_field("offset", &self.offset)?;
        }
        struct_ser.end()
    }
}
impl<'de> serde::Deserialize<'de> for OtaConfigResp {
    #[allow(deprecated)]
    fn deserialize<D>(deserializer: D) -> std::result::Result<Self, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        const FIELDS: &[&str] = &[
            "state",
            "offset",
        ];

        #[allow(clippy::enum_variant_names)]
        enum GeneratedField {
            State,
            Offset,
        }
        impl<'de> serde::Deserialize<'de> for GeneratedField {
            fn deserialize<D>(deserializer: D) -> std::result::Result<GeneratedField, D::Error>
            where
                D: serde::Deserializer<'de>,
            {
                struct GeneratedVisitor;

                impl<'de> serde::de::Visitor<'de> for GeneratedVisitor {
                    type Value = GeneratedField;

                    fn expecting(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                        write!(formatter, "expected one of: {:?}", &FIELDS)
                    }

                    #[allow(unused_variables)]
                    fn visit_str<E>(self, value: &str) -> std::result::Result<GeneratedField, E>
                    where
                        E: serde::de::Error,
                    {
                        match value {
                            "state" => Ok(GeneratedField::State),
                            "offset" => Ok(GeneratedField::Offset),
                            _ => Err(serde::de::Error::unknown_field(value, FIELDS)),
                        }
                    }
                }
                deserializer.deserialize_identifier(GeneratedVisitor)
            }
        }
        struct GeneratedVisitor;
        impl<'de> serde::de::Visitor<'de> for GeneratedVisitor {
            type Value = OtaConfigResp;

            fn expecting(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                formatter.write_str("struct tech.brainco.treadmill.OtaConfigResp")
            }

            fn visit_map<V>(self, mut map_: V) -> std::result::Result<OtaConfigResp, V::Error>
                where
                    V: serde::de::MapAccess<'de>,
            {
                let mut state__ = None;
                let mut offset__ = None;
                while let Some(k) = map_.next_key()? {
                    match k {
                        GeneratedField::State => {
                            if state__.is_some() {
                                return Err(serde::de::Error::duplicate_field("state"));
                            }
                            state__ = Some(map_.next_value::<ota_config_resp::State>()? as i32);
                        }
                        GeneratedField::Offset => {
                            if offset__.is_some() {
                                return Err(serde::de::Error::duplicate_field("offset"));
                            }
                            offset__ = 
                                Some(map_.next_value::<::pbjson::private::NumberDeserialize<_>>()?.0)
                            ;
                        }
                    }
                }
                Ok(OtaConfigResp {
                    state: state__.unwrap_or_default(),
                    offset: offset__.unwrap_or_default(),
                })
            }
        }
        deserializer.deserialize_struct("tech.brainco.treadmill.OtaConfigResp", FIELDS, GeneratedVisitor)
    }
}
impl serde::Serialize for ota_config_resp::State {
    #[allow(deprecated)]
    fn serialize<S>(&self, serializer: S) -> std::result::Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        let variant = match self {
            Self::None => "NONE",
            Self::Downloading => "DOWNLOADING",
            Self::DownloadFinished => "DOWNLOAD_FINISHED",
            Self::Rebooting => "REBOOTING",
            Self::Rebooted => "REBOOTED",
            Self::Abort => "ABORT",
        };
        serializer.serialize_str(variant)
    }
}
impl<'de> serde::Deserialize<'de> for ota_config_resp::State {
    #[allow(deprecated)]
    fn deserialize<D>(deserializer: D) -> std::result::Result<Self, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        const FIELDS: &[&str] = &[
            "NONE",
            "DOWNLOADING",
            "DOWNLOAD_FINISHED",
            "REBOOTING",
            "REBOOTED",
            "ABORT",
        ];

        struct GeneratedVisitor;

        impl<'de> serde::de::Visitor<'de> for GeneratedVisitor {
            type Value = ota_config_resp::State;

            fn expecting(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(formatter, "expected one of: {:?}", &FIELDS)
            }

            fn visit_i64<E>(self, v: i64) -> std::result::Result<Self::Value, E>
            where
                E: serde::de::Error,
            {
                i32::try_from(v)
                    .ok()
                    .and_then(|x| x.try_into().ok())
                    .ok_or_else(|| {
                        serde::de::Error::invalid_value(serde::de::Unexpected::Signed(v), &self)
                    })
            }

            fn visit_u64<E>(self, v: u64) -> std::result::Result<Self::Value, E>
            where
                E: serde::de::Error,
            {
                i32::try_from(v)
                    .ok()
                    .and_then(|x| x.try_into().ok())
                    .ok_or_else(|| {
                        serde::de::Error::invalid_value(serde::de::Unexpected::Unsigned(v), &self)
                    })
            }

            fn visit_str<E>(self, value: &str) -> std::result::Result<Self::Value, E>
            where
                E: serde::de::Error,
            {
                match value {
                    "NONE" => Ok(ota_config_resp::State::None),
                    "DOWNLOADING" => Ok(ota_config_resp::State::Downloading),
                    "DOWNLOAD_FINISHED" => Ok(ota_config_resp::State::DownloadFinished),
                    "REBOOTING" => Ok(ota_config_resp::State::Rebooting),
                    "REBOOTED" => Ok(ota_config_resp::State::Rebooted),
                    "ABORT" => Ok(ota_config_resp::State::Abort),
                    _ => Err(serde::de::Error::unknown_variant(value, FIELDS)),
                }
            }
        }
        deserializer.deserialize_any(GeneratedVisitor)
    }
}
impl serde::Serialize for SamplingRate {
    #[allow(deprecated)]
    fn serialize<S>(&self, serializer: S) -> std::result::Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        let variant = match self {
            Self::None => "SAMPLING_RATE_NONE",
            Self::Off => "SAMPLING_RATE_OFF",
            Self::SamplingRate25 => "SAMPLING_RATE_25",
            Self::SamplingRate50 => "SAMPLING_RATE_50",
            Self::SamplingRate100 => "SAMPLING_RATE_100",
            Self::SamplingRate200 => "SAMPLING_RATE_200",
            Self::SamplingRate270 => "SAMPLING_RATE_270",
        };
        serializer.serialize_str(variant)
    }
}
impl<'de> serde::Deserialize<'de> for SamplingRate {
    #[allow(deprecated)]
    fn deserialize<D>(deserializer: D) -> std::result::Result<Self, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        const FIELDS: &[&str] = &[
            "SAMPLING_RATE_NONE",
            "SAMPLING_RATE_OFF",
            "SAMPLING_RATE_25",
            "SAMPLING_RATE_50",
            "SAMPLING_RATE_100",
            "SAMPLING_RATE_200",
            "SAMPLING_RATE_270",
        ];

        struct GeneratedVisitor;

        impl<'de> serde::de::Visitor<'de> for GeneratedVisitor {
            type Value = SamplingRate;

            fn expecting(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(formatter, "expected one of: {:?}", &FIELDS)
            }

            fn visit_i64<E>(self, v: i64) -> std::result::Result<Self::Value, E>
            where
                E: serde::de::Error,
            {
                i32::try_from(v)
                    .ok()
                    .and_then(|x| x.try_into().ok())
                    .ok_or_else(|| {
                        serde::de::Error::invalid_value(serde::de::Unexpected::Signed(v), &self)
                    })
            }

            fn visit_u64<E>(self, v: u64) -> std::result::Result<Self::Value, E>
            where
                E: serde::de::Error,
            {
                i32::try_from(v)
                    .ok()
                    .and_then(|x| x.try_into().ok())
                    .ok_or_else(|| {
                        serde::de::Error::invalid_value(serde::de::Unexpected::Unsigned(v), &self)
                    })
            }

            fn visit_str<E>(self, value: &str) -> std::result::Result<Self::Value, E>
            where
                E: serde::de::Error,
            {
                match value {
                    "SAMPLING_RATE_NONE" => Ok(SamplingRate::None),
                    "SAMPLING_RATE_OFF" => Ok(SamplingRate::Off),
                    "SAMPLING_RATE_25" => Ok(SamplingRate::SamplingRate25),
                    "SAMPLING_RATE_50" => Ok(SamplingRate::SamplingRate50),
                    "SAMPLING_RATE_100" => Ok(SamplingRate::SamplingRate100),
                    "SAMPLING_RATE_200" => Ok(SamplingRate::SamplingRate200),
                    "SAMPLING_RATE_270" => Ok(SamplingRate::SamplingRate270),
                    _ => Err(serde::de::Error::unknown_variant(value, FIELDS)),
                }
            }
        }
        deserializer.deserialize_any(GeneratedVisitor)
    }
}
impl serde::Serialize for SensorApp {
    #[allow(deprecated)]
    fn serialize<S>(&self, serializer: S) -> std::result::Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        use serde::ser::SerializeStruct;
        let mut len = 0;
        if self.msg_id != 0 {
            len += 1;
        }
        if self.device_info.is_some() {
            len += 1;
        }
        if self.device_evt != 0 {
            len += 1;
        }
        if self.ga_result.is_some() {
            len += 1;
        }
        if self.ota_resp.is_some() {
            len += 1;
        }
        if self.ota_data.is_some() {
            len += 1;
        }
        if self.imu_data.is_some() {
            len += 1;
        }
        if self.imu_resp.is_some() {
            len += 1;
        }
        if self.flex_data.is_some() {
            len += 1;
        }
        if self.flex_resp.is_some() {
            len += 1;
        }
        if self.tm_data.is_some() {
            len += 1;
        }
        if self.amps_data.is_some() {
            len += 1;
        }
        let mut struct_ser = serializer.serialize_struct("tech.brainco.treadmill.SensorApp", len)?;
        if self.msg_id != 0 {
            struct_ser.serialize_field("msgId", &self.msg_id)?;
        }
        if let Some(v) = self.device_info.as_ref() {
            struct_ser.serialize_field("deviceInfo", v)?;
        }
        if self.device_evt != 0 {
            let v = DeviceEvent::try_from(self.device_evt)
                .map_err(|_| serde::ser::Error::custom(format!("Invalid variant {}", self.device_evt)))?;
            struct_ser.serialize_field("deviceEvt", &v)?;
        }
        if let Some(v) = self.ga_result.as_ref() {
            struct_ser.serialize_field("gaResult", v)?;
        }
        if let Some(v) = self.ota_resp.as_ref() {
            struct_ser.serialize_field("otaResp", v)?;
        }
        if let Some(v) = self.ota_data.as_ref() {
            struct_ser.serialize_field("otaData", v)?;
        }
        if let Some(v) = self.imu_data.as_ref() {
            struct_ser.serialize_field("imuData", v)?;
        }
        if let Some(v) = self.imu_resp.as_ref() {
            struct_ser.serialize_field("imuResp", v)?;
        }
        if let Some(v) = self.flex_data.as_ref() {
            struct_ser.serialize_field("flexData", v)?;
        }
        if let Some(v) = self.flex_resp.as_ref() {
            struct_ser.serialize_field("flexResp", v)?;
        }
        if let Some(v) = self.tm_data.as_ref() {
            struct_ser.serialize_field("tmData", v)?;
        }
        if let Some(v) = self.amps_data.as_ref() {
            struct_ser.serialize_field("ampsData", v)?;
        }
        struct_ser.end()
    }
}
impl<'de> serde::Deserialize<'de> for SensorApp {
    #[allow(deprecated)]
    fn deserialize<D>(deserializer: D) -> std::result::Result<Self, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        const FIELDS: &[&str] = &[
            "msg_id",
            "msgId",
            "device_info",
            "deviceInfo",
            "device_evt",
            "deviceEvt",
            "ga_result",
            "gaResult",
            "ota_resp",
            "otaResp",
            "ota_data",
            "otaData",
            "imu_data",
            "imuData",
            "imu_resp",
            "imuResp",
            "flex_data",
            "flexData",
            "flex_resp",
            "flexResp",
            "tm_data",
            "tmData",
            "amps_data",
            "ampsData",
        ];

        #[allow(clippy::enum_variant_names)]
        enum GeneratedField {
            MsgId,
            DeviceInfo,
            DeviceEvt,
            GaResult,
            OtaResp,
            OtaData,
            ImuData,
            ImuResp,
            FlexData,
            FlexResp,
            TmData,
            AmpsData,
        }
        impl<'de> serde::Deserialize<'de> for GeneratedField {
            fn deserialize<D>(deserializer: D) -> std::result::Result<GeneratedField, D::Error>
            where
                D: serde::Deserializer<'de>,
            {
                struct GeneratedVisitor;

                impl<'de> serde::de::Visitor<'de> for GeneratedVisitor {
                    type Value = GeneratedField;

                    fn expecting(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                        write!(formatter, "expected one of: {:?}", &FIELDS)
                    }

                    #[allow(unused_variables)]
                    fn visit_str<E>(self, value: &str) -> std::result::Result<GeneratedField, E>
                    where
                        E: serde::de::Error,
                    {
                        match value {
                            "msgId" | "msg_id" => Ok(GeneratedField::MsgId),
                            "deviceInfo" | "device_info" => Ok(GeneratedField::DeviceInfo),
                            "deviceEvt" | "device_evt" => Ok(GeneratedField::DeviceEvt),
                            "gaResult" | "ga_result" => Ok(GeneratedField::GaResult),
                            "otaResp" | "ota_resp" => Ok(GeneratedField::OtaResp),
                            "otaData" | "ota_data" => Ok(GeneratedField::OtaData),
                            "imuData" | "imu_data" => Ok(GeneratedField::ImuData),
                            "imuResp" | "imu_resp" => Ok(GeneratedField::ImuResp),
                            "flexData" | "flex_data" => Ok(GeneratedField::FlexData),
                            "flexResp" | "flex_resp" => Ok(GeneratedField::FlexResp),
                            "tmData" | "tm_data" => Ok(GeneratedField::TmData),
                            "ampsData" | "amps_data" => Ok(GeneratedField::AmpsData),
                            _ => Err(serde::de::Error::unknown_field(value, FIELDS)),
                        }
                    }
                }
                deserializer.deserialize_identifier(GeneratedVisitor)
            }
        }
        struct GeneratedVisitor;
        impl<'de> serde::de::Visitor<'de> for GeneratedVisitor {
            type Value = SensorApp;

            fn expecting(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                formatter.write_str("struct tech.brainco.treadmill.SensorApp")
            }

            fn visit_map<V>(self, mut map_: V) -> std::result::Result<SensorApp, V::Error>
                where
                    V: serde::de::MapAccess<'de>,
            {
                let mut msg_id__ = None;
                let mut device_info__ = None;
                let mut device_evt__ = None;
                let mut ga_result__ = None;
                let mut ota_resp__ = None;
                let mut ota_data__ = None;
                let mut imu_data__ = None;
                let mut imu_resp__ = None;
                let mut flex_data__ = None;
                let mut flex_resp__ = None;
                let mut tm_data__ = None;
                let mut amps_data__ = None;
                while let Some(k) = map_.next_key()? {
                    match k {
                        GeneratedField::MsgId => {
                            if msg_id__.is_some() {
                                return Err(serde::de::Error::duplicate_field("msgId"));
                            }
                            msg_id__ = 
                                Some(map_.next_value::<::pbjson::private::NumberDeserialize<_>>()?.0)
                            ;
                        }
                        GeneratedField::DeviceInfo => {
                            if device_info__.is_some() {
                                return Err(serde::de::Error::duplicate_field("deviceInfo"));
                            }
                            device_info__ = map_.next_value()?;
                        }
                        GeneratedField::DeviceEvt => {
                            if device_evt__.is_some() {
                                return Err(serde::de::Error::duplicate_field("deviceEvt"));
                            }
                            device_evt__ = Some(map_.next_value::<DeviceEvent>()? as i32);
                        }
                        GeneratedField::GaResult => {
                            if ga_result__.is_some() {
                                return Err(serde::de::Error::duplicate_field("gaResult"));
                            }
                            ga_result__ = map_.next_value()?;
                        }
                        GeneratedField::OtaResp => {
                            if ota_resp__.is_some() {
                                return Err(serde::de::Error::duplicate_field("otaResp"));
                            }
                            ota_resp__ = map_.next_value()?;
                        }
                        GeneratedField::OtaData => {
                            if ota_data__.is_some() {
                                return Err(serde::de::Error::duplicate_field("otaData"));
                            }
                            ota_data__ = map_.next_value()?;
                        }
                        GeneratedField::ImuData => {
                            if imu_data__.is_some() {
                                return Err(serde::de::Error::duplicate_field("imuData"));
                            }
                            imu_data__ = map_.next_value()?;
                        }
                        GeneratedField::ImuResp => {
                            if imu_resp__.is_some() {
                                return Err(serde::de::Error::duplicate_field("imuResp"));
                            }
                            imu_resp__ = map_.next_value()?;
                        }
                        GeneratedField::FlexData => {
                            if flex_data__.is_some() {
                                return Err(serde::de::Error::duplicate_field("flexData"));
                            }
                            flex_data__ = map_.next_value()?;
                        }
                        GeneratedField::FlexResp => {
                            if flex_resp__.is_some() {
                                return Err(serde::de::Error::duplicate_field("flexResp"));
                            }
                            flex_resp__ = map_.next_value()?;
                        }
                        GeneratedField::TmData => {
                            if tm_data__.is_some() {
                                return Err(serde::de::Error::duplicate_field("tmData"));
                            }
                            tm_data__ = map_.next_value()?;
                        }
                        GeneratedField::AmpsData => {
                            if amps_data__.is_some() {
                                return Err(serde::de::Error::duplicate_field("ampsData"));
                            }
                            amps_data__ = map_.next_value()?;
                        }
                    }
                }
                Ok(SensorApp {
                    msg_id: msg_id__.unwrap_or_default(),
                    device_info: device_info__,
                    device_evt: device_evt__.unwrap_or_default(),
                    ga_result: ga_result__,
                    ota_resp: ota_resp__,
                    ota_data: ota_data__,
                    imu_data: imu_data__,
                    imu_resp: imu_resp__,
                    flex_data: flex_data__,
                    flex_resp: flex_resp__,
                    tm_data: tm_data__,
                    amps_data: amps_data__,
                })
            }
        }
        deserializer.deserialize_struct("tech.brainco.treadmill.SensorApp", FIELDS, GeneratedVisitor)
    }
}
impl serde::Serialize for TreadmillData {
    #[allow(deprecated)]
    fn serialize<S>(&self, serializer: S) -> std::result::Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        use serde::ser::SerializeStruct;
        let mut len = 0;
        if self.msg_id != 0 {
            len += 1;
        }
        if self.st != 0 {
            len += 1;
        }
        if self.target_speed != 0 {
            len += 1;
        }
        if self.real_speed != 0 {
            len += 1;
        }
        if self.gradient != 0 {
            len += 1;
        }
        let mut struct_ser = serializer.serialize_struct("tech.brainco.treadmill.TreadmillData", len)?;
        if self.msg_id != 0 {
            struct_ser.serialize_field("msgId", &self.msg_id)?;
        }
        if self.st != 0 {
            let v = treadmill_data::Status::try_from(self.st)
                .map_err(|_| serde::ser::Error::custom(format!("Invalid variant {}", self.st)))?;
            struct_ser.serialize_field("st", &v)?;
        }
        if self.target_speed != 0 {
            struct_ser.serialize_field("targetSpeed", &self.target_speed)?;
        }
        if self.real_speed != 0 {
            struct_ser.serialize_field("realSpeed", &self.real_speed)?;
        }
        if self.gradient != 0 {
            struct_ser.serialize_field("gradient", &self.gradient)?;
        }
        struct_ser.end()
    }
}
impl<'de> serde::Deserialize<'de> for TreadmillData {
    #[allow(deprecated)]
    fn deserialize<D>(deserializer: D) -> std::result::Result<Self, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        const FIELDS: &[&str] = &[
            "msg_id",
            "msgId",
            "st",
            "target_speed",
            "targetSpeed",
            "real_speed",
            "realSpeed",
            "gradient",
        ];

        #[allow(clippy::enum_variant_names)]
        enum GeneratedField {
            MsgId,
            St,
            TargetSpeed,
            RealSpeed,
            Gradient,
        }
        impl<'de> serde::Deserialize<'de> for GeneratedField {
            fn deserialize<D>(deserializer: D) -> std::result::Result<GeneratedField, D::Error>
            where
                D: serde::Deserializer<'de>,
            {
                struct GeneratedVisitor;

                impl<'de> serde::de::Visitor<'de> for GeneratedVisitor {
                    type Value = GeneratedField;

                    fn expecting(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                        write!(formatter, "expected one of: {:?}", &FIELDS)
                    }

                    #[allow(unused_variables)]
                    fn visit_str<E>(self, value: &str) -> std::result::Result<GeneratedField, E>
                    where
                        E: serde::de::Error,
                    {
                        match value {
                            "msgId" | "msg_id" => Ok(GeneratedField::MsgId),
                            "st" => Ok(GeneratedField::St),
                            "targetSpeed" | "target_speed" => Ok(GeneratedField::TargetSpeed),
                            "realSpeed" | "real_speed" => Ok(GeneratedField::RealSpeed),
                            "gradient" => Ok(GeneratedField::Gradient),
                            _ => Err(serde::de::Error::unknown_field(value, FIELDS)),
                        }
                    }
                }
                deserializer.deserialize_identifier(GeneratedVisitor)
            }
        }
        struct GeneratedVisitor;
        impl<'de> serde::de::Visitor<'de> for GeneratedVisitor {
            type Value = TreadmillData;

            fn expecting(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                formatter.write_str("struct tech.brainco.treadmill.TreadmillData")
            }

            fn visit_map<V>(self, mut map_: V) -> std::result::Result<TreadmillData, V::Error>
                where
                    V: serde::de::MapAccess<'de>,
            {
                let mut msg_id__ = None;
                let mut st__ = None;
                let mut target_speed__ = None;
                let mut real_speed__ = None;
                let mut gradient__ = None;
                while let Some(k) = map_.next_key()? {
                    match k {
                        GeneratedField::MsgId => {
                            if msg_id__.is_some() {
                                return Err(serde::de::Error::duplicate_field("msgId"));
                            }
                            msg_id__ = 
                                Some(map_.next_value::<::pbjson::private::NumberDeserialize<_>>()?.0)
                            ;
                        }
                        GeneratedField::St => {
                            if st__.is_some() {
                                return Err(serde::de::Error::duplicate_field("st"));
                            }
                            st__ = Some(map_.next_value::<treadmill_data::Status>()? as i32);
                        }
                        GeneratedField::TargetSpeed => {
                            if target_speed__.is_some() {
                                return Err(serde::de::Error::duplicate_field("targetSpeed"));
                            }
                            target_speed__ = 
                                Some(map_.next_value::<::pbjson::private::NumberDeserialize<_>>()?.0)
                            ;
                        }
                        GeneratedField::RealSpeed => {
                            if real_speed__.is_some() {
                                return Err(serde::de::Error::duplicate_field("realSpeed"));
                            }
                            real_speed__ = 
                                Some(map_.next_value::<::pbjson::private::NumberDeserialize<_>>()?.0)
                            ;
                        }
                        GeneratedField::Gradient => {
                            if gradient__.is_some() {
                                return Err(serde::de::Error::duplicate_field("gradient"));
                            }
                            gradient__ = 
                                Some(map_.next_value::<::pbjson::private::NumberDeserialize<_>>()?.0)
                            ;
                        }
                    }
                }
                Ok(TreadmillData {
                    msg_id: msg_id__.unwrap_or_default(),
                    st: st__.unwrap_or_default(),
                    target_speed: target_speed__.unwrap_or_default(),
                    real_speed: real_speed__.unwrap_or_default(),
                    gradient: gradient__.unwrap_or_default(),
                })
            }
        }
        deserializer.deserialize_struct("tech.brainco.treadmill.TreadmillData", FIELDS, GeneratedVisitor)
    }
}
impl serde::Serialize for treadmill_data::Status {
    #[allow(deprecated)]
    fn serialize<S>(&self, serializer: S) -> std::result::Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        let variant = match self {
            Self::StInvalid => "ST_INVALID",
            Self::StStop => "ST_STOP",
            Self::StRun => "ST_RUN",
            Self::StDecay => "ST_DECAY",
        };
        serializer.serialize_str(variant)
    }
}
impl<'de> serde::Deserialize<'de> for treadmill_data::Status {
    #[allow(deprecated)]
    fn deserialize<D>(deserializer: D) -> std::result::Result<Self, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        const FIELDS: &[&str] = &[
            "ST_INVALID",
            "ST_STOP",
            "ST_RUN",
            "ST_DECAY",
        ];

        struct GeneratedVisitor;

        impl<'de> serde::de::Visitor<'de> for GeneratedVisitor {
            type Value = treadmill_data::Status;

            fn expecting(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(formatter, "expected one of: {:?}", &FIELDS)
            }

            fn visit_i64<E>(self, v: i64) -> std::result::Result<Self::Value, E>
            where
                E: serde::de::Error,
            {
                i32::try_from(v)
                    .ok()
                    .and_then(|x| x.try_into().ok())
                    .ok_or_else(|| {
                        serde::de::Error::invalid_value(serde::de::Unexpected::Signed(v), &self)
                    })
            }

            fn visit_u64<E>(self, v: u64) -> std::result::Result<Self::Value, E>
            where
                E: serde::de::Error,
            {
                i32::try_from(v)
                    .ok()
                    .and_then(|x| x.try_into().ok())
                    .ok_or_else(|| {
                        serde::de::Error::invalid_value(serde::de::Unexpected::Unsigned(v), &self)
                    })
            }

            fn visit_str<E>(self, value: &str) -> std::result::Result<Self::Value, E>
            where
                E: serde::de::Error,
            {
                match value {
                    "ST_INVALID" => Ok(treadmill_data::Status::StInvalid),
                    "ST_STOP" => Ok(treadmill_data::Status::StStop),
                    "ST_RUN" => Ok(treadmill_data::Status::StRun),
                    "ST_DECAY" => Ok(treadmill_data::Status::StDecay),
                    _ => Err(serde::de::Error::unknown_variant(value, FIELDS)),
                }
            }
        }
        deserializer.deserialize_any(GeneratedVisitor)
    }
}
