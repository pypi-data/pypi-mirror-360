import re
import subprocess
import time
from typing import List

from r00logger import log
from system import CMDResult, run, exists_process, run_background, run_stream
from . import DevSTATUS
from .helpers.constants import PATTERN_ADB_PROCESS
from .helpers.exceptions import *
from .helpers.utils import wait_close_android_studio


class ADBase:
    @staticmethod
    def exec(
            command: str,
            timeout: int = 60,
            ignore_errors: bool = False,
            background: bool = False,
            verbose: bool = False,
            log_off: bool = False,
            stream: bool = False
    ) -> CMDResult | subprocess.Popen:
        """
        Выполняет произвольную ADB команду на хосте.

        :param command: Команда для выполнения.
        :param timeout: Время ожидания выполнения команды в секундах.
        :param ignore_errors: Если True, не вызывает исключение при ошибках выполнения команды.
        :param background: Если True, выполняет команду в фоновом режиме.
        :param verbose: Если True, показывает логи выполнения команды.
        :param log_off: Выключить все логи
        :param stream: Режим stream
        :return: Объект CmdResult или subprocess.Popen (stream режим)

        """
        # full_command = f'r00adb -s {self._host} {command}' if kwargs.get('need_serial') else f'r00adb {command}'
        full_command = f'r00adb {command}'

        if stream:
            return run_stream(full_command, ignore_errors=ignore_errors)
        else:
            if not background:
                result = run(f'r00adb {command}', timeout=timeout, ignore_errors=ignore_errors, disable_log=log_off, verbose=verbose)
            else:
                return run_background(full_command)
        if not ignore_errors and result.failed:
            exc = RuntimeError(f"Команда завершилась с return_code={result.return_code}: {result}")
            raise ADBCommandError(command=full_command, result=result.output, exc=exc)
        return result

    def kill_server(self) -> None:
        """Принудительно завершает процесс ADB сервера (`r00adb kill-server`)."""
        wait_close_android_studio()
        self.exec('kill-server', timeout=15, ignore_errors=True)
        exists_process(PATTERN_ADB_PROCESS, kill=True)
        time.sleep(.5)

    def start_server(self) -> None:
        """Запускает ADB сервер (`r00adb start-server`)."""
        self.exec('start-server', timeout=15, ignore_errors=False)

    def restart_server(self) -> None:
        """Перезапускает ADB сервер."""
        self.kill_server()
        self.start_server()

    def get_device(self, serial: str = None, repeat=3) -> dict:
        """
        Получает информацию о состоянии устройства.
        Если не установлен serial то берётся первое устройство
        """
        i = 0
        while i < repeat:
            i += 1
            devices = self.all_devices()
            if not devices:
                self.restart_server()
                time.sleep(1)
                continue

            log.trace(f"Колличество подключений: {len(devices)}")

            if not serial:
                return devices[0]

            for device in devices:
                if serial in device['serial']:
                    return device

        log.warning("Нет подключенных телефонов")
        return {}

    def all_devices(self) -> List[dict]:
        """
        Получает список всех устройств, подключенных через r00adb.
        :return: Список словарей, каждый из которых представляет устройство.
        """

        result_list = list()
        cmdres = self.exec('devices', timeout=10, ignore_errors=True)
        if cmdres.failed or cmdres.return_code != 0:
            log.warning('Не удалось выполнить команду r00adb devices')
            return result_list

        if not cmdres.output:
            log.warning("Пустой вывод от 'r00adb devices'")
            return result_list

        lines = cmdres.output.splitlines()
        header_skipped = False
        for line in lines:
            line = line.strip()
            if not line:
                continue

            if not header_skipped:
                if line.lower().startswith('list of devices attached'):
                    header_skipped = True
                continue

            # Регулярное выражение для разбора строки устройства
            match = re.match(
                r'^([a-zA-Z0-9.\-:_]+(?:\:\d+)?)\s+'  # serial (может содержать порт)
                r'(device|offline|unauthorized|connecting|authorizing|bootloader|recovery|sideload|unknown)\s*(.*)$',
                line
            )

            if match:
                serial, status, details = match.groups()
                status_valid = True if status in DevSTATUS.VALIDS_STATUSES else False
                result_list.append({
                    "serial": serial,
                    "status": status,
                    "status_valid": status_valid,
                })

            else:
                log.warning(f"Не распознана строка вывода r00adb: {line}")

        if not result_list:
            log.warning(f"Нет живых девайсов: {cmdres.output}")
            return result_list
        return result_list

    def tcpip(self, port: int = None) -> str | int:
        """ Перезапускает adbd на устройстве для прослушивания TCP/IP подключений на указанном порту. """
        if not port:
            port = 5555
        log.debug(f"Перезапускаем adbd на устройстве для прослушивания TCP/IP на порту {port}")
        cmsres = self.exec(f'tcpip {port}', ignore_errors=True)
        if cmsres.success:
            return port
        return cmsres.output


adbase = ADBase()
