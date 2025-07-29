// 内部核心实现，禁止直接调用
#[macro_export]
macro_rules! __impl_enum_conversion_inner {
    ($module:expr, $repr:ty, $name:ident, $($variant:ident = $value:expr),+ $(,)?) => {
        #[repr($repr)]
        #[cfg_attr(feature = "python", pyo3_stub_gen::derive::gen_stub_pyclass_enum)]
        #[cfg_attr(feature = "python", pyo3::pyclass(module = "treadmill_sdk", eq, eq_int))]
        #[derive(Debug, Clone, Copy, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
        pub enum $name {
            $($variant = $value),+
        }

        impl From<$repr> for $name {
            fn from(value: $repr) -> Self {
                match value {
                    $($value => $name::$variant,)+
                    _ => panic!("Invalid value for enum {}", stringify!($name))
                }
            }
        }

        impl From<$name> for $repr {
            fn from(value: $name) -> Self {
                value as $repr
            }
        }

        #[cfg(feature = "python")]
        #[cfg_attr(feature = "python", pyo3_stub_gen::derive::gen_stub_pymethods)]
        #[cfg_attr(feature = "python", pyo3::pymethods)]
        impl $name {
            #[allow(dead_code)]
            #[new]
            fn py_new(value: i64) -> Self {
                (value as $repr).into()
            }

            #[getter]
            pub fn int_value(&self) -> $repr {
                *self as $repr
            }
        }
    };
}

// === 外部宏1：默认treadmill、u8 ===
#[macro_export]
macro_rules! impl_enum_conversion {
  ($name:ident, $($variant:ident = $value:expr),+ $(,)?) => {
    $crate::__impl_enum_conversion_inner!("treadmill_sdk", u8, $name, $($variant = $value),+);
  };
}

// === 外部宏2：默认treadmill、u16 ===
#[macro_export]
macro_rules! impl_enum_u16_conversion {
  ($name:ident, $($variant:ident = $value:expr),+ $(,)?) => {
    $crate::__impl_enum_conversion_inner!("treadmill_sdk", u16, $name, $($variant = $value),+);
  };
}

// === 外部宏3：默认treadmill、u32 ===
#[macro_export]
macro_rules! impl_enum_u32_conversion {
  ($name:ident, $($variant:ident = $value:expr),+ $(,)?) => {
    $crate::__impl_enum_conversion_inner!("treadmill_sdk", u32, $name, $($variant = $value),+);
  };
}

// === 日志宏：根据特性导入不同的日志库 ===
// 该宏会根据编译时的特性配置，导入不同的日志库（tracing 或 log）
// 注意：在使用该宏之前，请确保已启用
#[macro_export]
macro_rules! cfg_import_logging {
  () => {
    cfg_if::cfg_if! {
      if #[cfg(all(feature = "tracing-log", not(target_os = "android"), not(target_family = "wasm"), not(feature = "python")))] {
        #[allow(unused_imports)]
        use tracing::*;
      } else {
        #[allow(unused_imports)]
        use log::*;
      }
    }
  };
}

// cfg_import_logging!();
