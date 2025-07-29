#include <stdbool.h>
#include <stdint.h>
// #include <stdlib.h>

/**
 * Calculate the CRC32 value of a memory buffer.
 *
 * @param crc accumulated CRC32 value, must be 0 on first call
 * @param buf buffer to calculate CRC32 value for
 * @param size bytes in buffer
 *
 * @return calculated CRC32 value
 */
uint32_t ef_calc_crc32(uint32_t crc, const void *buf, int size);

// 计算CRC16
unsigned short calculateCRC16(const unsigned char *data, unsigned int len);
