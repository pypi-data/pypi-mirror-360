import os
from .helpers.exceptions import *
from .helpers.constants import DevSTATUS, Transport
from .main import ADBManager


# temp
os.environ['ADB_TRANSPORT'] = Transport.ADB_USB
os.environ['ADB_SDK'] = "28"

adb = ADBManager()

# Определяем публичное API пакета
__all__ = [
    'adb',
    'Transport',
    'ADBConnectionError',
    'ADBCommandError',
    'ADBFatalError',
    'ADBError',
]