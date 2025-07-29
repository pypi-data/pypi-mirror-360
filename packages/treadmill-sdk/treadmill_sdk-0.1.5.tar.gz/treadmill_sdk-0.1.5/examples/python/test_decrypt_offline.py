import json
import logging
import treadmill_sdk
import treadmill_message_pb2
import treadmill_output_pb2
import google.protobuf.message
from logger import getLogger

# Configure logging
logger = getLogger(logging.DEBUG)

# 读取部分：按文本换行符分割
with open("sensor_app_enc_without_prefix.dat", "r") as f_read:
    lines = f_read.read().splitlines()  # 按换行符分割，去除末尾 \n
    for line in lines:
        if line:  # 跳过空行
            # 将十六进制字符串转换回 bytes
            encrypted = bytes.fromhex(line)
            logger.debug(f"Line: {encrypted.hex()}, len: {len(encrypted)}")

            # 解密
            try:
                decrypted = treadmill_sdk.decrypt(encrypted)
                logger.debug(f"Decrypted: {decrypted.hex()}, len: {len(decrypted)}")
            except Exception as e:
                logger.error(f"Decryption failed for line {line}: {e}")
                continue

            # 解析 protobuf
            msg = treadmill_message_pb2.SensorApp()
            try:
                msg.ParseFromString(decrypted)
                # 输出完整消息和具体字段
                logger.info(f"Parsed message: {msg}")
            except google.protobuf.message.DecodeError as e:
                logger.error(
                    f"Failed to parse protobuf for decrypted {decrypted.hex()}: {e}"
                )
