import json
import logging
import treadmill_sdk
import treadmill_message_pb2
import treadmill_output_pb2
import google.protobuf.message
from logger import getLogger

# Configure logging
logger = getLogger(logging.DEBUG)

# Constants
PLAINTEXT = b"Hello, Device!"
msg_id = 0

test_str = "22 0D 08 4A 10 C0 CB 04 18 01 28 E8 07 50 01"
# payload_bytes from test_str
payload_bytes = bytes([0x22, 0x0D, 0x08, 0x4A, 0x10, 0xC0, 0xCB, 0x04, 0x18, 0x01, 0x28, 0xE8, 0x07, 0x50, 0x01])
# payload_bytes = bytes([34, 7, 16, 241, 117, 24, 1, 80, 1])

# 解析 protobuf
# msg = treadmill_message_pb2.SensorApp()
# try:
#     msg.ParseFromString(payload_bytes)
#     # 输出完整消息和具体字段
#     logger.info(f"Parsed message: {msg}")
# except google.protobuf.message.DecodeError as e:
#     logger.error(f"Failed to parse protobuf for decrypted {payload_bytes.hex()}: {e}")
# # print(msg)
# exit()


def gen_msg_id():
    global msg_id
    msg_id += 1
    return msg_id


class TmlMessage:
    @staticmethod
    def from_json(data):
        timestamp = data["ts"]
        if "event" in data:  # event
            event = data["event"]
            return TmlMessage(timestamp, event)

        if "left_foot" in data:
            left = data["left_foot"]
            step_duration = data["step_duration"]
            activity = 0  # data["activity"] walk or run

        return TmlMessage(timestamp, None, left, activity, step_duration)

    def __init__(
        self, timestamp, event=None, left=None, activity=None, step_duration=None
    ):
        self.timestamp = timestamp
        self.event = event
        self.left = left
        self.activity = activity
        self.step_duration = step_duration

    def __repr__(self):
        return f"timestamp: {self.timestamp}, event: {self.event}, left: {self.left}, activity: {self.activity}, step_duration: {self.step_duration}"

    def to_json_bytes(self):
        msg = treadmill_output_pb2.GaitAnalysisResult()
        msg.timestamp = self.timestamp
        if self.event is not None:
            event = 0
            if self.event == "unilateral_dragging":
                event = 3
            elif self.event == "handrail_supported":
                event = 2
            elif self.event == "no_load":
                event = 1
            msg.abnormal_gait = event
        if self.left is not None:
            msg.foot = (
                treadmill_output_pb2.GaitAnalysisResult.FootStrike.LEFT_FOOT
                if self.left
                else treadmill_output_pb2.GaitAnalysisResult.FootStrike.RIGHT_FOOT
            )
        if self.activity is not None:
            msg.pattern = (
                treadmill_output_pb2.GaitAnalysisResult.GaitPattern.GAIT_PATTERN_UNSPECIFIED
            )
        if self.step_duration is not None:
            msg.gait_duration = self.step_duration

        resp = treadmill_message_pb2.SensorApp(msg_id=gen_msg_id(), ga_result=msg)
        logger.debug(f"Message:\n {resp}")
        return resp.msg_id, resp.SerializeToString()


# 写入部分：使用字符串形式加换行符
with open("tml_mock_data.dat", "w") as f_write:  # 使用文本模式 "w"
    with open("tml_mock_data.json", "r") as f:
        data = json.load(f)
        if "data" in data:
            items = data["data"]
            for item in items:
                message = TmlMessage.from_json(item)
                logger.info(f"Message: {message}")

                msg_id, plain_bytes = message.to_json_bytes()
                # logger.debug(f"Plaintext: len={len(plain_bytes)}, hex={plain_bytes.hex()}")

                # 加密
                encrypted = treadmill_sdk.encrypt(plain_bytes)
                # 去掉前 12 字节
                encrypted = bytes(encrypted[12:])
                logger.debug(f"Encrypted: len={len(encrypted)}, hex={encrypted.hex()}")

                # 验证解密
                decrypted = treadmill_sdk.decrypt(encrypted)
                if decrypted != plain_bytes:
                    logger.error("Decryption failed")
                    break

                data = treadmill_sdk.wrap_message(encrypted)
                hex_str = data.hex()  # 转为十六进制字符串
                logger.debug(f"Wrapped: len={len(data)}, hex={hex_str}")
                f_write.write(hex_str + "\n")  # 写入字符串并加换行符

# 定义 nonce_bytes
nonce_bytes = bytes(
    [0x9D, 0x3F, 0x82, 0x68, 0x3C, 0x01, 0x66, 0x12, 0xB9, 0x19, 0xB4, 0x41]
)

# 读取部分：按文本换行符分割
with open("tml_mock_data.dat", "r") as f_read:
    lines = f_read.read().splitlines()  # 按换行符分割，去除末尾 \n
    for line in lines:
        break
        if line:  # 跳过空行
            # 将十六进制字符串转换回 bytes
            encrypted_2 = bytes.fromhex(line)
            logger.debug(f"Line: {encrypted_2.hex()}, len: {len(encrypted_2)}")

            # encrypted_2 = nonce_bytes + encrypted_2
            # 解密
            try:
                decrypted = treadmill_sdk.decrypt(KEY, encrypted_2, USER_ID, SN_CODE)
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
