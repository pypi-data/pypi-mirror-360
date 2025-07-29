import sys
import struct
import os
import serial
import serial.tools.list_ports
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QFileDialog, QLineEdit,
                             QFormLayout, QComboBox, QMessageBox, QProgressBar,
                             QTextEdit, QCheckBox)  # Added QCheckBox
from PyQt5.QtCore import Qt, QTimer, QIODevice, QByteArray, QThread, pyqtSignal
from PyQt5.QtGui import QTextCursor
import time

# --- Existing Constants (L2) ---
FLASH_START_ADDR = 0x01000000
FLASH_SIZE = 0x00800000
FLASH_SAVE_ADDR = 0x01080000  # [cite: 15] Load address for PROGRAM_START
# Command Definitions (L2 - from dfu_master.c and PDF [cite: 9])
CMD_FRAME_HEADER_L = 0x44  # L2 Header Low Byte [cite: 8]
CMD_FRAME_HEADER_H = 0x47  # L2 Header High Byte [cite: 8]
GET_INFO = 0x01  # L2 Command [cite: 9]
PROGRAM_START = 0x23  # L2 Command [cite: 9]
PROGRAME_FLASH = 0x24  # L2 Command [cite: 9]
PROGRAME_END = 0x25  # L2 Command [cite: 9]
SYSTEM_INFO = 0x27  # L2 Command [cite: 9]
DFU_MODE_SET = 0x41  # (Not in PDF L2 commands, but in original script)
DFU_FW_INFO_GET = 0x42  # L2 Command [cite: 9]
ACK_SUCCESS = 0x01  # [cite: 18]
ACK_ERROR = 0x02  # [cite: 18]
DFU_VERSION = 0X02
# (Fast DFU specific command, assuming it's an L2 type if used with current ACK handling)
# If FAST_DFU_FLASH_SUCCESS is an L2 command type, it should be defined here.
# For this example, let's assume it was a typo and not used, or handled differently.
# If it's a real L2 cmd, ensure it's handled in handle_received_l2_command
# FAST_DFU_FLASH_SUCCESS = 0xXX (placeholder)


# DFU Event Definitions (Simplified based on C code)
DFU_EVENT_IDLE = 0
DFU_EVENT_CONNECTING = 1
DFU_EVENT_CONNECTED = 2
DFU_EVENT_GETTING_INFO = 3
DFU_EVENT_INFO_RECEIVED = 4
DFU_EVENT_SETTING_DFU_MODE = 5
DFU_EVENT_DFU_MODE_SET = 6
DFU_EVENT_PROGRAM_STARTING = 7
DFU_EVENT_PROGRAM_STARTED = 8
DFU_EVENT_PROGRAMMING = 9
DFU_EVENT_PROGRAM_PROGRESS = 10
DFU_EVENT_PROGRAM_END = 11
DFU_EVENT_PROGRAM_SUCCESS = 12
DFU_EVENT_DISCONNECTED = 13
DFU_EVENT_ERROR = 14
DFU_EVENT_BUSY = 15

# L2 Parsing States
CHECK_FRAME_L_STATE = 0x00
CHECK_FRAME_H_STATE = 0x01
RECEIVE_CMD_TYPE_L_STATE = 0x02
RECEIVE_CMD_TYPE_H_STATE = 0x03
RECEIVE_LEN_L_STATE = 0x04
RECEIVE_LEN_H_STATE = 0x05
RECEIVE_DATA_STATE = 0x06
RECEIVE_CHECK_SUM_L_STATE = 0x07
RECEIVE_CHECK_SUM_H_STATE = 0x08

# Structure Sizes (based on C code behavior)
SIZE_OF_BOOT_INFO_T = 32
SIZE_OF_DFU_IMG_INFO_T = 40  # Used in PROGRAM_START, matches PDF file parse [cite: 36]


class SerialReader(QThread):
    data_received = pyqtSignal(bytes)
    error_occurred = pyqtSignal(str)

    def __init__(self, serial_port):
        super().__init__()
        self._serial_port = serial_port
        self._running = True

    def run(self):
        while self._running and self._serial_port and self._serial_port.is_open:
            try:
                if self._serial_port.in_waiting > 0:
                    data = self._serial_port.read(self._serial_port.in_waiting)
                    self.data_received.emit(data)
                time.sleep(0.005)
            except serial.SerialException as e:
                self.error_occurred.emit(f"Serial Read Error: {e}")
                self._running = False
            except Exception as e:  # Catch any other unexpected error during read
                self.error_occurred.emit(f"An error occurred during serial read: {e}")
                self._running = False

    def stop(self):
        self._running = False
        self.wait()


