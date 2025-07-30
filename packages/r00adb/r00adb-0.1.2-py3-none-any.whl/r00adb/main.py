import os
from typing import List

from r00logger import log
from . import Transport
from .executors.default import DefaultShell
from .helpers.constants import Device
from .helpers.exceptions import *


class ADBManager:
    def __init__(self):
        self._executor: Optional[DefaultShell] = None
        self.device = Device()

    @property
    def twrp(self):
        self._ensure_connected()
        return self._executor.twrp

    @property
    def is_connected(self) -> bool:
        """Проверяет, установлено ли активное подключение."""
        return self._executor is not None

    def _select_transport(self) -> DefaultShell:
        # Выбираем транспорт общения с телефоном
        if self.device.transport in ["adbusb", "adbwifi"]:
            if self.device.sdk >= 28:  # Упрощенная проверка
                from .executors.sdk28.adb import AdbExecutor
                executor = AdbExecutor(self.device)
            else:
                raise NotImplementedError(
                    f"Поддержка SDK {self.device.sdk} не реализована для транспорта {self.device.transport}.")
        elif self.device.transport == "ssh":
            if self.device.sdk >= 28:
                from .executors.sdk28.ssh import SSHExecutor
                executor = SSHExecutor(self.device)
            else:
                raise NotImplemented(
                    f"Поддержка SDK {self.device.sdk} не реализована для транспорта {self.device.transport}.")
        else:
            raise ValueError(
                f"Неизвестный транспорт: {self.device.transport}. Поддерживаются только 'adbusb', 'adbwifi' и 'ssh'.")
        return executor

    def _ensure_connected(self):
        """
        Проверяет наличие подключения. Если его нет, пытается подключиться автоматически
        с использованием переменных окружения.
        """
        if self.is_connected:
            return

        # Transport
        if not self.device.transport:
            self.device.transport = os.getenv('ADB_TRANSPORT') if os.getenv('ADB_TRANSPORT') else Transport.ADB_USB

        # Host
        adb_host = os.getenv('ADB_HOST')
        if adb_host:
            if not self.device.host:
                self.device.host = adb_host

        # Port
        self.device.port = os.getenv('ADB_PORT')

        # SDK
        if not self.device.sdk:
            self.device.sdk = int(os.getenv('ADB_SDK')) if os.getenv('ADB_SDK') else 28

        log.trace("Выполняется авто-подключение с использованием переменных окружения.")
        self.connect(self.device.transport, self.device.host, self.device.port, self.device.sdk)

    def connect(self, transport, host, port, sdk) -> None:
        self.device.transport = transport
        self.device.host = host
        self.device.port = port
        self.device.sdk = sdk

        log.trace(f"Запрос на подключение: transport={transport}, sdk={sdk}, host={host}")
        if self.is_connected:
            log.warning("Уже существует активное подключение. Переподключаемся...")
            self.disconnect()
            self.device.status = None
            self.device.is_status_valid = False

        self._executor: DefaultShell = self._select_transport()
        self._executor.connect()
        log.info(f"Подключение к устройству установлено! -> {self.device}")

    def disconnect(self):
        """Закрывает текущее подключение, вызывая метод close() исполнителя."""
        if self.is_connected:
            log.debug("Закрытие ADB подключения.")
            try:
                self._executor.close()
            except Exception as e:
                log.warning(f"Ошибка при закрытии соединения исполнителя: {e}")
            finally:
                self._executor = None

    # --- МЕТОДЫ-ПРОКСИ к DefaultShell ---
    def shell(self, command: str, timeout: Optional[int] = None, ignore_errors: bool = False, background: bool = False,
              verbose: bool = False, su: bool = False, log_off: bool = False, stream: bool = False) -> Optional[str]:
        self._ensure_connected()
        return self._executor.shell(command=command, timeout=timeout, ignore_errors=ignore_errors,
                                    background=background, verbose=verbose, su=su, log_off=log_off,
                                    stream=stream)

    def push(self, local: str, remote: str, timeout=300) -> str:
        self._ensure_connected()
        return self._executor.push(local=local, remote=remote, timeout=timeout)

    def pull(self, remote: str, local: str, timeout=300) -> str:
        self._ensure_connected()
        return self._executor.pull(remote=remote, local=local, timeout=timeout)

    def pull_dir(self, remote_dir: str, local_dir: str, timeout: int = 300) -> str:
        self._ensure_connected()
        return self._executor.pull_dir(remote_dir=remote_dir, local_dir=local_dir, timeout=timeout)

    def reboot(self, download_mode: bool = False, recovery_mode: bool = False, sleep: int = 18, force: bool = False, su: bool = False) -> bool:
        self._ensure_connected()
        log.warning("Выполняется перезагрузка. Соединение будет восстановлено")
        try:
            self._executor.reboot(download_mode=download_mode, recovery_mode=recovery_mode, sleep=sleep, force=force, su=su)
        finally:
            self._executor = None

        if not download_mode:
            self.connect(self.device.transport, self.device.host, self.device.port, self.device.sdk)
        return True

    def start_app(self, package_name: str, timeout: int = 60, no_wait: bool = False, ignore_errors: bool = False) -> bool:
        self._ensure_connected()
        return self._executor.start_app(package_name=package_name, timeout=timeout, no_wait=no_wait, ignore_errors=ignore_errors)

    def stop_app(self, package_name: str, timeout: int = 60, su: bool = False, ignore_errors: bool = True) -> None:
        self._ensure_connected()
        self._executor.stop_app(package_name=package_name, timeout=timeout, su=su, ignore_errors=ignore_errors)

    def list_dir(self, dir_path: str, su: bool = False, timeout: Optional[int] = 30, ignore_errors: bool = False) -> List[str]:
        self._ensure_connected()
        return self._executor.list_dir(dir_path=dir_path, su=su, timeout=timeout, ignore_errors=ignore_errors)

    def get_pid(self, package: str, su: bool = False) -> str:
        self._ensure_connected()
        return self._executor.get_pid(package=package, su=su)

    def chmod(self, path: str, mode: str, su: bool = False, ignore_errors: bool = False) -> str:
        self._ensure_connected()
        return self._executor.chmod(path=path, mode=mode, su=su, ignore_errors=ignore_errors)

    def remove(self, path: str, remove_self: bool = False, su: bool = False, ignore_errors: bool = False,
               timeout: Optional[int] = None) -> str:
        self._ensure_connected()
        return self._executor.remove(path=path, remove_self=remove_self, su=su, ignore_errors=ignore_errors,
                                     timeout=timeout)

    def mkdir(self, path: str, su: bool = False, ignore_errors: bool = False) -> str:
        self._ensure_connected()
        return self._executor.mkdir(path=path, su=su, ignore_errors=ignore_errors)

    def kill(self, match: str, su: bool = False, ignore_errors: bool = True) -> str:
        self._ensure_connected()
        return self._executor.kill(match=match, su=su, ignore_errors=ignore_errors)

    def exists(self, path: str, su: bool = False) -> bool:
        self._ensure_connected()
        return self._executor.exists(path=path, su=su)

    def is_file(self, path: str, su: bool = False) -> bool:
        self._ensure_connected()
        return self._executor.is_file(path=path, su=su)

    def is_dir(self, path: str, su: bool = False) -> bool:
        self._ensure_connected()
        return self._executor.is_dir(path=path, su=su)

    def is_twrp_mode(self) -> bool:
        self._ensure_connected()
        return self._executor.is_twrp_mode()

    def get_prop(self, prop_name: str, su: bool = False) -> str:
        self._ensure_connected()
        return self._executor.get_prop(prop_name=prop_name, su=su)

    def touch(self, path: str, su: bool = False, ignore_errors: bool = False) -> str:
        self._ensure_connected()
        return self._executor.touch(path=path, su=su, ignore_errors=ignore_errors)


