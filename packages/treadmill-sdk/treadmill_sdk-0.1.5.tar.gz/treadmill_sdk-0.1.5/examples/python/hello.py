import logging
from logger import getLogger
from treadmill_sdk import get_bytes

logger = getLogger(logging.INFO)

data = get_bytes()
logger.info(data)
logger.info(len(data))
# logger.info(type(data))
# logger.info(isinstance(data, bytes))
# logger.info(isinstance(data, str))
# logger.info(data is None)

def parse_eeg_data(data_bytes, gain_value):
    # 解析 EEG 数据
    buffer = []
    for i in range(0, len(data_bytes), 3):
        value = int.from_bytes(data_bytes[i : i + 3], byteorder="big", signed=True)
        voltage = float(value) * (2 * 4.5 / gain_value) / (2**24)
        buffer.append(voltage)
    return buffer


# fmt: off
data_bytes = [192, 0, 0, 255, 250, 112, 255, 251, 143, 255, 251, 106, 255, 249, 76, 255, 250, 7, 255, 251, 133, 255, 251, 189, 255, 251, 16, 192, 0, 0, 181, 78, 183, 184, 0, 46, 201, 20, 83, 198, 197, 240, 186, 139, 109, 182, 99, 239, 190, 158, 216, 177, 173, 136, 192, 0, 0, 186, 61, 247, 186, 181, 139, 197, 228, 87, 185, 57, 0, 179, 43, 203, 179, 214, 159, 179, 2, 155, 176, 85, 51, 192, 0, 0, 177, 236, 222, 182, 102, 175, 211, 126, 128, 208, 20, 61, 190, 18, 242, 188, 11, 151, 224, 145, 215, 194, 152, 12]
print(parse_eeg_data(data_bytes, 1.0))
