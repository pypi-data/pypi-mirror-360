import importlib
import os
import time
from abc import abstractmethod, ABC

from adb_shell.adb_device import AdbDeviceTcp, AdbDeviceUsb
from adb_shell.auth.keygen import keygen
from adb_shell.auth.sign_cryptography import CryptographySigner

from r00logger import log
from r00system.command import exists_process, kill_process
#from ..r00adb import r00adb
from ..executors.default import DefaultShell
from ..helpers.constants import PATTERN_ADB_PROCESS
from ..helpers.exceptions import *
from ..helpers.utils import ADBScheme, wait_close_android_studio


class ITransport(ABC):
    def __init__(self, scheme: ADBScheme):
        self.scheme = scheme
        self._executor = None

    @abstractmethod
    def connect(self, timeout=60) -> DefaultShell:
        raise NotImplementedError("Метод connect() должен быть реализован в подклассах.")

    def ChoiceExecutor(self, *args):
        clsname = self.__class__.__name__
        try:
            transport = clsname.replace('Connection', '')
            module_name = f'..executors.sdk{self.scheme.sdk}.{transport.lower()}'
            class_name = transport.capitalize() + 'Shell'
            module = importlib.import_module(module_name, package=__package__)
            self._executor = getattr(module, class_name)(*args)
            return self._executor
        except AttributeError:
            log.error("Не удалось найти класс для подключения")
            raise ValueError(f"Динамический импорт на основе класса подключения: {clsname} и версии SDK: {self.scheme.sdk} не найден.")


class ADBConnection(ITransport):
    def _connect_usb(self) -> None:
        device = adb.get_device()
        if device.is_valid_status:
            self.scheme.host = adb.host
            return
        else:
            adb.restart_server()
        raise ADBConnectionError(f"Девайс не подключен по USB, {device}")

    def _connect_wifi(self) -> None:
        if not self.scheme.host:
            raise ADBFatalError("Для подключения по ADB Wi-Fi необходимо указать IP-адрес устройства.")

        if adb.connect_wifi():
            return
        raise ADBConnectionError("Не удалось подключиться к устройству по ADB Wi-Fi")

    def connect(self, timeout=60) -> DefaultShell | None:
        """
        Проверяет доступность устройства через 'r00adb devices' и создает исполнителя ExecutorAdbHost.

        :param timeout: Общий таймаут для операций проверки (примерно).
        :return: Экземпляр IShellExecutor (ExecutorAdbHost).
        :raises ADBConnectionError: Если устройство не найдено или недоступно.
        """
        adb.set_serial(self.scheme.host, self.scheme.port)
        is_usb = True if self.scheme.transport == 'adbusb' else False
        self._connect_usb() if is_usb else self._connect_wifi()
        return self.ChoiceExecutor(adb, self.scheme)



class SSHConnection(ITransport):
    def connect(self, timeout=60):
        pass




















#
# class RAWConnection(ITransport):
#     def connect(self, timeout=60) -> DefaultShell:
#         # --- Выбор транспорта ---
#         if self.scheme.transport == 'rawwifi':
#             conn = AdbDeviceTcp(host=self.scheme.host, port=self.scheme.port, default_transport_timeout_s=timeout)
#         else:
#             serial = self.scheme.host if self.scheme.host else None
#             conn = AdbDeviceUsb(serial=serial, default_transport_timeout_s=timeout)
#
#         # --- Подключение ---
#         if isinstance(conn, AdbDeviceTcp):
#             r00adb.set_serial(self.scheme.host, self.scheme.port)
#             r00adb.tcpip()
#
#         selected_rsa_keys = self.get_rsa_keys()
#         wait_close_android_studio()
#         if exists_process(PATTERN_ADB_PROCESS):
#             kill_process(PATTERN_ADB_PROCESS)
#             time.sleep(.5)
#
#         try:
#             # Пытаемся подключиться к устройству, используя транспорт r00adb-shell
#             conn.connect(
#                 rsa_keys=selected_rsa_keys,
#                 transport_timeout_s=timeout,
#                 auth_timeout_s=timeout,
#                 read_timeout_s=timeout,
#             )
#
#             # Проверяет доступность устройства
#             if not conn.available:
#                 raise ADBConnectionError("Не удалось подключиться к устройству.")
#             return self.ChoiceExecutor(conn, self.scheme)
#
#         except Exception as e:
#             raise ADBConnectionError(f"Не удалось подключиться к ADB устройству {self.scheme}: {e}") from e
#
#     @staticmethod
#     def ensure_adb_keys() -> str:
#         """Проверяет наличие ключей ADB и генерирует их при необходимости."""
#         private_key_path = os.path.expanduser("~/.android/adbkey")
#         public_key_path = private_key_path + ".pub"
#
#         if not os.path.exists(private_key_path) or not os.path.exists(public_key_path):
#             adb_key_dir = os.path.expanduser("~/.android")
#             os.makedirs(adb_key_dir, exist_ok=True)
#             log.info(f"Генерация новой пары ключей RSA в: {private_key_path}")
#             try:
#                 keygen(private_key_path)
#                 log.info(f"Ключи сгенерированы: {private_key_path}, {public_key_path}")
#             except Exception as e:
#                 log.critical(f"ОШИБКА при генерации ключей: {e}")
#                 raise ADBConnectionError(f"Не удалось сгенерировать ключи: {e}")
#
#             # Дополнительная проверка после генерации
#             if not os.path.exists(private_key_path) or not os.path.exists(public_key_path):
#                 log.critical("ОШИБКА: RSA ключи не были созданы после генерации. Проверьте права доступа.")
#                 raise ADBConnectionError("Ключи не найдены после попытки генерации.")
#         else:
#             log.trace(f"Используются существующие ключи: {private_key_path}, {public_key_path}")
#         return private_key_path
#
#     def get_rsa_keys(self) -> list:
#         private_key_path = self.ensure_adb_keys()
#
#         try:
#             signer_graphy = CryptographySigner(private_key_path)
#             rsa_keys_list_graphy = [signer_graphy]
#             log.info("Создан подписчик CryptographySigner.")
#             return rsa_keys_list_graphy
#
#             # Баг - вылазиет окно с подтверждением ключа на телефоне - не использовать
#             # signer_rsa = PythonRSASigner.FromRSAKeyPath(private_key_path)
#             # rsa_keys_list_rsa = [signer_rsa]
#             # log.info("Создан подписчик PythonRSASigner.")
#             # return rsa_keys_list_rsa
#
#             # Рабочий
#             # signer_crypto = PycryptodomeAuthSigner(private_key_path)
#             # rsa_keys_list_crypto = [signer_crypto]
#             # return rsa_keys_list_crypto
#         except Exception as e:
#             raise ADBConnectionError(f"Ошибка при создании подписчика (rsa_keys): {e}")
