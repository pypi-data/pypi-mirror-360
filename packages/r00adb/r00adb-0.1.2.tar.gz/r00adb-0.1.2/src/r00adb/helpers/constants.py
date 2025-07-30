from dataclasses import dataclass
from typing import FrozenSet, Optional

from r00pykit.text import is_ipv4_addres


@dataclass
class Transport:
    ADB_USB = 'adbusb'
    ADB_WIFI = 'adbwifi'
    SSH = 'ssh'


class Device:
    def __init__(self):
        self.transport = None
        self._sdk: int = 0
        self.host: Optional[str] = None
        self._port: int = 0
        self.status: Optional[str] = None
        self.status_valid: bool = False

    def __str__(self):
        return f"Device(transport={self.transport}, sdk={self.sdk}, host={self.host}, port={self.port}, status={self.status}, status_valid={self.status_valid})"

    def __repr__(self):
        return self.__str__()

    @property
    def sdk(self):
        return self._sdk

    @sdk.setter
    def sdk(self, value: int):
        if value:
            self._sdk = int(value)

    @property
    def port(self):
        if not self._port and self.host and is_ipv4_addres(self.host):
            self.port = 5555
        return self._port

    @port.setter
    def port(self, value: int):
        if value:
            self._port = int(value)



SHELL_TIMEOUT = 60
MAX_LOG_RESULT_LEN = 200
ERROR_SHELL_PATTERNS = [
    # Строки:
    'Read-only file system',
    'Permission denied',
    'Operation not permitted',
    'No such file or directory',
    'Not a directory',
    'Invalid argument',
    'Illegal option',
    'Usage:',
    'unknown option',
    'grep: ',  # Частое начало ошибки grep
    'Out of memory',
    'Killed',
    "Error:",
    "Exception:",
    "Failed to",
    "does not exist",
    ": not found"
]

PATTERN_ADB_PROCESS = "r00adb.*server"


@dataclass
class DevSTATUS:
    """Device status constants."""
    UNAUTHORIZED: str = "unauthorized"
    DISCONNECTED: str = "disconnected"
    DEVICE: str = "device"
    OFFLINE: str = "offline"
    RECOVERY: str = "recovery"
    NO_DEVICE: str = "no_device"
    NORMAL_MODE: str = "normal_mode"
    DOWNLOAD_MODE: str = "download_mode"
    INVALIDS_STATUSES: FrozenSet[str] = frozenset({
        "unauthorized",
        "disconnected",
        "offline",
        "no_device",
        "no permissions"
    })

    VALIDS_STATUSES: FrozenSet[str] = frozenset({
        "device",
        "recovery",
    })