class DfuMaster:
    # L1 Packet Constants based on image_f6cb18.png and PDF [cite: 4]
    L1_FRAME_START = b"BRNC"  # [cite: 4]
    L1_HEADER_VERSION = 0x02  # [cite: 4]
    L1_PAYLOAD_VERSION = 0x13  # For algorithm board communication [cite: 4, 6]
    L1_SRC_ID_MASTER = 0x10  # This script is the Master/APP [cite: 6]
    L1_DST_ID_SLAVE = 0x03  # The target algorithm board [cite: 6]
    L1_FLAG_DEFAULT = 0x00  # [cite: 4]
    L1_HEADER_BEFORE_PAYLOAD_LEN = 4 + 1 + 1 + 2 + 1 + 1 + 1  # BRNC to flag
    L1_CRC_FIELD_LEN = 2

    # L1 Parsing States
    _L1_STATE_WAIT_BRNC_B = 0
    _L1_STATE_WAIT_BRNC_R = 1
    _L1_STATE_WAIT_BRNC_N = 2
    _L1_STATE_WAIT_BRNC_C = 3
    _L1_STATE_RECEIVE_HEADER_V = 4
    _L1_STATE_RECEIVE_PAYLOAD_V = 5
    _L1_STATE_RECEIVE_L1_PAYLOAD_LEN_L = 6
    _L1_STATE_RECEIVE_L1_PAYLOAD_LEN_H = 7
    _L1_STATE_RECEIVE_SRC_ID = 8
    _L1_STATE_RECEIVE_DST_ID = 9
    _L1_STATE_RECEIVE_FLAG = 10
    _L1_STATE_RECEIVE_L2_FRAME_PAYLOAD = 11
    _L1_STATE_RECEIVE_L1_CRC_L = 12
    _L1_STATE_RECEIVE_L1_CRC_H = 13

    def __init__(self):
        self.serial_port = None
        self.serial_reader_thread = None

        self.once_send_size = 220
        self.receive_max_len = 2048  # Max length for L2 data field
        self.s_progress = 0
        # L1 Parsing Variables
        self._reset_l1_parser_state()

        # L2 Parsing State Variables (previously s_parse_state, etc.)
        self.s_l2_parse_state = CHECK_FRAME_L_STATE
        self.s_l2_receive_frame = {
            "cmd_type": 0,  # L2 command type
            "data_len": 0,  # L2 data field length
            "data": b"",  # L2 data field
            "check_sum": 0  # L2 checksum
        }
        self.s_l2_cmd_receive_flag = False  # Flag for L2 command successfully parsed
        self.s_l2_receive_data_count = 0  # Counter for L2 data bytes
        self.s_l2_receive_check_sum = 0  # Accumulator for L2 checksum calculation

        # DFU Process Variables (remain L2/application specific)
        self.firmware_data = None
        self.img_info = {}
        self.s_file_size = 0
        self.s_all_check_sum = 0  # Checksum of the programmed data (L2 PROGRAME_END)
        self.program_size = 0
        self.fast_dfu_mode = 0
        self.s_run_fw_flag = True
        self.s_dfu_save_addr = 0
        self.s_bootloader_boot_info = {}
        self.s_app_info = {}
        self.s_sec_flag = False
        self.s_version_flag = False

        self.event_callback = None
        self.dfu_in_progress = False

    def _reset_l1_parser_state(self):
        self.s_l1_parse_state = self._L1_STATE_WAIT_BRNC_B
        self.s_l1_received_buffer = bytearray()
        self.s_l1_received_payload_len = 0  # This will store L1's payload_length (i.e., L2 frame length)
        self.s_l1_current_l2_payload_bytes_count = 0

    def set_event_callback(self, callback):
        self.event_callback = callback

    def emit_event(self, event, progress=0, message=""):
        if self.event_callback:
            self.event_callback(event, progress, message)

    def connect(self, port, baudrate):
        if self.serial_port and self.serial_port.is_open:
            self.disconnect()
        try:
            self.serial_port = serial.Serial(port, baudrate, timeout=0.05)
            self.emit_event(DFU_EVENT_CONNECTED, message=f"Connected to {port}")
            self.serial_reader_thread = SerialReader(self.serial_port)
            self.serial_reader_thread.data_received.connect(self.handle_serial_data)  # Entry point for L1 parsing
            self.serial_reader_thread.error_occurred.connect(lambda err: self.emit_event(DFU_EVENT_ERROR, message=err))
            self.serial_reader_thread.start()
            self._reset_l1_parser_state()  # Reset parser on new connection
            self.s_l2_parse_state = CHECK_FRAME_L_STATE  # Reset L2 parser too
            return True
        except serial.SerialException as e:
            self.emit_event(DFU_EVENT_ERROR, message=f"Serial Connection Error: {e}")
            return False
        except Exception as e:
            self.emit_event(DFU_EVENT_ERROR, message=f"An unexpected error occurred during connection: {e}")
            return False

    def disconnect(self):
        if self.dfu_in_progress:
            self.emit_event(DFU_EVENT_ERROR, message="DFU in progress, forcing disconnect.")
            self.dfu_in_progress = False
        if self.serial_reader_thread:
            self.serial_reader_thread.stop()
            self.serial_reader_thread = None
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            self.emit_event(DFU_EVENT_DISCONNECTED, message="Disconnected")
        self.serial_port = None

    def _crc16_xmodem(self, data):  # For L1 CRC [cite: 6]
        crc = 0x0000
        poly = 0x1021  # Standard XMODEM polynomial
        for byte in data:
            crc ^= (byte << 8)
            for _ in range(8):
                if crc & 0x8000:
                    crc = (crc << 1) ^ poly
                else:
                    crc <<= 1
        return crc & 0xFFFF

    def _calculate_l2_checksum(self, data):  # Original checksum for L2
        checksum = sum(data)
        return checksum & 0xFFFF

    def _construct_l2_frame(self, cmd_type, data=b""):  # Renamed from construct_frame
        header = struct.pack("<BB", CMD_FRAME_HEADER_L, CMD_FRAME_HEADER_H)  # L2 Header: 0x44 0x47 [cite: 8]
        cmd_type_packed = struct.pack("<H", cmd_type)  # L2 cmd_type [cite: 8]
        data_len_packed = struct.pack("<H", len(data))  # L2 data length [cite: 8]

        # L2 checksum is calculated over cmd_type, data_len, and data
        checksum_data = cmd_type_packed + data_len_packed + data
        checksum = self._calculate_l2_checksum(checksum_data)  # L2 simple sum checksum
        checksum_packed = struct.pack("<H", checksum)

        l2_frame = header + checksum_data + checksum_packed
        return l2_frame

    def _construct_l1_frame(self, l2_frame_payload):
        l1_payload_actual_len = len(l2_frame_payload)  # This is the length of the L2 frame

        # L1 Fields [cite: 4]
        frame_start = self.L1_FRAME_START
        header_version_byte = struct.pack("<B", self.L1_HEADER_VERSION)
        payload_version_byte = struct.pack("<B", self.L1_PAYLOAD_VERSION)
        payload_length_bytes = struct.pack("<H", l1_payload_actual_len)  # Little-endian length of L2 frame
        src_id_byte = struct.pack("<B", self.L1_SRC_ID_MASTER)  # Master sending
        dst_id_byte = struct.pack("<B", self.L1_DST_ID_SLAVE)  # To slave
        flag_byte = struct.pack("<B", self.L1_FLAG_DEFAULT)

        # Data for L1 CRC calculation: (header_version to l2_frame_payload inclusive) [cite: 4, 6]
        data_for_l1_crc = (
                frame_start +
                header_version_byte +
                payload_version_byte +
                payload_length_bytes +
                src_id_byte +
                dst_id_byte +
                flag_byte +
                l2_frame_payload
        )
        l1_crc_val = self._crc16_xmodem(data_for_l1_crc)
        l1_crc_bytes = struct.pack("<H", l1_crc_val)  # Assuming little-endian for CRC too

        # Construct final L1 frame
        l1_frame = data_for_l1_crc + l1_crc_bytes
        return l1_frame

    def send_command(self, l2_cmd_type, l2_data=b""):  # l2_cmd_type and l2_data are for L2
        if not self.serial_port or not self.serial_port.is_open:
            self.emit_event(DFU_EVENT_ERROR, message="Serial port not connected. L1/L2 Command not sent.")
            return False
        try:
            l2_frame = self._construct_l2_frame(l2_cmd_type, l2_data)
            l1_frame = self._construct_l1_frame(l2_frame)
            print(f"Sending L1 (L2 Cmd: 0x{l2_cmd_type:02X}): {', '.join([f'0x{b:02X}' for b in l1_frame])}")
            self.serial_port.write(l1_frame)
            return True
        except serial.SerialException as e:
            self.emit_event(DFU_EVENT_ERROR, message=f"Serial Write Error: {e}")
            self.disconnect()  # Disconnect on serial write error
            return False
        except Exception as e:
            self.emit_event(DFU_EVENT_ERROR, message=f"Error sending L1/L2 command: {e}")
            return False

    # This is the new L1 parser entry point
    def handle_serial_data(self, data):
        for byte_val in data:
            self._parse_l1_byte(byte_val)

    def _parse_l1_byte(self, byte_val):
        # print(f"L1 State: {self.s_l1_parse_state}, Byte: {hex(byte_val)}") # Debug
        if self.s_l1_parse_state == self._L1_STATE_WAIT_BRNC_B:
            if byte_val == self.L1_FRAME_START[0]:  # 'B'
                self.s_l1_received_buffer.append(byte_val)
                self.s_l1_parse_state = self._L1_STATE_WAIT_BRNC_R
            # else: Discard byte, wait for 'B'
        elif self.s_l1_parse_state == self._L1_STATE_WAIT_BRNC_R:
            if byte_val == self.L1_FRAME_START[1]:  # 'R'
                self.s_l1_received_buffer.append(byte_val)
                self.s_l1_parse_state = self._L1_STATE_WAIT_BRNC_N
            else:
                self._reset_l1_parser_state()  # Sync error
        elif self.s_l1_parse_state == self._L1_STATE_WAIT_BRNC_N:
            if byte_val == self.L1_FRAME_START[2]:  # 'N'
                self.s_l1_received_buffer.append(byte_val)
                self.s_l1_parse_state = self._L1_STATE_WAIT_BRNC_C
            else:
                self._reset_l1_parser_state()
        elif self.s_l1_parse_state == self._L1_STATE_WAIT_BRNC_C:
            if byte_val == self.L1_FRAME_START[3]:  # 'C'
                self.s_l1_received_buffer.append(byte_val)
                self.s_l1_parse_state = self._L1_STATE_RECEIVE_HEADER_V
            else:
                self._reset_l1_parser_state()

        elif self.s_l1_parse_state == self._L1_STATE_RECEIVE_HEADER_V:
            self.s_l1_received_buffer.append(byte_val)
            if byte_val != self.L1_HEADER_VERSION:  # [cite: 4]
                self.emit_event(DFU_EVENT_ERROR, message=f"L1: Invalid header_version {hex(byte_val)}")
                self._reset_l1_parser_state()
                return
            self.s_l1_parse_state = self._L1_STATE_RECEIVE_PAYLOAD_V

        elif self.s_l1_parse_state == self._L1_STATE_RECEIVE_PAYLOAD_V:
            self.s_l1_received_buffer.append(byte_val)
            if byte_val != self.L1_PAYLOAD_VERSION:  # [cite: 4, 6]
                self.emit_event(DFU_EVENT_ERROR, message=f"L1: Invalid payload_version {hex(byte_val)}")
                self._reset_l1_parser_state()
                return
            self.s_l1_parse_state = self._L1_STATE_RECEIVE_L1_PAYLOAD_LEN_L

        elif self.s_l1_parse_state == self._L1_STATE_RECEIVE_L1_PAYLOAD_LEN_L:
            self.s_l1_received_buffer.append(byte_val)
            self.s_l1_received_payload_len = byte_val  # LSB of L1 payload length [cite: 4]
            self.s_l1_parse_state = self._L1_STATE_RECEIVE_L1_PAYLOAD_LEN_H

        elif self.s_l1_parse_state == self._L1_STATE_RECEIVE_L1_PAYLOAD_LEN_H:
            self.s_l1_received_buffer.append(byte_val)
            self.s_l1_received_payload_len |= (byte_val << 8)  # MSB of L1 payload length [cite: 4]
            # L1 payload_length is the length of the entire L2 frame.
            # Max L2 data is self.receive_max_len. L2 overhead is 8 bytes (2+2+2+2).
            if self.s_l1_received_payload_len > (self.receive_max_len + 8 + 20):  # Allow some buffer
                self.emit_event(DFU_EVENT_ERROR,
                                message=f"L1: L2 frame length too large: {self.s_l1_received_payload_len}")
                self._reset_l1_parser_state()
                return
            self.s_l1_parse_state = self._L1_STATE_RECEIVE_SRC_ID

        elif self.s_l1_parse_state == self._L1_STATE_RECEIVE_SRC_ID:
            self.s_l1_received_buffer.append(byte_val)  # Received L1 src_id [cite: 4]
            # For master, expected src_id from slave would be L1_DST_ID_SLAVE (0x03)
            if byte_val != self.L1_DST_ID_SLAVE:
                self.emit_event(DFU_EVENT_ERROR, message=f"L1: Unexpected SRC_ID {hex(byte_val)} from slave.")
                # self._reset_l1_parser_state() # Or just log and continue, depending on strictness
            self.s_l1_parse_state = self._L1_STATE_RECEIVE_DST_ID

        elif self.s_l1_parse_state == self._L1_STATE_RECEIVE_DST_ID:
            self.s_l1_received_buffer.append(byte_val)  # Received L1 dst_id [cite: 4]
            if byte_val != self.L1_SRC_ID_MASTER:  # Frame must be destined for us (Master) [cite: 6]
                self.emit_event(DFU_EVENT_ERROR, message=f"L1: Frame not for this master. DST_ID: {hex(byte_val)}")
                self._reset_l1_parser_state()
                return
            self.s_l1_parse_state = self._L1_STATE_RECEIVE_FLAG

        elif self.s_l1_parse_state == self._L1_STATE_RECEIVE_FLAG:
            self.s_l1_received_buffer.append(byte_val)  # L1 flag [cite: 4]
            self.s_l1_current_l2_payload_bytes_count = 0  # Reset for L2 frame payload
            if self.s_l1_received_payload_len == 0:  # No L2 frame payload
                self.s_l1_parse_state = self._L1_STATE_RECEIVE_L1_CRC_L
            else:
                self.s_l1_parse_state = self._L1_STATE_RECEIVE_L2_FRAME_PAYLOAD

        elif self.s_l1_parse_state == self._L1_STATE_RECEIVE_L2_FRAME_PAYLOAD:
            self.s_l1_received_buffer.append(byte_val)
            self.s_l1_current_l2_payload_bytes_count += 1
            if self.s_l1_current_l2_payload_bytes_count == self.s_l1_received_payload_len:
                self.s_l1_parse_state = self._L1_STATE_RECEIVE_L1_CRC_L

        elif self.s_l1_parse_state == self._L1_STATE_RECEIVE_L1_CRC_L:
            self.s_l1_received_buffer.append(byte_val)  # L1 CRC LSB
            self.s_l1_parse_state = self._L1_STATE_RECEIVE_L1_CRC_H

        elif self.s_l1_parse_state == self._L1_STATE_RECEIVE_L1_CRC_H:
            self.s_l1_received_buffer.append(byte_val)  # L1 CRC MSB
            self._process_received_l1_frame()  # Full L1 frame received
            self._reset_l1_parser_state()  # Reset for next L1 frame
        else:  # Should not happen
            self._reset_l1_parser_state()

    def _process_received_l1_frame(self):
        # s_l1_received_buffer contains the full L1 frame:
        # BRNC (4) + HVer(1) + PVer(1) + PLen(2) + Src(1) + Dst(1) + Flag(1) + L2Frame(PLen) + CRC(2)

        # Extract received L1 CRC (last 2 bytes)
        received_l1_crc_bytes = self.s_l1_received_buffer[-self.L1_CRC_FIELD_LEN:]
        received_l1_crc = struct.unpack("<H", received_l1_crc_bytes)[0]

        # Data for L1 CRC check starts after "BRNC" (4 bytes) and ends before L1 CRC field
        data_for_l1_crc_check = self.s_l1_received_buffer[0: -self.L1_CRC_FIELD_LEN]

        calculated_l1_crc = self._crc16_xmodem(data_for_l1_crc_check)

        # print(f"L1 RX: {self.s_l1_received_buffer.hex().upper()}") # Debug
        # print(f"L1 CRC Data: {data_for_l1_crc_check.hex().upper()}") # Debug
        # print(f"L1 RX CRC: {hex(received_l1_crc)}, Calc CRC: {hex(calculated_l1_crc)}") # Debug

        if calculated_l1_crc == received_l1_crc:
            # L1 CRC OK. Extract L2 frame payload.
            # L2 frame starts after L1 fixed header (BRNC to Flag)
            l2_frame_start_index = self.L1_HEADER_BEFORE_PAYLOAD_LEN
            l2_frame_end_index = l2_frame_start_index + self.s_l1_received_payload_len
            l2_frame_data = self.s_l1_received_buffer[l2_frame_start_index: l2_frame_end_index]

            # print(f"L1 CRC OK. Processing L2 frame: {l2_frame_data.hex().upper()}") # Debug

            # Reset L2 parser state before processing new L2 frame
            self.s_l2_parse_state = CHECK_FRAME_L_STATE
            self.s_l2_receive_frame = {"cmd_type": 0, "data_len": 0, "data": b"", "check_sum": 0}
            self.s_l2_receive_check_sum = 0
            self.s_l2_receive_data_count = 0

            for l2_byte_val in l2_frame_data:
                self._parse_l2_byte(l2_byte_val)  # Feed to L2 parser
        else:
            self.emit_event(DFU_EVENT_ERROR,
                            message=f"L1 CRC Mismatch! Expected {hex(calculated_l1_crc)}, Got {hex(received_l1_crc)}")

    # This is the L2 parser (original handle_serial_data logic)
    def _parse_l2_byte(self, byte_int):
        # print(f"L2 State: {self.s_l2_parse_state}, Byte: {hex(byte_int)}") # Debug
        if self.s_l2_parse_state == CHECK_FRAME_L_STATE:  # L2 Header Byte 1 (0x44)
            self.s_l2_receive_check_sum = 0
            self.s_l2_receive_data_count = 0
            self.s_l2_receive_frame["data"] = bytearray()
            if byte_int == CMD_FRAME_HEADER_L:
                self.s_l2_parse_state = CHECK_FRAME_H_STATE
            # else: remain in state, L2 sync error, wait for 0x44
        elif self.s_l2_parse_state == CHECK_FRAME_H_STATE:  # L2 Header Byte 2 (0x47)
            if byte_int == CMD_FRAME_HEADER_H:
                self.s_l2_parse_state = RECEIVE_CMD_TYPE_L_STATE
            elif byte_int == CMD_FRAME_HEADER_L:  # Another 0x44, re-sync
                pass  # Stay in CHECK_FRAME_H_STATE waiting for 0x47
            else:  # L2 sync error
                self.s_l2_parse_state = CHECK_FRAME_L_STATE
        elif self.s_l2_parse_state == RECEIVE_CMD_TYPE_L_STATE:
            self.s_l2_receive_frame["cmd_type"] = byte_int
            self.s_l2_receive_check_sum += byte_int
            self.s_l2_parse_state = RECEIVE_CMD_TYPE_H_STATE
        elif self.s_l2_parse_state == RECEIVE_CMD_TYPE_H_STATE:
            self.s_l2_receive_frame["cmd_type"] |= (byte_int << 8)
            self.s_l2_receive_check_sum += byte_int
            self.s_l2_parse_state = RECEIVE_LEN_L_STATE
        elif self.s_l2_parse_state == RECEIVE_LEN_L_STATE:  # L2 Data Length LSB
            self.s_l2_receive_frame["data_len"] = byte_int
            self.s_l2_receive_check_sum += byte_int
            self.s_l2_parse_state = RECEIVE_LEN_H_STATE
        elif self.s_l2_parse_state == RECEIVE_LEN_H_STATE:  # L2 Data Length MSB
            self.s_l2_receive_frame["data_len"] |= (byte_int << 8)
            self.s_l2_receive_check_sum += byte_int
            if self.s_l2_receive_frame["data_len"] == 0:
                self.s_l2_parse_state = RECEIVE_CHECK_SUM_L_STATE
            elif self.s_l2_receive_frame["data_len"] > self.receive_max_len:  # Max L2 data field length
                self.emit_event(DFU_EVENT_ERROR,
                                message=f"L2 Data length too large: {self.s_l2_receive_frame['data_len']}")
                self.s_l2_parse_state = CHECK_FRAME_L_STATE
            else:
                self.s_l2_receive_frame["data"] = bytearray(
                    self.s_l2_receive_frame["data_len"])  # Prepare buffer for L2 data
                self.s_l2_receive_data_count = 0
                self.s_l2_parse_state = RECEIVE_DATA_STATE
        elif self.s_l2_parse_state == RECEIVE_DATA_STATE:  # L2 Data Field
            if self.s_l2_receive_data_count < self.s_l2_receive_frame["data_len"]:
                self.s_l2_receive_frame["data"][self.s_l2_receive_data_count] = byte_int
                self.s_l2_receive_check_sum += byte_int
                self.s_l2_receive_data_count += 1
                if self.s_l2_receive_data_count == self.s_l2_receive_frame["data_len"]:
                    self.s_l2_parse_state = RECEIVE_CHECK_SUM_L_STATE
            else:  # Should not happen given the length check
                self.emit_event(DFU_EVENT_ERROR, message="L2 Data reception overflow.")
                self.s_l2_parse_state = CHECK_FRAME_L_STATE
        elif self.s_l2_parse_state == RECEIVE_CHECK_SUM_L_STATE:  # L2 Checksum LSB
            self.s_l2_receive_frame["check_sum"] = byte_int
            self.s_l2_parse_state = RECEIVE_CHECK_SUM_H_STATE
        elif self.s_l2_parse_state == RECEIVE_CHECK_SUM_H_STATE:  # L2 Checksum MSB
            self.s_l2_receive_frame["check_sum"] |= (byte_int << 8)
            self._check_and_handle_l2_command()  # Validate and process L2 command
            self.s_l2_parse_state = CHECK_FRAME_L_STATE  # Reset L2 parser for next L2 frame

    def _check_and_handle_l2_command(self):  # Renamed from check_and_handle_command
        # print(f"L2 RX Frame: Cmd=0x{self.s_l2_receive_frame['cmd_type']:04X}, Len={self.s_l2_receive_frame['data_len']}, SumRcv=0x{self.s_l2_receive_frame['check_sum']:04X}, SumCalc=0x{(self.s_l2_receive_check_sum & 0xffff):04X}") # Debug
        if (self.s_l2_receive_check_sum & 0xffff) == self.s_l2_receive_frame["check_sum"]:
            self.s_l2_cmd_receive_flag = True  # May not be strictly needed anymore
            self._handle_received_l2_command()
        else:
            self.s_l2_cmd_receive_flag = False
            self.emit_event(DFU_EVENT_ERROR,
                            message=f"L2 Checksum error for L2 cmd 0x{self.s_l2_receive_frame['cmd_type']:04X}. Expected {self.s_l2_receive_frame['check_sum']:04X}, Got {(self.s_l2_receive_check_sum & 0xffff):04X}")

    def _handle_received_l2_command(self):  # Renamed from handle_received_command
        cmd_type = self.s_l2_receive_frame["cmd_type"]
        data = bytes(self.s_l2_receive_frame["data"])  # Convert L2 data to bytes
        ack_status = data[0] if len(data) > 0 else None
        # print(f"Handling L2 Command: 0x{cmd_type:04X}, ACK Status: {ack_status}, Data: {data.hex()}") # Debug

        # --- ALL ORIGINAL L2 COMMAND HANDLING LOGIC GOES HERE ---
        # (GET_INFO, PROGRAM_START, DFU_FW_INFO_GET, SYSTEM_INFO, etc.)
        # No changes needed inside this L2 command handling logic itself,
        # as it operates on L2 commands and data.

        if cmd_type == GET_INFO:
            if ack_status == ACK_SUCCESS:
                self.emit_event(DFU_EVENT_INFO_RECEIVED, message="L2: Received GET_INFO response.")
                if len(data) > 17:
                    dfu_version = data[17]
                    self.s_version_flag = (dfu_version == DFU_VERSION)
                    self.emit_event(DFU_EVENT_INFO_RECEIVED, message=f"Slave DFU Version: {dfu_version}")
                if len(data) >= 8 + SIZE_OF_BOOT_INFO_T:
                    boot_info_data = data[8:8 + SIZE_OF_BOOT_INFO_T]
                    try:
                        self.s_bootloader_boot_info["load_addr"] = struct.unpack_from("<I", boot_info_data, 8)[0]
                        self.s_bootloader_boot_info["bin_size"] = struct.unpack_from("<I", boot_info_data, 0)[0]
                        self.emit_event(DFU_EVENT_INFO_RECEIVED,
                                        message=f"Slave Bootloader Addr: 0x{self.s_bootloader_boot_info.get('load_addr', 0):08X}, Size: {self.s_bootloader_boot_info.get('bin_size', 0)}")
                    except Exception as e:
                        self.emit_event(DFU_EVENT_ERROR, message=f"Error parsing slave bootloader info: {e}")
                if self.s_version_flag:  # New DFU Version
                    self.emit_event(DFU_EVENT_GETTING_INFO, message="L2: Getting DFU Firmware Info...")
                    self.dfu_fw_info_get()
                else:  # Old DFU Version
                    self.emit_event(DFU_EVENT_GETTING_INFO, message="L2: Getting System Info (Old Version)...")
                    self.system_info_get()
            else:
                self.emit_event(DFU_EVENT_ERROR, message="L2: GET_INFO command failed.")
                self.disconnect()

        elif cmd_type == DFU_FW_INFO_GET:  # [cite: 9]
            if ack_status == ACK_SUCCESS:
                self.emit_event(DFU_EVENT_INFO_RECEIVED, message="L2: Received DFU_FW_INFO_GET response.")
                # Response format for 0x42 is detailed in PDF (slave->master) [cite: 31, 33]
                # data[0] is ACK status.
                # data[1-4] is copy_addr (0x1080000)
                # data[5] is fw_flag (0x01)
                # data[6-45] is dfu_img_info_t (40 bytes)
                if len(data) >= 1 + 4 + 1 + SIZE_OF_DFU_IMG_INFO_T:  # 1 (ack) + 4 (addr) + 1 (flag) + 40 (img_info)
                    self.s_dfu_save_addr = struct.unpack_from("<I", data, 1)[0]  # [cite: 33]
                    # Verify s_dfu_save_addr, e.g. FLASH_SAVE_ADDR
                    if self.s_dfu_save_addr != FLASH_SAVE_ADDR:
                        self.emit_event(DFU_EVENT_ERROR,
                                        message=f"L2: DFU_FW_INFO_GET save_addr mismatch. Expected {FLASH_SAVE_ADDR:08X}, got {self.s_dfu_save_addr:08X}")
                        # self.disconnect() # Or handle as warning

                    app_info_data = data[6: 6 + SIZE_OF_DFU_IMG_INFO_T]
                    try:
                        # Parse app_info (dfu_img_info_t from slave) [cite: 33]
                        self.s_app_info["pattern"] = struct.unpack_from("<H", app_info_data, 0)[
                            0]  # offset 0 in 40B struct [cite: 39] (matches "信息类型" 0x44 0x47)
                        self.s_app_info["version"] = struct.unpack_from("<H", app_info_data, 2)[
                            0]  # offset 2 [cite: 39]

                        # boot_info is at offset 4 within dfu_img_info_t (size 32)
                        # For DFU_FW_INFO_GET response, the offsets from PDF for 0x23 request are used.
                        # Fields like "固件大小", "校验和", "加载地址", "运行地址", "xip控制命令", "option", "固件名称"
                        # are part of the 40-byte structure.
                        # Example from PDF[cite: 33]:
                        # boot_info_app_data = app_info_data[4:4+SIZE_OF_BOOT_INFO_T] # This was from GR551x SDK assumption
                        # For Evorun:
                        self.s_app_info["bin_size"] = struct.unpack_from("<I", app_info_data, 4)[
                            0]  # "固件大小" [cite: 39] (offset 4-7 in 40B)
                        self.s_app_info["load_addr"] = struct.unpack_from("<I", app_info_data, 12)[
                            0]  # "加载地址" [cite: 39] (offset 12-15 in 40B)
                        # The original script compared local file info's load_addr with slave's app_info load_addr
                        # For Evorun, the "加载地址" in the DFU_FW_INFO_GET response refers to the *currently running* app's load_addr.
                        # The DFU save address is FLASH_SAVE_ADDR (0x01080000) [cite: 15, 20, 33]

                        self.s_app_info["comments"] = app_info_data[28:40].split(b'\x00')[0].decode('ascii',
                                                                                                    errors='ignore')  # "固件名称" [cite: 41] (offset 28-39 in 40B)

                        self.emit_event(DFU_EVENT_INFO_RECEIVED,
                                        message=f"Slave DFU Save Addr: 0x{self.s_dfu_save_addr:08X}")
                        self.emit_event(DFU_EVENT_INFO_RECEIVED,
                                        message=f"Slave App Current Load Addr: 0x{self.s_app_info.get('load_addr', 0):08X}, Size: {self.s_app_info.get('bin_size', 0)}, Name: {self.s_app_info.get('comments', 'N/A')}")

                        # Address conflict check (Simplified based on original script logic)
                        # This should ideally compare the *new* firmware's region (FLASH_SAVE_ADDR to FLASH_SAVE_ADDR + new_fw_size)
                        # with the *slave's bootloader* region.
                        # The original script had more complex logic with PADDING, which might be GR551x specific.
                        # For Evorun, the key is not to overwrite the bootloader.
                        conflict = False
                        slave_boot_start = self.s_bootloader_boot_info.get('load_addr', 0)  # From GET_INFO
                        slave_boot_size = self.s_bootloader_boot_info.get('bin_size', 0)
                        new_fw_start = FLASH_SAVE_ADDR
                        new_fw_size = self.img_info.get('bin_size', 0)  # From local file to be flashed

                        if slave_boot_start > 0 and new_fw_start < slave_boot_start + slave_boot_size and \
                                new_fw_start + new_fw_size > slave_boot_start:
                            conflict = True
                            self.emit_event(DFU_EVENT_ERROR, message="DFU save address conflict with slave bootloader.")
                            self.disconnect()

                        if not conflict:
                            self.emit_event(DFU_EVENT_PROGRAM_STARTING,
                                            message="L2: Starting Program (Evorun)...")  # Changed from SETTING_DFU_MODE
                            # According to Evorun PDF flowchart[cite: 35], after 0x42, decide if upgrade needed, then 0x23.
                            # The original script went to dfu_mode_set. Evorun does not have DFU_MODE_SET cmd.
                            # We proceed to PROGRAM_START (0x23)
                            self.program_start_evorun()  # Use the Evorun specific program_start
                    except Exception as e:
                        self.emit_event(DFU_EVENT_ERROR, message=f"Error parsing slave DFU firmware info (0x42): {e}")
                        self.disconnect()
                else:
                    self.emit_event(DFU_EVENT_ERROR, message="L2: DFU_FW_INFO_GET response too short.")
                    self.disconnect()
            else:
                self.emit_event(DFU_EVENT_ERROR, message="L2: DFU_FW_INFO_GET command failed.")
                self.disconnect()

        elif cmd_type == SYSTEM_INFO:  # 0x27, old DFU path or for specific info
            if ack_status == ACK_SUCCESS:
                self.emit_event(DFU_EVENT_INFO_RECEIVED, message="L2: Received SYSTEM_INFO response.")
                # Parse system information (security status, bootloader info)
                # data[0] is ack. PDF for 0x27 response structure is not fully detailed, but implies boot info
                if len(data) > 1:  # Placeholder for security flag if it were here
                    # self.s_sec_flag = bool(data[1])
                    # self.emit_event(DFU_EVENT_INFO_RECEIVED, message=f"Slave Security Enabled: {self.s_sec_flag}")
                    pass

                # Assuming the response contains boot_info_t after ack, similar to GET_INFO
                # This part needs clarification from Evorun spec if 0x27 response differs from GET_INFO significantly
                if len(data) >= 1 + 8 + SIZE_OF_BOOT_INFO_T:  # ack + possible offset + boot_info
                    # For now, assume boot_info_data starts after some offset (e.g. 1 for ACK, 8 like in GET_INFO)
                    # This is a guess; PDF doesn't detail 0x27 response structure beyond "Normal data return"
                    # Let's assume data[1:] might contain fields similar to other info commands.
                    # If GET_INFO already provides bootloader info, this might be redundant or for other system params.
                    # For now, we rely on GET_INFO for bootloader info.
                    # If Evorun's old path (s_version_flag=False) uses 0x27 and then needs bootloader info,
                    # it should be parsed here.
                    # boot_info_data = data[1+8 : 1+8+SIZE_OF_BOOT_INFO_T]
                    # try:
                    #    self.s_bootloader_boot_info["load_addr"] = struct.unpack_from("<I", boot_info_data, 0)[0]
                    #    self.s_bootloader_boot_info["bin_size"] = struct.unpack_from("<I", boot_info_data, 4)[0]
                    #    self.emit_event(DFU_EVENT_INFO_RECEIVED, message=f"Slave Bootloader Addr (from SYS_INFO): 0x{self.s_bootloader_boot_info.get('load_addr', 0):08X}, Size: {self.s_bootloader_boot_info.get('bin_size', 0)}")
                    # except Exception as e:
                    #     self.emit_event(DFU_EVENT_ERROR, message=f"Error parsing slave bootloader info (SYSTEM_INFO): {e}")
                    pass

                # After SYSTEM_INFO (old path), typically proceed to PROGRAM_START
                self.emit_event(DFU_EVENT_PROGRAM_STARTING,
                                message="L2: Starting Program (Old DFU Path via SYS_INFO)...")
                self.program_start_evorun()  # Use Evorun specific program_start

            else:
                self.emit_event(DFU_EVENT_ERROR, message="L2: SYSTEM_INFO command failed.")
                self.disconnect()

        # DFU_MODE_SET is not in Evorun PDF. If it was specific to GR551x, it's removed from Evorun flow.
        # elif cmd_type == DFU_MODE_SET:
        #     ...

        elif cmd_type == PROGRAM_START:  # 0x23 [cite: 9]
            if ack_status == ACK_SUCCESS:  # [cite: 18]
                self.emit_event(DFU_EVENT_PROGRAM_STARTED, message="L2: PROGRAM_START Acknowledged.")
                # Evorun PDF for 0x23 response is just ACK[cite: 18]. No fast DFU status here.
                # Original script had fast_dfu_mode logic here. Evorun doesn't specify fast DFU mode.
                # Assume normal DFU flow: start sending flash chunks.
                self.program_size = 0
                self.s_all_check_sum = 0  # Checksum for PROGRAME_END [cite: 25]
                self.emit_event(DFU_EVENT_PROGRAMMING, message="L2: Starting Flash Programming...")
                self.send_next_flash_chunk_evorun()
            else:  # ACK_ERROR or other
                error_message = "L2: PROGRAM_START (0x23) command failed."
                self.emit_event(DFU_EVENT_ERROR, message=error_message)
                self.disconnect()

        elif cmd_type == PROGRAME_FLASH:  # 0x24 [cite: 9]
            if ack_status == ACK_SUCCESS:  # [cite: 22]
                progress = 0
                if self.s_file_size > 0:  # s_file_size should be from local file's dfu_img_info.bin_size
                    progress = int((self.program_size / self.s_file_size) * 100)
                if self.s_progress != progress:
                    self.emit_event(DFU_EVENT_PROGRAM_PROGRESS, progress=progress, message=f"Programming... {progress}%")
                    self.s_progress = progress

                if self.program_size < self.s_file_size:
                    self.send_next_flash_chunk_evorun()
                else:  # All chunks sent
                    self.emit_event(DFU_EVENT_PROGRAM_END, message="L2: Programming Complete, Finalizing...")
                    self.programe_end_evorun()  # run_fw flag is handled by s_run_fw_flag in programe_end
            else:
                self.emit_event(DFU_EVENT_ERROR, message="L2: PROGRAME_FLASH (0x24) command failed.")
                self.disconnect()

        # FAST_DFU_FLASH_SUCCESS was GR551x specific, not in Evorun PDF for 0x24 ACK.
        # elif cmd_type == FAST_DFU_FLASH_SUCCESS:
        #    ...

        elif cmd_type == PROGRAME_END:  # 0x25 [cite: 9]
            if ack_status == ACK_SUCCESS:  # [cite: 27]
                # Evorun PROGRAME_END response is just ACK. No checksum returned from slave. [cite: 27]
                # The checksum sent *to* slave in 0x25 request is the firmware file checksum. [cite: 25]
                # Success is implied by ACK.
                self.emit_event(DFU_EVENT_PROGRAM_SUCCESS, progress=100, message="DFU Upgrade Successful! (Evorun)")
                self.dfu_in_progress = False
                if self.serial_port and self.serial_port.is_open and self.firmware_data:
                    QTimer.singleShot(100, lambda: self.emit_event(DFU_EVENT_IDLE, message="Ready"))
            else:  # ACK_ERROR
                self.emit_event(DFU_EVENT_ERROR, message="L2: PROGRAME_END (0x25) command failed.")
                self.dfu_in_progress = False
                if self.serial_port and self.serial_port.is_open and self.firmware_data:
                    QTimer.singleShot(100, lambda: self.emit_event(DFU_EVENT_IDLE, message="Error Occurred"))
        else:
            self.emit_event(DFU_EVENT_INFO_RECEIVED,
                            message=f"L2: Received unhandled L2 command type: 0x{cmd_type:04X}")

    # --- DFU Commands (L2 Content Preparation) ---
    # These methods prepare data for L2 commands and then call send_command (which handles L1/L2 framing)

    def get_info(self):  # Corresponds to L2 GET_INFO (0x01), but 0x01 is not in Evorun PDF [cite: 9]
        # Evorun starts with 0x42 (DFU_FW_INFO_GET) [cite: 35] or 0x27 (SYSTEM_INFO).
        # For initial handshake, let's use 0x42 as per the flowchart.
        # If GET_INFO (0x01) was part of GR551x SDK for bootloader info,
        # it's replaced by Evorun's specific commands.
        # We need a method to get initial slave info to decide if update is needed.
        # The flowchart [cite: 35] starts with "获取固件文件信息" (local) then "发送命令0x42".
        self.emit_event(DFU_EVENT_GETTING_INFO, message="L2: Sending DFU_FW_INFO_GET (0x42)...")
        self.send_command(DFU_FW_INFO_GET)  # 0x42 request has no data payload [cite: 29]

    # dfu_mode_set not in Evorun protocol [cite: 9]
    # def dfu_mode_set(self, dfu_mode): ...
    def dfu_mode_set(self, dfu_mode):
        data = struct.pack("<B", dfu_mode)
        self.emit_event(DFU_EVENT_SETTING_DFU_MODE, message="Sending DFU_MODE_SET command...")
        self.send_command(DFU_MODE_SET, data)

    def dfu_fw_info_get(self):  # This is the initiator in Evorun flow [cite: 35]
        self.emit_event(DFU_EVENT_GETTING_INFO, message="L2: Sending DFU_FW_INFO_GET (0x42)...")
        self.send_command(DFU_FW_INFO_GET)  # Request for 0x42 has no DATA field [cite: 29]

    def system_info_get(self):  # L2 SYSTEM_INFO (0x27) [cite: 9]
        # For Evorun, 0x27 DATA field: 1 byte reserved (0x00), 4 bytes addr (0x01000000), 2 bytes len (0x0030) [cite: 10, 12]
        # Total 1+4+2 = 7 bytes for DATA field of L2 command 0x27
        reserved_byte = 0x00
        info_addr = FLASH_START_ADDR  # 0x01000000 [cite: 10]
        info_len = 0x0030  # [cite: 12]
        l2_data = struct.pack("<B I H", reserved_byte, info_addr, info_len)
        self.emit_event(DFU_EVENT_GETTING_INFO, message="L2: Sending SYSTEM_INFO (0x27)...")
        self.send_command(SYSTEM_INFO, l2_data)

    # program_start needs to be adapted for Evorun 0x23 command structure [cite: 15]
    def program_start_evorun(self):  # Corresponds to L2 PROGRAM_START (0x23)
        if not self.dfu_in_progress:
            self.emit_event(DFU_EVENT_ERROR, message="DFU process not started. Cannot send PROGRAM_START (0x23).")
            return False

        # img_info is populated by DfuGui.read_firmware_info from the .bin/.ota file
        # It should contain fields as per Evorun PDF's "固件文件解析" [cite: 36, 39, 41]
        # These are: 信息类型 (pattern), 版本值 (version), 固件大小 (bin_size), 校验和 (check_sum),
        # 加载地址 (load_addr), 运行地址 (run_addr), xip控制命令 (xqspi_xip_cmd), option, 固件名称 (comments)

        # Construct L2 DATA for 0x23 command [cite: 15]
        # Byte 0: 标志数据 (flag_data) = 0x00
        # Byte 1-2: 信息类型 (info_type) = 0x4744 (parsed as pattern from file, should be this format)
        # Byte 3-4: 版本值 (version) = from file
        # Byte 5-8: 固件大小 (firmware_size) = from file (bin_size)
        # Byte 9-12: 校验和 (checksum) = from file (check_sum of binary)
        # Byte 13-16: 加载地址 (load_address) = 0x01080000 (fixed DFU target address) [cite: 15]
        # Byte 17-20: 运行地址 (run_address) = from file (run_addr) (PDF example uses 0x01020000) [cite: 15]
        # Byte 21-24: xip控制命令 (xip_ctrl_cmd) = from file (xqspi_xip_cmd) (PDF example 0x0000000B) [cite: 15]
        # Byte 25-28: option = from file (PDF example fixed value, implies it's in file info) [cite: 15]
        # Byte 29-40: 固件名称 (firmware_name, 12 bytes) = from file (comments) [cite: 15]
        # Total L2 DATA length = 1 + 2 + 2 + 4 + 4 + 4 + 4 + 4 + 4 + 12 = 41 bytes.

        try:
            flag_data = 0x00  # [cite: 15]
            # self.img_info["pattern"] should be 0x4744 if parsed correctly from file's "信息类型" [cite: 39]
            info_type = self.img_info.get("pattern", 0x4744)  # Default, but should be from file
            version = self.img_info.get("version", 1)  # Default, but should be from file [cite: 39]
            firmware_size = self.img_info.get("bin_size", 0)  # From file [cite: 39]
            checksum = self.img_info.get("check_sum", 0)  # From file [cite: 39]

            # Load address for DFU operation is fixed [cite: 15]
            load_address = FLASH_SAVE_ADDR  # 0x01080000

            run_address = self.img_info.get("run_addr", 0)  # From file [cite: 39]
            xip_ctrl_cmd = self.img_info.get("xqspi_xip_cmd", 0)  # From file [cite: 39]
            # "option" field from PDF [cite: 15] (Byte 25-28), needs to be in self.img_info if it's dynamic
            # Let's assume it's part of the parsed file info, or use a default if missing.
            # The Python script's `read_firmware_info` parses `bitfield_value` which contains xqspi_speed etc.
            # And `settings_addr`, `settings_size`. The Evorun PDF for PROGRAM_START [cite: 15] has "option".
            # The PDF for file parsing [cite: 39, 41] also shows "option".
            # This needs to be mapped correctly from `self.img_info`.
            # For now, if `self.img_info` has an "option" key from parsing, use it. Otherwise, a default.
            option_val = self.img_info.get("option",
                                           0)  # Example default, should be from file parsing logic for "option" [cite: 41]

            fw_name_str = self.img_info.get("comments", "tm_app")[:12]  # Max 12 chars [cite: 15, 41]
            fw_name_bytes = fw_name_str.encode('ascii', 'ignore').ljust(12, b'\x00')

            l2_data = struct.pack("<B H H I I I I I I 12s",
                                  flag_data, info_type, version, firmware_size, checksum,
                                  load_address, run_address, xip_ctrl_cmd, option_val,
                                  fw_name_bytes)

            # Update s_file_size for progress calculation during PROGRAME_FLASH
            # self.s_file_size = firmware_size

        except KeyError as e:
            self.emit_event(DFU_EVENT_ERROR, message=f"L2: PROGRAM_START missing info from file: {e}")
            return False
        except struct.error as e:
            self.emit_event(DFU_EVENT_ERROR, message=f"L2: PROGRAM_START packing error: {e}")
            return False
        self.dfu_mode_set(0x01)  # Move to the next step
        time.sleep(0.01)
        self.s_progress = 0
        self.emit_event(DFU_EVENT_PROGRAM_STARTING,
                        message=f"L2: Sending PROGRAM_START (0x23) with {len(l2_data)} bytes of L2 data...")
        return self.send_command(PROGRAM_START, l2_data)

    # program_start2 and original program_start are GR551x specific, replaced by program_start_evorun
    # def program_start(self, img_info, security=False, run_fw=True, fast_dfu=False): ...
    # def program_start2(self, img_info, security=False, run_fw=True, fast_dfu=False): ...

    def send_next_flash_chunk_evorun(self):  # Corresponds to L2 PROGRAME_FLASH (0x24)
        if self.firmware_data is None or self.program_size >= self.s_file_size:
            # This state should ideally be caught by the L2 command handler logic
            return False

        chunk_size = min(self.once_send_size, self.s_file_size - self.program_size)
        data_chunk = self.firmware_data[self.program_size: self.program_size + chunk_size]

        # L2 DATA for 0x24 command [cite: 20]
        # Byte 0: 标志数据 (flag_data) = 0x01
        # Byte 1-4: 写入地址 (write_address) = FLASH_SAVE_ADDR + self.program_size
        # Byte 5-6: 数据包长度 (packet_length) = chunk_size (length of data_chunk)
        # Byte 7...: 数据 (data) = data_chunk
        # Total L2 DATA length = 1 + 4 + 2 + chunk_size

        flag_data = 0x01  # [cite: 20]
        write_address = FLASH_SAVE_ADDR + self.program_size  # [cite: 20]
        packet_length = chunk_size

        # Checksum for programe_end is over the actual firmware data bytes being sent
        self.s_all_check_sum = (self.s_all_check_sum + sum(data_chunk)) & 0xFFFFFFFF

        header_for_l2_data = struct.pack("<B I H", flag_data, write_address, packet_length)
        l2_data = header_for_l2_data + data_chunk

        # print(f"L2: Sending flash chunk. Addr:0x{write_address:08X}, Size:{packet_length}, ChunkHex: {data_chunk[:16].hex()}...") # Debug

        if self.send_command(PROGRAME_FLASH, l2_data):
            self.program_size += chunk_size  # Update after successful send
            return True
        else:
            return False  # Error sending command

    def programe_end_evorun(self):  # Corresponds to L2 PROGRAME_END (0x25)
        if not self.dfu_in_progress:
            self.emit_event(DFU_EVENT_ERROR, message="DFU not in progress, cannot send PROGRAME_END (0x25).")
            return False

        # L2 DATA for 0x25 command [cite: 25]
        # Byte 0: 标志数据 (flag_data) = 0x01 (run firmware if true, based on s_run_fw_flag)
        # Byte 1-4: 固件文件校验值 (firmware_file_checksum) = self.s_all_check_sum

        # The PDF description "固定 0x01" for flag_data seems to imply always run.
        # However, typically this flag controls whether to run the new firmware.
        # Let's use s_run_fw_flag. If PDF means the *byte itself* is 0x01 when true, that's fine.
        flag_data = 0x01 if self.s_run_fw_flag else 0x00
        # Using 0x01 as per PDF fixed value example[cite: 25], implying it might always try to run.
        # If it needs to be conditional:
        # flag_data = 0x01 if self.s_run_fw_flag else 0x00

        firmware_file_checksum = self.s_all_check_sum & 0xFFFFFFFF

        l2_data = struct.pack("<B I", flag_data, firmware_file_checksum)

        self.emit_event(DFU_EVENT_PROGRAM_END, message="L2: Sending PROGRAME_END (0x25)...")
        return self.send_command(PROGRAME_END, l2_data)

    def start_dfu_process(self, firmware_data_full, img_info_parsed, run_fw=True, filesize = 0,fast_dfu=False):  # fast_dfu not used by Evorun
        if self.dfu_in_progress:
            self.emit_event(DFU_EVENT_BUSY, message="DFU process already in progress.")
            return False
        if not self.serial_port or not self.serial_port.is_open:
            self.emit_event(DFU_EVENT_ERROR, message="Serial port not connected. Cannot start DFU.")
            return False
        if not firmware_data_full or not img_info_parsed:  # firmware_data_full is the raw .bin content
            self.emit_event(DFU_EVENT_ERROR, message="No valid firmware file loaded or info parsed.")
            return False

        self.dfu_in_progress = True
        self.emit_event(DFU_EVENT_BUSY, message="DFU process started (Evorun)...")

        self.firmware_data = firmware_data_full  # Store the raw firmware bytes for send_next_flash_chunk
        self.img_info = img_info_parsed  # Parsed info from file (used for PROGRAM_START)

        # s_file_size is critical, should be the actual binary size to be transferred.
        # This is typically img_info_parsed.get("bin_size")
        self.s_file_size = self.img_info.get("bin_size", 0)
        self.s_file_size = filesize
        if self.s_file_size == 0:
            self.emit_event(DFU_EVENT_ERROR, message="Firmware binary size is 0. Cannot proceed.")
            self.dfu_in_progress = False
            return False

        self.s_run_fw_flag = run_fw
        # self.fast_dfu_mode = 0 # Evorun does not specify fast DFU

        # Reset L1 and L2 parsers and DFU state variables
        self._reset_l1_parser_state()
        self.s_l2_parse_state = CHECK_FRAME_L_STATE
        self.s_l2_cmd_receive_flag = False
        self.s_l2_receive_data_count = 0
        self.s_l2_receive_check_sum = 0
        self.s_l2_receive_frame = {"cmd_type": 0, "data_len": 0, "data": b"", "check_sum": 0}

        self.program_size = 0
        self.s_all_check_sum = 0  # For L2 PROGRAME_END data checksum
        self.s_dfu_save_addr = 0  # Will be confirmed by DFU_FW_INFO_GET response
        self.s_bootloader_boot_info = {}
        self.s_app_info = {}
        # self.s_sec_flag = False # Not specified in Evorun commands
        self.s_version_flag = True  # Assuming Evorun protocol is the "new" version flow (uses 0x42)

        # Start the DFU sequence for Evorun: Send DFU_FW_INFO_GET (0x42) [cite: 35]
        self.dfu_fw_info_get()
        return True


