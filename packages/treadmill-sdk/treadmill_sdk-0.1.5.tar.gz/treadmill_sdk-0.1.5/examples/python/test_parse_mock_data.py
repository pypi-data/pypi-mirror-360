"""
Treadmill SDK Demo
演示使用 treadmill_sdk 库解析模拟数据。
"""

from typing import Final
import treadmill_sdk
import logging
from logger import getLogger

# 配置日志记录器
logger = getLogger(logging.INFO)

# 定义常量
MOCK_DATA: Final[bytes] = bytes.fromhex(
    "42524E4302131E000301A55AEDA9F18AE0157C0AFFE5F33D7F5928BE6C537DEE0C4094B7E6722656D5C49E"
    "42524E4302131F000301A55AEC A9E58AC0B96513D6251C6A2E88D7B04F5D52E9E60D4B47071B0FDF2ADCAC73"
    "42524e43021319000301a55ae6a93c9e64a197199d83e5049c78c38c95afbb0a23730d56f0f6"
    "42524e43021319000301a55ae6a93d9e64ad931966d636584986a85a55adb211f66953aa04a1"
    "42524e43021319000301a55ae6a9229e64999f1997f9d3cfcb87dfc439961e74ceeb1bd5294e"
    "42524e43021319000301a55ae6a9239e64859b19e775c6099d05dd3100354fcb5242298227f0"
    "42524e43021319000301a55ae6a9209e64f1e61846272da3d847fd6ceab5443a7af566d56b6d"
    "42524e43021319000301a55ae6a9219e64fde218bd72feff0db996ba2ab74d21afef38299f3a"
    "42524e43021319000301a55ae6a9269e64e9ee18902c54003b45429743a33ad6fa34a64e8033"
    "42524e43021319000301a55ae6a9279e64d5ea183513ccf36b3f92258942da21f5fb4d4ea88a"
    "42524e43021319000301a55ae6a9249e64c1f6182f7060d08fbe5237eabd60552e9c1d275dbb"
    "42524e43021319000301a55ae6a9259e64cdf218d425b38c5a4039e12abf694efb8643dba9ec"
    "42524e43021319000301a55ae6a92a9e64b9fe1842ee3018f6494ba8044814d64e1c4c813c87"
)


class TreadmillDataParser:
    """跑步机数据解析器"""

    def __init__(self) -> None:
        """初始化解析器并设置回调"""
        self._setup_callbacks()

    def _setup_callbacks(self) -> None:
        """设置回调函数"""
        treadmill_sdk.set_abnormal_event_callback(self._on_abnormal_event)
        treadmill_sdk.set_gait_data_callback(self._on_gait_data)

    def _on_abnormal_event(self, timestamp: int, sport_time: int, sport_id: int, event: int) -> None:
        """异常事件回调处理"""
        logger.info(
            f"检测到异常事件: timstamp: {timestamp}, sport_time: {sport_time}, "
            f"sport_id: {sport_id}, event: {event}"
        )

    def _on_gait_data(
        self, timestamp: int, sport_time: int, sport_id: int, foot: int, pattern: int, gait_duration: int, step_load: int,
    ) -> None:
        """步态数据回调处理"""
        logger.info(
            f"收到步态数据: timestamp: {timestamp}, sport_time: {sport_time}, sport_id: {sport_id}, "
            f"foot: {foot}, pattern: {pattern}, gait_duration: {gait_duration}, step_load: {step_load}"
        )

    def parse_data(self, data: bytes) -> None:
        """解析数据"""
        try:
            logger.info(f"开始解析数据: 长度={len(data)}字节")
            logger.debug(f"原始数据(hex): {data.hex()}")

            treadmill_sdk.did_receive_data(data)

        except Exception as e:
            logger.error(f"数据解析失败: {e}")
            raise


def main() -> None:
    """主函数"""
    try:
        parser = TreadmillDataParser()
        parser.parse_data(MOCK_DATA)

    except KeyboardInterrupt:
        logger.info("程序被用户终止")
    except Exception as e:
        logger.error(f"程序运行出错: {e}")
        raise


if __name__ == "__main__":
    main()
