"""
Treadmill SDK Demo
演示使用 treadmill_sdk 库解析串口数据流
"""

import treadmill_sdk
import asyncio
import serial
import logging
from logger import getLogger
from typing import Optional

# 配置日志
logger = getLogger(logging.INFO)


class SerialReader:
    def __init__(self, port_name: str = "/dev/ttyUSB0", baudrate: int = 115200):
        self.port_name = port_name
        self.baudrate = baudrate
        self.port: Optional[serial.Serial] = None

    async def start(self):
        """启动串口读取"""
        try:
            self.port = serial.Serial(self.port_name, self.baudrate, timeout=1)
            logger.info(f"串口已打开: {self.port_name}")

            # 设置回调
            treadmill_sdk.set_abnormal_event_callback(self._on_abnormal_event)
            treadmill_sdk.set_gait_data_callback(self._on_gait_data)

            await self._read_loop()

        except serial.SerialException as e:
            logger.error(f"串口错误: {e}")
        finally:
            self.stop()

    def stop(self):
        """停止串口读取"""
        if self.port and self.port.is_open:
            self.port.close()
            logger.info("串口已关闭")

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

    async def _read_loop(self):
        """串口读取循环"""
        while True:
            try:
                if self.port and self.port.in_waiting:
                    data = self.port.read(self.port.in_waiting)
                    if data:
                        treadmill_sdk.did_receive_data(data)
                await asyncio.sleep(0.1)  # 等待新数据
            except Exception as e:
                logger.error(f"读取错误: {e}")
                break

def on_msg_resp(device_id: str, resp: str) -> None:
    """消息响应回调"""
    logger.info(f"设备 {device_id} 收到消息: {resp}")
    # 这里可以添加对消息的处理逻辑

async def main():
    """主函数"""
    treadmill_sdk.set_msg_resp_callback(on_msg_resp)

    reader = SerialReader()
    try:
        port = reader.port
        if port is None or not port.is_open:
            logger.error(f"无法打开串口: {reader.port_name}")
            return
        cmd_bytes = treadmill_sdk.get_device_info()
        print(f"设备信息cmd: {cmd_bytes}, len: {len(cmd_bytes)}")
        port.write(cmd_bytes)
        await reader.start()
    except KeyboardInterrupt:
        logger.info("程序被用户终止")
    except Exception as e:
        logger.error(f"程序异常终止: {e}")
    finally:
        reader.stop()


if __name__ == "__main__":
    asyncio.run(main())
