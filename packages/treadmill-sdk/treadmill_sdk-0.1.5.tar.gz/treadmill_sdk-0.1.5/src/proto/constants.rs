pub(crate) const BUFFER_MAX_SIZE: usize = 81920;
pub(crate) const PROTO_FOOTER_CRC16: usize = 2; // CRC16
pub(crate) const PROTO_FOOTER_CRC32: usize = 4; // CRC32
                                                // pub(crate) const PROTO_MAGIC_LEN: usize = 4;
pub(crate) const PROTO_HEADER_MAGIC_BNCP: [u8; 4] = *b"BnCP"; // 定义 Header Magic
pub(crate) const PROTO_HEADER_MAGIC: [u8; 4] = *b"BRNC"; // 定义 Header Magic

pub(crate) const HEADER_VERSION_STARK: u8 = 0;
// Stark Protocol
// #define PROTO_MAGIC "BnCP"
// #define PROTO_HEADER_LEN 8 // PROTO_MAGIC + src + dst + exceptLength = 4 + 1 + 1 + 2 = 8 bytes
// #define PROTO_FOOTER_LEN 4 // CRC32 4 bytes

pub(crate) const HEADER_VERSION_V1: u8 = 1;
pub(crate) const HEADER_VERSION_V2: u8 = 2;
