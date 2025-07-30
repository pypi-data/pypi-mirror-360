import asyncio
import queue
import struct
from asyncio import Queue
from contextlib import suppress
from datetime import datetime
from dataclasses import dataclass
from enum import IntEnum
from typing import Optional, Dict, List

import numpy as np
from bleak import (
    BleakScanner,
    BLEDevice,
    AdvertisementData,
    BleakClient,
    BleakGATTCharacteristic,
)

from sensor import sensor_utils


@dataclass
class Characteristic:
    uuid: str
    service_uuid: str
    descriptor_uuids: List[str]


class Command(IntEnum):
    GET_PROTOCOL_VERSION = (0x00,)
    GET_FEATURE_MAP = (0x01,)
    GET_DEVICE_NAME = (0x02,)
    GET_MODEL_NUMBER = (0x03,)
    GET_SERIAL_NUMBER = (0x04,)
    GET_HW_REVISION = (0x05,)
    GET_FW_REVISION = (0x06,)
    GET_MANUFACTURER_NAME = (0x07,)
    GET_BOOTLOADER_VERSION = (0x0A,)

    GET_BATTERY_LEVEL = (0x08,)
    GET_TEMPERATURE = (0x09,)

    POWEROFF = (0x1D,)
    SWITCH_TO_OAD = (0x1E,)
    SYSTEM_RESET = (0x1F,)
    SWITCH_SERVICE = (0x20,)

    SET_LOG_LEVEL = (0x21,)
    SET_LOG_MODULE = (0x22,)
    PRINT_KERNEL_MSG = (0x23,)
    MOTOR_CONTROL = (0x24,)
    LED_CONTROL_TEST = (0x25,)
    PACKAGE_ID_CONTROL = (0x26,)

    GET_ACCELERATE_CAP = (0x30,)
    SET_ACCELERATE_CONFIG = (0x31,)

    GET_GYROSCOPE_CAP = (0x32,)
    SET_GYROSCOPE_CONFIG = (0x33,)

    GET_MAGNETOMETER_CAP = (0x34,)
    SET_MAGNETOMETER_CONFIG = (0x35,)

    GET_EULER_ANGLE_CAP = (0x36,)
    SET_EULER_ANGLE_CONFIG = (0x37,)

    QUATERNION_CAP = (0x38,)
    QUATERNION_CONFIG = (0x39,)

    GET_ROTATION_MATRIX_CAP = (0x3A,)
    SET_ROTATION_MATRIX_CONFIG = (0x3B,)

    GET_GESTURE_CAP = (0x3C,)
    SET_GESTURE_CONFIG = (0x3D,)

    GET_EMG_RAWDATA_CAP = (0x3E,)
    SET_EMG_RAWDATA_CONFIG = (0x3F,)

    GET_MOUSE_DATA_CAP = (0x40,)
    SET_MOUSE_DATA_CONFIG = (0x41,)

    GET_JOYSTICK_DATA_CAP = (0x42,)
    SET_JOYSTICK_DATA_CONFIG = (0x43,)

    GET_DEVICE_STATUS_CAP = (0x44,)
    SET_DEVICE_STATUS_CONFIG = (0x45,)

    GET_EMG_RAWDATA_CONFIG = (0x46,)

    SET_DATA_NOTIF_SWITCH = (0x4F,)
    SET_FUNCTION_SWITCH = (0x85,)

    CMD_GET_EEG_CONFIG = (0xA0,)
    CMD_SET_EEG_CONFIG = (0xA1,)
    CMD_GET_ECG_CONFIG = (0xA2,)
    CMD_SET_ECG_CONFIG = (0xA3,)
    CMD_GET_IMPEDANCE_CONFIG = (0xA4,)
    CMD_SET_IMPEDANCE_CONFIG = (0xA5,)
    CMD_GET_EEG_CAP = (0xA6,)
    CMD_GET_ECG_CAP = (0xA7,)
    CMD_GET_IMPEDANCE_CAP = (0xA8,)
    CMD_GET_IMU_CONFIG = (0xAC,)
    CMD_SET_IMU_CONFIG = (0xAD,)
    CMD_GET_BLE_MTU_INFO = (0xAE,)
    CMD_GET_BRT_CONFIG = (0xB3,)

    CMD_SET_FRIMWARE_FILTER_SWITCH = (0xAA,)
    CMD_GET_FRIMWARE_FILTER_SWITCH = (0xA9,)
    # Partial command packet, format: [CMD_PARTIAL_DATA, packet number in reverse order, packet content]
    MD_PARTIAL_DATA = 0xFF