# --- DfuGui Class (No changes needed for L1/L2 protocol layering, only calls to DfuMaster) ---
# Ensure DfuGui.read_firmware_info parses fields required by program_start_evorun
# and that DfuGui.start_dfu_upgrade calls DfuMaster.start_dfu_process correctly.

class DfuGui(QWidget):
    def __init__(self):
        super().__init__()
        self.firmware_file_content = None  # Raw bytes of the selected firmware file's content
        self.parsed_img_info = {}  # Stores dfu_img_info_t fields parsed from file
        self.dfu_master = DfuMaster()
        self.dfu_master.set_event_callback(self.update_status)

        self.initUI()
        self.load_ports()
        self.file_size = 0
    def initUI(self):  # Simplified, keep original UI elements
        self.setWindowTitle('Evorun UART DFU Master (L1/L2)')  # Updated title
        self.setGeometry(100, 100, 700, 550)  # Slightly taller for more info fields

        layout = QVBoxLayout()
        serial_layout = QHBoxLayout()
        self.port_label = QLabel("Serial Port:")
        self.port_combobox = QComboBox()
        self.refresh_ports_button = QPushButton("Refresh Ports")
        self.refresh_ports_button.clicked.connect(self.load_ports)
        self.baudrate_label = QLabel("Baud Rate:")
        self.baudrate_combobox = QComboBox()
        self.baudrate_combobox.addItems(
            ["9600", "19200", "38400", "57600", "115200", "230400", "460800", "921600", "1000000", "2000000"])
        self.baudrate_combobox.setCurrentText("38400")
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.toggle_connection)
        serial_layout.addWidget(self.port_label)
        serial_layout.addWidget(self.port_combobox)
        serial_layout.addWidget(self.refresh_ports_button)
        serial_layout.addWidget(self.baudrate_label)
        serial_layout.addWidget(self.baudrate_combobox)
        serial_layout.addWidget(self.connect_button)
        layout.addLayout(serial_layout)

        file_layout = QHBoxLayout()
        self.file_label = QLabel("No file selected (.bin or .ota)")
        self.select_file_button = QPushButton("Select Firmware File")
        self.select_file_button.clicked.connect(self.select_firmware_file)
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(self.select_file_button)
        layout.addLayout(file_layout)

        info_layout = QFormLayout()
        # Parsed from local firmware file
        self.fw_info_type_value = QLineEdit()
        self.fw_info_type_value.setReadOnly(True)
        info_layout.addRow("FW File Info Type (Pattern):", self.fw_info_type_value)

        self.fw_version_value = QLineEdit()
        self.fw_version_value.setReadOnly(True)
        info_layout.addRow("FW File Version:", self.fw_version_value)

        self.fw_bin_size_value = QLineEdit()  # This is img_info.bin_size
        self.fw_bin_size_value.setReadOnly(True)
        info_layout.addRow("FW File Bin Size (bytes):", self.fw_bin_size_value)

        self.fw_checksum_value = QLineEdit()  # img_info.check_sum
        self.fw_checksum_value.setReadOnly(True)
        info_layout.addRow("FW File Checksum (of bin):", self.fw_checksum_value)

        self.fw_load_addr_value = QLineEdit()  # img_info.load_addr (from file)
        self.fw_load_addr_value.setReadOnly(True)
        info_layout.addRow("FW File Load Address (in file):", self.fw_load_addr_value)

        self.fw_run_addr_value = QLineEdit()  # img_info.run_addr
        self.fw_run_addr_value.setReadOnly(True)
        info_layout.addRow("FW File Run Address:", self.fw_run_addr_value)

        self.fw_xip_cmd_value = QLineEdit()
        self.fw_xip_cmd_value.setReadOnly(True)
        info_layout.addRow("FW File XIP CMD:", self.fw_xip_cmd_value)

        self.fw_option_value = QLineEdit()
        self.fw_option_value.setReadOnly(True)
        info_layout.addRow("FW File Option Field:", self.fw_option_value)

        self.fw_name_value = QLineEdit()  # img_info.comments
        self.fw_name_value.setReadOnly(True)
        info_layout.addRow("FW File Name (max 12c):", self.fw_name_value)

        # Info received from slave device
        self.slave_boot_addr_value = QLineEdit()
        self.slave_boot_addr_value.setReadOnly(True)
        info_layout.addRow("Slave Bootloader Addr:", self.slave_boot_addr_value)

        self.slave_dfu_save_addr_value = QLineEdit()  # s_dfu_save_addr from DFU_FW_INFO_GET
        self.slave_dfu_save_addr_value.setReadOnly(True)
        info_layout.addRow("Slave DFU Save Addr (fixed):", self.slave_dfu_save_addr_value)

        self.slave_app_load_addr_value = QLineEdit()
        self.slave_app_load_addr_value.setReadOnly(True)
        info_layout.addRow("Slave Current App Load Addr:", self.slave_app_load_addr_value)

        layout.addLayout(info_layout)

        options_layout = QHBoxLayout()
        # self.fast_dfu_checkbox = QCheckBox("Fast DFU Mode") # Not for Evorun
        self.run_fw_checkbox = QCheckBox("Run firmware after upgrade")
        self.run_fw_checkbox.setChecked(True)
        # options_layout.addWidget(self.fast_dfu_checkbox)
        options_layout.addWidget(self.run_fw_checkbox)
        layout.addLayout(options_layout)

        self.start_upgrade_button = QPushButton("Start DFU Upgrade")
        self.start_upgrade_button.clicked.connect(self.start_dfu_upgrade)
        self.start_upgrade_button.setEnabled(False)
        layout.addWidget(self.start_upgrade_button)

        self.status_label = QLabel("Status: Idle")
        layout.addWidget(self.status_label)
        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.progress_bar)
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)
        self.setLayout(layout)

    def load_ports(self):
        self.port_combobox.clear()
        ports = serial.tools.list_ports.comports()
        if not ports:
            self.port_combobox.addItem("No Ports Found")
            self.connect_button.setEnabled(False)
        else:
            for port_info in ports:  # Changed variable name
                self.port_combobox.addItem(port_info.device)
            self.connect_button.setEnabled(True)

    def toggle_connection(self):
        if self.dfu_master.serial_port and self.dfu_master.serial_port.is_open:
            self.dfu_master.disconnect()
            # Connect button state managed by DFU_EVENT_DISCONNECTED
        else:
            port = self.port_combobox.currentText()
            if port == "No Ports Found" or not port:
                QMessageBox.warning(self, "Connection Error", "No serial port selected or found.")
                return
            try:
                baudrate = int(self.baudrate_combobox.currentText())
            except ValueError:
                QMessageBox.warning(self, "Connection Error", "Invalid baud rate.")
                return

            self.update_status(DFU_EVENT_CONNECTING, message=f"Connecting to {port}...")
            if self.dfu_master.connect(port, baudrate):
                self.connect_button.setText("Disconnect")
                # Start button enabled by DFU_EVENT_CONNECTED if file is also selected
            else:  # Connection failed (event DFU_EVENT_ERROR emitted by connect)
                self.connect_button.setText("Connect")

    def select_firmware_file(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Select Firmware File", "",
                                                  "OTA Files (*.ota *.bin);;All Files (*)",
                                                  options=options)  # Added .ota
        if fileName:
            self.file_label.setText(os.path.basename(fileName))
            self.read_firmware_info_evorun(fileName)  # Use Evorun specific parser
            if self.dfu_master.serial_port and self.dfu_master.serial_port.is_open and self.firmware_file_content:
                self.start_upgrade_button.setEnabled(True)
            elif not (self.dfu_master.serial_port and self.dfu_master.serial_port.is_open):
                self.start_upgrade_button.setEnabled(False)

    def read_firmware_info_evorun(self, file_path):  # Adapted for Evorun PDF [cite: 36]
        self.clear_firmware_gui_info()
        self.firmware_file_content = None
        self.parsed_img_info = {}

        try:
            total_file_size = os.path.getsize(file_path)
            if total_file_size < 48:  # Need last 48 bytes for info block [cite: 36]
                QMessageBox.warning(self, "File Error", f"File size ({total_file_size} bytes) < 48 bytes minimum.")
                return

            with open(file_path, "rb") as f:
                # Read the entire file content for DFU programming
                self.firmware_file_content = f.read()

                # Seek to read the last 48 bytes for the info block [cite: 36]
                f.seek(-48, os.SEEK_END)
                last_48_bytes = f.read(48)
                self.file_size = total_file_size
            if len(last_48_bytes) != 48:
                QMessageBox.warning(self, "File Error", "Could not read last 48 bytes for info block.")
                return

            # Parse the first 40 bytes of these last 48 bytes as dfu_img_info_t [cite: 36]
            dfu_img_info_bytes = last_48_bytes[:SIZE_OF_DFU_IMG_INFO_T]  # SIZE_OF_DFU_IMG_INFO_T is 40

            # Fields from Evorun PDF Table "字段说明" for file parsing [cite: 39, 41]
            # 0-1: 信息类型 (info_type/pattern) - uint16_t (e.g., 0x4744)
            # 2-3: 版本值 (version) - uint16_t
            # 4-7: 固件大小 (firmware_size/bin_size) - uint32_t
            # 8-11: 校验和 (checksum of bin) - uint32_t
            # 12-15: 加载地址 (load_address from file info) - uint32_t
            # 16-19: 运行地址 (run_address from file info) - uint32_t
            # 20-23: xip控制命令 (xip_ctrl_cmd) - uint32_t
            # 24-27: option - uint32_t
            # 28-39: 固件名称 (firmware_name) - 12 char/bytes

            try:
                s = struct.Struct("< H H I I I I I I 12s")  # Corresponds to the 40 byte structure
                unpacked_data = s.unpack(dfu_img_info_bytes)

                self.parsed_img_info = {
                    "file_path": file_path,
                    "total_file_size": total_file_size,  # Full size of the .ota/.bin file
                    "pattern": unpacked_data[0],  # "信息类型" [cite: 39]
                    "version": unpacked_data[1],  # "版本值" [cite: 39]
                    "bin_size": unpacked_data[2],  # "固件大小" [cite: 39]
                    "check_sum": unpacked_data[3],  # "校验和" [cite: 39]
                    "load_addr": unpacked_data[4],  # "加载地址" from file info [cite: 39]
                    "run_addr": unpacked_data[5],  # "运行地址" from file info [cite: 39]
                    "xqspi_xip_cmd": unpacked_data[6],  # "xip控制命令" [cite: 39]
                    "option": unpacked_data[7],  # "option" [cite: 41]
                    "comments": unpacked_data[8].split(b'\x00')[0].decode('ascii', 'ignore')  # "固件名称" [cite: 41]
                }
                # Note: The "firmware_data" for DfuMaster is self.firmware_file_content (the whole file)
                # The PROGRAM_START command will use fields from self.parsed_img_info.
                # The PROGRAME_FLASH command will use self.firmware_file_content, sliced by bin_size.

                # Update GUI fields
                self.fw_info_type_value.setText(f"0x{self.parsed_img_info['pattern']:04X}")
                self.fw_version_value.setText(str(self.parsed_img_info['version']))
                self.fw_bin_size_value.setText(str(self.parsed_img_info['bin_size']))
                self.fw_checksum_value.setText(f"0x{self.parsed_img_info['check_sum']:08X}")
                self.fw_load_addr_value.setText(f"0x{self.parsed_img_info['load_addr']:08X}")
                self.fw_run_addr_value.setText(f"0x{self.parsed_img_info['run_addr']:08X}")
                self.fw_xip_cmd_value.setText(f"0x{self.parsed_img_info['xqspi_xip_cmd']:08X}")
                self.fw_option_value.setText(f"0x{self.parsed_img_info['option']:08X}")
                self.fw_name_value.setText(self.parsed_img_info['comments'])

                if self.dfu_master.serial_port and self.dfu_master.serial_port.is_open:
                    self.start_upgrade_button.setEnabled(True)

            except struct.error as e:
                QMessageBox.warning(self, "File Parse Error", f"Error unpacking Evorun firmware info (40 bytes): {e}")
                self.clear_firmware_gui_info()
            except Exception as e:
                QMessageBox.warning(self, "File Parse Error", f"Unexpected error parsing firmware info: {e}")
                self.clear_firmware_gui_info()

        except FileNotFoundError:
            QMessageBox.warning(self, "File Error", "Selected file not found.")
            self.clear_firmware_gui_info()
        except Exception as e:
            QMessageBox.warning(self, "File Error", f"An unexpected error occurred reading file: {e}")
            self.clear_firmware_gui_info()

    def clear_firmware_gui_info(self):  # Renamed to avoid conflict
        self.file_label.setText("No file selected (.bin or .ota)")
        self.fw_info_type_value.clear()
        self.fw_version_value.clear()
        self.fw_bin_size_value.clear()
        self.fw_checksum_value.clear()
        self.fw_load_addr_value.clear()
        self.fw_run_addr_value.clear()
        self.fw_xip_cmd_value.clear()
        self.fw_option_value.clear()
        self.fw_name_value.clear()

        # self.slave_boot_addr_value.clear() # Cleared by update_status if needed
        # self.slave_dfu_save_addr_value.clear()
        # self.slave_app_load_addr_value.clear()

        self.firmware_file_content = None
        self.parsed_img_info = {}
        self.start_upgrade_button.setEnabled(False)

    def start_dfu_upgrade(self):
        if not self.firmware_file_content or not self.parsed_img_info:
            QMessageBox.warning(self, "DFU Error", "No valid firmware file loaded/parsed.")
            return
        if not (self.dfu_master.serial_port and self.dfu_master.serial_port.is_open):
            QMessageBox.warning(self, "DFU Error", "Serial port not connected.")
            return
        if self.dfu_master.dfu_in_progress:
            QMessageBox.information(self, "DFU Status", "DFU process is already in progress.")
            return

        self.start_upgrade_button.setEnabled(False)  # Disable during DFU
        run_fw = self.run_fw_checkbox.isChecked()
        # fast_dfu = self.fast_dfu_checkbox.isChecked() # Not for Evorun

        # firmware_file_content contains the *entire* file. DfuMaster will use this.
        # parsed_img_info contains the metadata parsed from the file.

        if self.dfu_master.start_dfu_process(self.firmware_file_content,
                                             self.parsed_img_info,
                                             True,
                                             self.file_size,
                                             ):  # fast_dfu removed
            self.progress_bar.setValue(0)
            self.log_output.clear()
            self.log_output.append("--- DFU START (Evorun Protocol) ---")
        else:  # Start failed (e.g., bin_size was 0)
            self.start_upgrade_button.setEnabled(True)

    def update_status(self, event, progress=0, message=""):
        status_text = f"Status: {message}"
        self.status_label.setText(status_text)
        self.log_output.append(message)  # Log all messages

        if event == DFU_EVENT_PROGRAM_PROGRESS:
            self.progress_bar.setValue(progress)
        elif event in [DFU_EVENT_ERROR, DFU_EVENT_PROGRAM_SUCCESS, DFU_EVENT_IDLE, DFU_EVENT_BUSY]:
            if event == DFU_EVENT_ERROR:
                self.progress_bar.setValue(0)
                self.log_output.append("--- DFU END (ERROR) ---")
            elif event == DFU_EVENT_PROGRAM_SUCCESS:
                self.progress_bar.setValue(100)
                self.log_output.append("--- DFU END (SUCCESS) ---")

            # Re-enable start button if DFU finished (success/error/idle) AND connected AND file loaded
            if not self.dfu_master.dfu_in_progress and \
                    self.dfu_master.serial_port and self.dfu_master.serial_port.is_open and \
                    self.firmware_file_content:
                self.start_upgrade_button.setEnabled(True)
            elif self.dfu_master.dfu_in_progress and event == DFU_EVENT_BUSY:
                self.start_upgrade_button.setEnabled(False)


        elif event == DFU_EVENT_CONNECTED:
            self.connect_button.setText("Disconnect")
            if self.firmware_file_content:  # File already selected
                self.start_upgrade_button.setEnabled(True)
        elif event == DFU_EVENT_DISCONNECTED:
            self.connect_button.setText("Connect")
            self.start_upgrade_button.setEnabled(False)
            self.dfu_master.dfu_in_progress = False  # Ensure flag is reset

        # Update slave info from DfuMaster state
        if self.dfu_master.s_bootloader_boot_info.get('load_addr', 0) != 0:
            self.slave_boot_addr_value.setText(f"0x{self.dfu_master.s_bootloader_boot_info['load_addr']:08X}")
        if self.dfu_master.s_dfu_save_addr != 0:
            self.slave_dfu_save_addr_value.setText(f"0x{self.dfu_master.s_dfu_save_addr:08X}")
        if self.dfu_master.s_app_info.get('load_addr', 0) != 0:
            self.slave_app_load_addr_value.setText(f"0x{self.dfu_master.s_app_info['load_addr']:08X}")

        self.log_output.verticalScrollBar().setValue(self.log_output.verticalScrollBar().maximum())

    def closeEvent(self, event):
        self.dfu_master.disconnect()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DfuGui()
    ex.show()
    sys.exit(app.exec_())
