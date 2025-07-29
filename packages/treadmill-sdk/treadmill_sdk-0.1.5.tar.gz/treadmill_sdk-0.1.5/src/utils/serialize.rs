pub mod serde_arc {
  use serde::{self, Deserialize, Deserializer, Serialize, Serializer};
  use std::sync::Arc;

  pub fn serialize<T, S>(arc: &Arc<T>, serializer: S) -> Result<S::Ok, S::Error>
  where
    T: Serialize,
    S: Serializer,
  {
    T::serialize(arc.as_ref(), serializer)
  }

  pub fn deserialize<'de, T, D>(deserializer: D) -> Result<Arc<T>, D::Error>
  where
    T: Deserialize<'de>,
    D: Deserializer<'de>,
  {
    let t = T::deserialize(deserializer)?;
    Ok(Arc::new(t))
  }
}