class DataSubscription(IntEnum):
    # Data Notify All Off
    OFF = (0x00000000,)

    # Accelerate On(C.7)
    ACCELERATE = (0x00000001,)

    # Gyroscope On(C.8)
    GYROSCOPE = (0x00000002,)

    # Magnetometer On(C.9)
    MAGNETOMETER = (0x00000004,)

    # Euler Angle On(C.10)
    EULERANGLE = (0x00000008,)

    # Quaternion On(C.11)
    QUATERNION = (0x00000010,)

    # Rotation Matrix On(C.12)
    ROTATIONMATRIX = (0x00000020,)

    # EMG Gesture On(C.13)
    EMG_GESTURE = (0x00000040,)

    # EMG Raw Data On(C.14)
    EMG_RAW = (0x00000080,)

    # HID Mouse On(C.15)
    HID_MOUSE = (0x00000100,)

    # HID Joystick On(C.16)
    HID_JOYSTICK = (0x00000200,)

    # Device Status On(C.17)
    DEVICE_STATUS = (0x00000400,)

    # Device Log On
    LOG = (0x00000800,)

    DNF_EEG = (0x00010000,)

    DNF_ECG = (0x00020000,)

    DNF_IMPEDANCE = (0x00040000,)

    DNF_IMU = (0x00080000,)

    DNF_ADS = (0x00100000,)

    DNF_BRTH = (0x00200000,)

    DNF_CONCAT_BLE = (0x80000000,)
    # Data Notify All On
    ALL = 0xFFFFFFFF


class DataType(IntEnum):
    ACC = (0x01,)
    GYO = (0x02,)
    MAG = (0x03,)
    EULER = (0x04,)
    QUAT = (0x05,)
    ROTA = (0x06,)
    EMG_GEST = (0x07,)
    EMG_ADC = (0x08,)
    HID_MOUSE = (0x09,)
    HID_JOYSTICK = (0x0A,)
    DEV_STATUS = (0x0B,)
    LOG = (0x0C,)

    PARTIAL = 0xFF


class SampleResolution(IntEnum):
    BITS_8 = (8,)
    BITS_12 = (12,)
    BITS_16 = (16,)
    BITS_24 = 24


class SamplingRate(IntEnum):
    HZ_250 = (250,)
    HZ_500 = (500,)
    HZ_650 = (650,)


@dataclass
class EmgRawDataConfig:
    fs: SamplingRate = SamplingRate.HZ_500
    channel_mask: int = 0xFF
    batch_len: int = 16
    resolution: SampleResolution = SampleResolution.BITS_8

    def to_bytes(self) -> bytes:
        body = b""
        body += struct.pack("<H", self.fs)
        body += struct.pack("<H", self.channel_mask)
        body += struct.pack("<B", self.batch_len)
        body += struct.pack("<B", self.resolution)
        return body

    @classmethod
    def from_bytes(cls, data: bytes):
        fs, channel_mask, batch_len, resolution = struct.unpack(
            "<HHBB",
            data,
        )
        return cls(fs, channel_mask, batch_len, resolution)


