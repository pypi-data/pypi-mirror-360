import os
import shutil
import subprocess
import time
from pathlib import Path

from r00logger import log, log_result
from ..default import DefaultShell
from ...adbase import adbase
from ...helpers.constants import Device, SHELL_TIMEOUT
from ...helpers.constants import Transport
from ...helpers.exceptions import *


class AdbExecutor(DefaultShell):
    def __init__(self, device: Device):
        self.device = device
        super().__init__(device)

    def exec(self,
             command: str,
             timeout: Optional[int] = None,
             ignore_errors: bool = False,
             background: bool = False,
             verbose: bool = False,
             su: bool = False,
             log_off: bool = False,
             stream: bool = False) -> Union[str, subprocess.Popen]:
        timeout = timeout if timeout else SHELL_TIMEOUT
        if su: command = f"\"su -c '{command}'\""
        command = f'-s {self.device.host} {command}'
        cmdres = adbase.exec(command, timeout, True, background, verbose, log_off, stream)

        if isinstance(cmdres, subprocess.Popen):
            return cmdres

        if ignore_errors:
            if cmdres.failed or background:
                return ''
            return cmdres.output.strip()
        return self._check_error_patterns_for_shell(cmdres.output, command, ignore_errors)

    def shell(self,
              command: str,
              timeout: Optional[int] = None,
              ignore_errors=False,
              background: bool = False,
              verbose=False,
              su=False,
              log_off: bool = False,
              stream: bool=False) -> Union[str, subprocess.Popen, None]:
        command = f'shell {command}'
        return self.exec(command, timeout, ignore_errors, background, verbose, su, log_off, stream)

    def connect(self):
        t0 = time.time()
        timeout = 180
        while time.time() - t0 < timeout:
            device = adbase.get_device(serial=self.device.host, repeat=1)
            if device:
                device_status = device.get('status')
                if device_status:
                    self.device.status = device_status

                if device['status_valid']:
                    self.device.status_valid = True
                    self.device.host = device['serial']
                else:
                    self.device.status_valid = False

            if self.device.transport == Transport.ADB_USB:
                if self.device.status_valid:
                    if 'uid=' in self.shell('id', log_off=True):
                        return True
                    timeleft = timeout - (time.time() - t0)
                    log.warning(f"Ожидаем когда телефон ответит: timeleft: {int(timeleft)} сек, {self.device}")
                    time.sleep(2)
                    continue
                else:
                    adbase.restart_server()

            elif self.device.transport == Transport.ADB_WIFI:
                connect_result = adbase.exec(f'connect {self.device.host}', ignore_errors=True, timeout=15)

                if 'Connection refused' in connect_result.output:
                    log.warning(connect_result.output)
                    adbase.tcpip(self.device.port)
                    time.sleep(3)

                elif f'connected to {self.device.host}' in connect_result.output:
                    if self.device.status_valid:
                        return True

                elif 'unauthorized' == self.device.status:
                    log.warning("Устройство не авторизовано. Проверьте экран устройства и подтвердите RSA-ключ!")
                    time.sleep(10)
                    adbase.restart_server()

                elif 'offline' in self.device.status:
                    log.warning("Устройство недоступно. Пытаемся перезапустить ADB сервер")
                    adbase.restart_server()
                    time.sleep(5)
                    continue

                elif 'failed to authenticate' in connect_result.output:
                    log.warning("Устройство не авторизовано. Проверьте экран устройства и подтвердите RSA-ключ")
                    adbase.restart_server()
                    time.sleep(5)
                else:
                    log.error(f"Устройство имеет не валидный статус: {self.device.status}")
            else:
                raise ValueError("Неизвестный транспорт")
        else:
            raise ADBError(f"Не удалось подключиться к устройству: {self.device}")

    def close(self):
        self.exec('disconnect', ignore_errors=True)

    def push(self, local: str, remote: str, timeout=300) -> str:
        if not isinstance(local, str): local = str(local)
        log.debug(f"Пушим файл на устройство: {local} -> {remote}")
        if self.is_dir(remote):
            remote = os.path.join(remote, os.path.basename(local))
        adbase.exec(f'push {local} {remote}', timeout=300)
        if not self.exists(remote):
            raise ADBError(f'Failed to push: {local} to {remote}')
        return remote

    def pull(self, remote: str, local: str, timeout: int = 300) -> str:
        """
        Скачивает файл или директорию с устройства на хост, автоматически
        определяя тип удаленного объекта.

        - Если `remote` - это файл:
          - Если `local` - путь к файлу: файл будет скопирован и переименован.
          - Если `local` - путь к директории: файл будет скопирован в эту директорию с исходным именем.

        - Если `remote` - это директория:
          - `local` должен быть путем к директории на хосте.
          - Содержимое `remote` будет скопировано в `local`. Если в `local` уже существует
            папка с тем же именем, что у `remote`, она будет перезаписана.

        :param remote: Путь к файлу или директории на устройстве.
        :param local: Путь к файлу или директории на хосте.
        :param timeout: Время ожидания выполнения команды в секундах.
        :return: Строка с финальным путем к скачанному файлу или директории на хосте.
        :raises ADBError: Если удаленный путь не существует или возникают другие ошибки ADB.
        :raises OSError: Если локальный путь некорректен (например, файл вместо папки).
        """
        if not self.exists(remote):
            raise ADBError(f"Удаленный путь '{remote}' не существует на устройстве.")

        # Нормализация локального пути
        local_path = Path(local).expanduser().resolve()

        if self.is_dir(remote):
            # --- Логика для ДИРЕКТОРИИ ---
            log.debug(f"Удаленный путь '{remote}' определен как директория. Скачивание в '{local_path}'...")

            # Убеждаемся, что локальный путь - это директория (или ее можно создать)
            if local_path.exists() and not local_path.is_dir():
                raise OSError(f"Локальный путь '{local_path}' существует, но не является директорией.")
            local_path.mkdir(parents=True, exist_ok=True)

            # `r00adb pull` копирует `remote` *внутрь* `local`.
            # Определяем имя удаленной папки, чтобы найти ее на хосте после копирования.
            remote_folder_name = Path(remote.strip('/')).name
            final_local_path = local_path / remote_folder_name

            # Очищаем место назначения, если оно уже существует, чтобы избежать конфликтов
            if final_local_path.exists():
                log.warning(f"Целевой путь '{final_local_path}' уже существует. Перезаписываем.")
                if final_local_path.is_dir():
                    shutil.rmtree(final_local_path)
                else:
                    final_local_path.unlink()

            # Выполняем команду pull. ADB сам создаст папку `remote_folder_name` внутри `local_path`.
            self.exec(f'pull "{remote}" "{local_path}"', timeout=timeout)

            if not final_local_path.is_dir():
                raise ADBError(f"Не удалось скопировать директорию '{remote}'. "
                               f"Целевой путь '{final_local_path}' не найден или не является директорией.")

            log.debug(f"Директория успешно скачана: '{remote}' -> '{final_local_path}'")
            return str(final_local_path)
        else:
            # --- Логика для ФАЙЛА ---
            log.debug(f"Удаленный путь '{remote}' определен как файл. Скачивание в '{local_path}'...")

            final_local_path = local_path
            # Если локальный путь указывает на существующую директорию,
            # файл будет скопирован в нее с сохранением имени.
            if local_path.is_dir():
                final_local_path = local_path / Path(remote).name
            else:
                # Если `local_path` - это путь к файлу, убедимся, что его родительская папка существует.
                final_local_path.parent.mkdir(parents=True, exist_ok=True)

            # Выполняем команду pull
            self.exec(f'pull "{remote}" "{final_local_path}"', timeout=timeout)

            if not final_local_path.exists():
                raise ADBError(f"Не удалось скачать файл: '{remote}' -> '{final_local_path}'")

            log.debug(f"Файл успешно скачан: '{remote}' -> '{final_local_path}'")
            return str(final_local_path)