@dataclass
class EegRawDataConfig:
    fs: SamplingRate = 0
    channel_mask: int = 0
    batch_len: int = 0
    resolution: SampleResolution = 0
    K: float = 0

    def to_bytes(self) -> bytes:
        body = b""
        body += struct.pack("<H", self.fs)
        body += struct.pack("<Q", self.channel_mask)
        body += struct.pack("<B", self.batch_len)
        body += struct.pack("<B", self.resolution)
        body += struct.pack("<d", self.K)
        return body

    @classmethod
    def from_bytes(cls, data: bytes):
        fs, channel_mask, batch_len, resolution, K = struct.unpack(
            "<HQBBd",
            data,
        )
        return cls(fs, channel_mask, batch_len, resolution, K)


@dataclass
class EegRawDataCap:
    fs: SamplingRate = 0
    channel_count: int = 0
    batch_len: int = 0
    resolution: SampleResolution = 0

    def to_bytes(self) -> bytes:
        body = b""
        body += struct.pack("<B", self.fs)
        body += struct.pack("<B", self.channel_count)
        body += struct.pack("<B", self.batch_len)
        body += struct.pack("<B", self.resolution)
        return body

    @classmethod
    def from_bytes(cls, data: bytes):
        fs, channel_count, batch_len, resolution = struct.unpack(
            "<BBBB",
            data,
        )
        return cls(fs, channel_count, batch_len, resolution)


@dataclass
class EcgRawDataConfig:
    fs: SamplingRate = SamplingRate.HZ_250
    channel_mask: int = 0
    batch_len: int = 16
    resolution: SampleResolution = SampleResolution.BITS_24
    K: float = 0

    def to_bytes(self) -> bytes:
        body = b""
        body += struct.pack("<H", self.fs)
        body += struct.pack("<H", self.channel_mask)
        body += struct.pack("<B", self.batch_len)
        body += struct.pack("<B", self.resolution)
        body += struct.pack("<d", self.K)
        return body

    @classmethod
    def from_bytes(cls, data: bytes):
        fs, channel_mask, batch_len, resolution, K = struct.unpack(
            "<HHBBd",
            data,
        )
        return cls(fs, channel_mask, batch_len, resolution, K)


@dataclass
class ImuRawDataConfig:
    channel_count: int = 0
    fs: SamplingRate = 0
    batch_len: int = 0
    accK: float = 0
    gyroK: float = 0

    def to_bytes(self) -> bytes:
        body = b""
        body += struct.pack("<i", self.channel_count)
        body += struct.pack("<H", self.fs)
        body += struct.pack("<B", self.batch_len)
        body += struct.pack("<d", self.accK)
        body += struct.pack("<d", self.gyroK)
        return body

    @classmethod
    def from_bytes(cls, data: bytes):
        channel_count, fs, batch_len, accK, gyroK = struct.unpack(
            "<iHBdd",
            data,
        )
        return cls(channel_count, fs, batch_len, accK, gyroK)


@dataclass
class BrthRawDataConfig:
    fs: SamplingRate = 0
    channel_mask: int = 0
    batch_len: int = 0
    resolution: SampleResolution = 0
    K: float = 0

    def to_bytes(self) -> bytes:
        body = b""
        body += struct.pack("<H", self.fs)
        body += struct.pack("<H", self.channel_mask)
        body += struct.pack("<B", self.batch_len)
        body += struct.pack("<B", self.resolution)
        body += struct.pack("<d", self.K)
        return body

    @classmethod
    def from_bytes(cls, data: bytes):
        fs, channel_mask, batch_len, resolution, K = struct.unpack(
            "<HHBBd",
            data,
        )
        return cls(fs, channel_mask, batch_len, resolution, K)


@dataclass
class Request:
    cmd: Command
    has_res: bool
    body: Optional[bytes] = None


class ResponseCode(IntEnum):
    SUCCESS = (0x00,)
    NOT_SUPPORT = (0x01,)
    BAD_PARAM = (0x02,)
    FAILED = (0x03,)
    TIMEOUT = (0x04,)
    PARTIAL_PACKET = 0xFF


@dataclass
class Response:
    code: ResponseCode
    cmd: Command
    data: bytes


class GForce:
    def __init__(
        self,
        device: BLEDevice,
        cmd_char: str,
        data_char: str,
        isUniversalStream: bool,
        event_loop: asyncio.AbstractEventLoop,
        gforce_event_loop: asyncio.AbstractEventLoop,
    ):
        self.device_name = ""
        self.client = None
        self.event_loop = event_loop
        self.gforce_event_loop = gforce_event_loop
        self.cmd_char = cmd_char
        self.data_char = data_char
        self.responses: Dict[Command, Queue] = {}
        self.resolution = SampleResolution.BITS_8
        self._num_channels = 8
        self._device = device
        self._is_universal_stream = isUniversalStream
        self._raw_data_buf: queue.Queue[bytes] = None
        self.packet_id = 0
        self.data_packet = []

    async def connect(self, disconnect_cb, buf: queue.Queue[bytes]):
        client = BleakClient(self._device, disconnected_callback=disconnect_cb)
        self.client = client
        self.device_name = self._device.name
        self._raw_data_buf = buf

        try:
            await sensor_utils.async_call(client.connect(), sensor_utils._TIMEOUT, self.gforce_event_loop)
        except Exception as e:
            return

        if not client.is_connected:
            return

        try:
            if not self._is_universal_stream:
                await sensor_utils.async_call(
                    client.start_notify(self.cmd_char, self._on_cmd_response),
                    sensor_utils._TIMEOUT,
                    self.gforce_event_loop,
                )

            else:
                await sensor_utils.async_call(
                    client.start_notify(self.data_char, self._on_universal_response),
                    sensor_utils._TIMEOUT,
                    self.gforce_event_loop,
                )
        except Exception as e:
            return

    def _on_data_response(self, q: queue.Queue[bytes], bs: bytearray):
        bs = bytes(bs)

        full_packet = []

        is_partial_data = bs[0] == ResponseCode.PARTIAL_PACKET
        if is_partial_data:
            packet_id = bs[1]
            if self.packet_id != 0 and self.packet_id != packet_id + 1:
                raise Exception(
                    "Unexpected packet id: expected {} got {}".format(
                        self.packet_id + 1,
                        packet_id,
                    )
                )
            elif self.packet_id == 0 or self.packet_id > packet_id:
                self.packet_id = packet_id
                self.data_packet += bs[2:]

                if self.packet_id == 0:
                    full_packet = self.data_packet
                    self.data_packet = []
        else:
            full_packet = bs

        if len(full_packet) == 0:
            return

        q.put_nowait(bytes(full_packet))

    @staticmethod
    def _convert_acceleration_to_g(data: bytes) -> np.ndarray[np.float32]:
        normalizing_factor = 65536.0

        acceleration_data = np.frombuffer(data, dtype=np.int32).astype(np.float32) / normalizing_factor
        num_channels = 3

        return acceleration_data.reshape(-1, num_channels)

    @staticmethod
    def _convert_gyro_to_dps(data: bytes) -> np.ndarray[np.float32]:
        normalizing_factor = 65536.0

        gyro_data = np.frombuffer(data, dtype=np.int32).astype(np.float32) / normalizing_factor
        num_channels = 3

        return gyro_data.reshape(-1, num_channels)

    @staticmethod
    def _convert_magnetometer_to_ut(data: bytes) -> np.ndarray[np.float32]:
        normalizing_factor = 65536.0

        magnetometer_data = np.frombuffer(data, dtype=np.int32).astype(np.float32) / normalizing_factor
        num_channels = 3

        return magnetometer_data.reshape(-1, num_channels)

    @staticmethod
    def _convert_euler(data: bytes) -> np.ndarray[np.float32]:

        euler_data = np.frombuffer(data, dtype=np.float32).astype(np.float32)
        num_channels = 3

        return euler_data.reshape(-1, num_channels)

    @staticmethod
    def _convert_quaternion(data: bytes) -> np.ndarray[np.float32]:

        quaternion_data = np.frombuffer(data, dtype=np.float32).astype(np.float32)
        num_channels = 4

        return quaternion_data.reshape(-1, num_channels)

    @staticmethod
    def _convert_rotation_matrix(data: bytes) -> np.ndarray[np.float32]:

        rotation_matrix_data = np.frombuffer(data, dtype=np.int32).astype(np.float32)
        num_channels = 9

        return rotation_matrix_data.reshape(-1, num_channels)

    @staticmethod
    def _convert_emg_gesture(data: bytes) -> np.ndarray[np.float16]:

        emg_gesture_data = np.frombuffer(data, dtype=np.int16).astype(np.float16)
        num_channels = 6

        return emg_gesture_data.reshape(-1, num_channels)

    def _on_universal_response(self, _: BleakGATTCharacteristic, bs: bytearray):
        self._raw_data_buf.put_nowait(bytes(bs))

    def _on_cmd_response(self, _: BleakGATTCharacteristic, bs: bytearray):
        sensor_utils.async_exec(self.async_on_cmd_response(bs), self.event_loop)

    async def async_on_cmd_response(self, bs: bytearray):
        try:
            # print(bytes(bs))
            response = self._parse_response(bytes(bs))
            if self.responses.get(response.cmd) != None:
                self.responses[response.cmd].put_nowait(
                    response.data,
                )
            else:
                print("invalid response:" + bytes(bs))
        except Exception as e:
            raise Exception("Failed to parse response: %s" % e)

    @staticmethod
    def _parse_response(res: bytes) -> Response:
        code = int.from_bytes(res[:1], byteorder="big")
        code = ResponseCode(code)

        cmd = int.from_bytes(res[1:2], byteorder="big")
        cmd = Command(cmd)

        data = res[2:]

        return Response(
            code=code,
            cmd=cmd,
            data=data,
        )

    async def get_protocol_version(self) -> str:
        buf = await self._send_request(
            Request(
                cmd=Command.GET_PROTOCOL_VERSION,
                has_res=True,
            )
        )
        return buf.decode("utf-8")

    async def get_feature_map(self) -> int:
        buf = await self._send_request(
            Request(
                cmd=Command.GET_FEATURE_MAP,
                has_res=True,
            )
        )
        return int.from_bytes(buf, byteorder="little")  # TODO: check if this is correct

    async def get_device_name(self) -> str:
        buf = await self._send_request(
            Request(
                cmd=Command.GET_DEVICE_NAME,
                has_res=True,
            )
        )
        return buf.decode("utf-8")

    async def get_firmware_revision(self) -> str:
        buf = await self._send_request(
            Request(
                cmd=Command.GET_FW_REVISION,
                has_res=True,
            )
        )
        return buf.decode("utf-8")

    async def get_hardware_revision(self) -> str:
        buf = await self._send_request(
            Request(
                cmd=Command.GET_HW_REVISION,
                has_res=True,
            )
        )
        return buf.decode("utf-8")

    async def get_model_number(self) -> str:
        buf = await self._send_request(
            Request(
                cmd=Command.GET_MODEL_NUMBER,
                has_res=True,
            )
        )
        return buf.decode("utf-8")

    async def get_serial_number(self) -> str:
        buf = await self._send_request(
            Request(
                cmd=Command.GET_SERIAL_NUMBER,
                has_res=True,
            )
        )
        return buf.decode("utf-8")

    async def get_manufacturer_name(self) -> str:
        buf = await self._send_request(
            Request(
                cmd=Command.GET_MANUFACTURER_NAME,
                has_res=True,
            )
        )

        return buf.decode("utf-8")

    async def get_bootloader_version(self) -> str:
        buf = await self._send_request(
            Request(
                cmd=Command.GET_BOOTLOADER_VERSION,
                has_res=True,
            )
        )

        return buf.decode("utf-8")

    async def get_battery_level(self) -> int:
        buf = await self._send_request(
            Request(
                cmd=Command.GET_BATTERY_LEVEL,
                has_res=True,
            )
        )
        return int.from_bytes(buf, byteorder="big")

    async def get_temperature(self) -> int:
        buf = await self._send_request(
            Request(
                cmd=Command.GET_TEMPERATURE,
                has_res=True,
            )
        )
        return int.from_bytes(buf, byteorder="big")

    async def power_off(self) -> None:
        await self._send_request(
            Request(
                cmd=Command.POWEROFF,
                has_res=False,
            )
        )

    async def system_reset(self):
        await self._send_request(
            Request(
                cmd=Command.SYSTEM_RESET,
                has_res=False,
            )
        )

    async def set_motor(self, switchStatus):
        body = [switchStatus == True]
        body = bytes(body)
        ret = await self._send_request(
            Request(
                cmd=Command.MOTOR_CONTROL,
                body=body,
                has_res=True,
            )
        )

    async def set_led(self, switchStatus):
        body = [switchStatus == True]
        body = bytes(body)
        ret = await self._send_request(
            Request(
                cmd=Command.LED_CONTROL_TEST,
                body=body,
                has_res=True,
            )
        )

    async def set_package_id(self, switchStatus):
        body = [switchStatus == True]
        body = bytes(body)
        ret = await self._send_request(
            Request(
                cmd=Command.PACKAGE_ID_CONTROL,
                body=body,
                has_res=True,
            )
        )

    async def set_log_level(self, logLevel):
        body = [0xFF & logLevel]
        body = bytes(body)
        ret = await self._send_request(
            Request(
                cmd=Command.SET_LOG_LEVEL,
                body=body,
                has_res=True,
            )
        )

    async def set_function_switch(self, funcSwitch):
        body = [0xFF & funcSwitch]
        body = bytes(body)
        ret = await self._send_request(
            Request(
                cmd=Command.SET_FUNCTION_SWITCH,
                body=body,
                has_res=True,
            )
        )

    async def set_firmware_filter_switch(self, switchStatus: int):
        body = [0xFF & switchStatus]
        body = bytes(body)
        await self._send_request(Request(cmd=Command.CMD_SET_FRIMWARE_FILTER_SWITCH, body=body, has_res=True))

    async def get_firmware_filter_switch(self):
        buf = await self._send_request(Request(cmd=Command.CMD_GET_FRIMWARE_FILTER_SWITCH, has_res=True))
        return buf[0]

    async def set_emg_raw_data_config(self, cfg=EmgRawDataConfig()):
        body = cfg.to_bytes()
        await self._send_request(
            Request(
                cmd=Command.SET_EMG_RAWDATA_CONFIG,
                body=body,
                has_res=True,
            )
        )

        # print('_send_request returned:', ret)

        self.resolution = cfg.resolution

        num_channels = 0
        ch_mask = cfg.channel_mask

        while ch_mask != 0:
            if ch_mask & 0x01 != 0:
                num_channels += 1
            ch_mask >>= 1

        self.__num_channels = num_channels

    async def get_emg_raw_data_config(self) -> EmgRawDataConfig:
        buf = await self._send_request(
            Request(
                cmd=Command.GET_EMG_RAWDATA_CONFIG,
                has_res=True,
            )
        )
        return EmgRawDataConfig.from_bytes(buf)

    async def get_eeg_raw_data_config(self) -> EegRawDataConfig:
        buf = await self._send_request(
            Request(
                cmd=Command.CMD_GET_EEG_CONFIG,
                has_res=True,
            )
        )
        return EegRawDataConfig.from_bytes(buf)

    async def get_eeg_raw_data_cap(self) -> EegRawDataCap:
        buf = await self._send_request(
            Request(
                cmd=Command.CMD_GET_EEG_CAP,
                has_res=True,
            )
        )
        return EegRawDataCap.from_bytes(buf)

    async def get_ecg_raw_data_config(self) -> EcgRawDataConfig:
        buf = await self._send_request(
            Request(
                cmd=Command.CMD_GET_ECG_CONFIG,
                has_res=True,
            )
        )
        return EcgRawDataConfig.from_bytes(buf)

    async def get_imu_raw_data_config(self) -> ImuRawDataConfig:
        buf = await self._send_request(
            Request(
                cmd=Command.CMD_GET_IMU_CONFIG,
                has_res=True,
            )
        )
        return ImuRawDataConfig.from_bytes(buf)

    async def get_brth_raw_data_config(self) -> BrthRawDataConfig:
        buf = await self._send_request(
            Request(
                cmd=Command.CMD_GET_BRT_CONFIG,
                has_res=True,
            )
        )
        return BrthRawDataConfig.from_bytes(buf)

    async def set_subscription(self, subscription: DataSubscription):
        body = [
            0xFF & subscription,
            0xFF & (subscription >> 8),
            0xFF & (subscription >> 16),
            0xFF & (subscription >> 24),
        ]
        body = bytes(body)
        await self._send_request(
            Request(
                cmd=Command.SET_DATA_NOTIF_SWITCH,
                body=body,
                has_res=True,
            )
        )

    async def start_streaming(self, q: queue.Queue):
        await sensor_utils.async_call(
            self.client.start_notify(
                self.data_char,
                lambda _, data: self._on_data_response(q, data),
            ),
            sensor_utils._TIMEOUT,
            self.gforce_event_loop,
        )

    async def stop_streaming(self):
        exceptions = []

        try:
            await sensor_utils.async_call(self.client.stop_notify(self.data_char), sensor_utils._TIMEOUT, self.gforce_event_loop)
        except Exception as e:
            exceptions.append(e)

        if len(exceptions) > 0:
            raise Exception("Failed to stop streaming: %s" % exceptions)

    async def disconnect(self):
        with suppress(asyncio.CancelledError):
            try:
                await sensor_utils.async_call(self.client.disconnect(), sensor_utils._TIMEOUT, self.gforce_event_loop)
            except Exception as e:
                pass

    def _get_response_channel(self, cmd: Command) -> Queue:
        if self.responses.get(cmd) != None:
            return self.responses[cmd]
        else:
            q = Queue()
            self.responses[cmd] = q
            return q

    async def _send_request(self, req: Request) -> Optional[bytes]:
        return await sensor_utils.async_call(self._send_request_internal(req=req), runloop=self.event_loop)

    async def _send_request_internal(self, req: Request) -> Optional[bytes]:
        q = None
        if req.has_res:
            q = self._get_response_channel(req.cmd)

        timeStamp_old = -1
        while not q.empty():
            timeStamp_old = q.get_nowait()

        now = datetime.now()
        timestamp_now = now.timestamp()
        if (timeStamp_old > -1) and ((timestamp_now - timeStamp_old) < 3):
            print("send request too fast")
            q.put_nowait(timeStamp_old)
            return None

        bs = bytes([req.cmd])
        if req.body is not None:
            bs += req.body

        # print(str(req.cmd) + str(req.body))
        try:
            await sensor_utils.async_call(
                self.client.write_gatt_char(self.cmd_char, bs),
                1,
                runloop=self.gforce_event_loop,
            )
        except Exception as e:
            self.responses[req.cmd] = None
            return None

        if not req.has_res:
            self.responses[req.cmd] = None
            return None

        try:
            ret = await asyncio.wait_for(q.get(), 2)
            now = datetime.now()
            timestamp_now = now.timestamp()
            q.put_nowait(timestamp_now)
            return ret
        except Exception as e:
            self.responses[req.cmd] = None
            return None
