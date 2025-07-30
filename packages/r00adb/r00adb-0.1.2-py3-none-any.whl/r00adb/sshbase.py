import socket
import time

from r00logger import log
from system import CMDResult
from .helpers.constants import Device


class SSHBase:
    def __init__(self, device: Device):
        self.device = device

    def exec(self,
             command: str,
             timeout: int = 60,
             background: bool = False,
             stream: bool = False,
             log_off: bool = False,
             raw: bool = False
             ) -> CMDResult:
        """
        Выполняет произвольную ADB команду на хосте.

        :param command: Команда для выполнения.
        :param timeout: Время ожидания выполнения команды в секундах.
        :param background: Выполняет команду в фоновом режиме без результата
        :param stream: Выводить результат команды в real-time.
        :param log_off: Отключить логированние
        :param raw: для push, pull
        :return: Объект CmdResult или subprocess.Popen (stream режим)
        """
        if background:
            return self._background_command(command, log_off)
        elif stream:
            return self._stream_command(command, log_off)
        elif raw:
            return self._raw_command(command, timeout, log_off)
        else:
            return self._base_command(command, timeout, log_off)

    def _raw_command(self, command: str, timeout: int, log_off: bool) -> CMDResult:
        """
        Выполняет команду и возвращает ее stdout как сырые байты.
        Использует маркер в stderr для определения конца вывода stdout.
        """
        ECHO_BOUNDARY = b"x_x_x_RAW_DONE_x_x_x"
        # Выводим маркер в stderr, чтобы он не смешался с stdout файла
        full_cmd = f"{command}; echo {ECHO_BOUNDARY.decode()} >&2\n"

        if not log_off:
            log.trace(f"⚙️ RAW command: {command}")

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                s.connect((self.device.host, self.device.port))
                s.sendall(full_cmd.encode())

                response_buffer = b""
                # --- ИСПРАВЛЕННАЯ ЛОГИКА ЧТЕНИЯ ---
                while ECHO_BOUNDARY not in response_buffer:
                    chunk = s.recv(65536)  # Читаем порциями
                    if not chunk:
                        log.warning("Connection closed unexpectedly before boundary was received.")
                        break
                    response_buffer += chunk

                # Теперь, когда у нас есть все данные (включая маркер),
                # мы можем их разделить.
                # Все, что было до маркера, — это stdout + stderr.
                # Так как маркер был в stderr, он пришел после stdout файла.
                parts = response_buffer.split(ECHO_BOUNDARY)

                # Первый элемент - это то, что нам нужно (данные файла + возможный мусор из stderr).
                # Поскольку мы использовали `cat`, он выводит только содержимое файла в stdout.
                # Другие команды могут выводить что-то в stderr до нашего маркера,
                # но для `cat` и `tar -f -` это безопасно.
                raw_output = parts[0]

                # Очень простая очистка, если `cat` вывел перевод строки в конце
                # и маркер "прилип" к нему. Это может быть неидеально, но часто работает.
                # Пример вывода: b'content\nmarker'
                # Нужно отделить контент от маркера.
                # Более надежный способ - просто принять, что все до маркера - это данные.

                # В данном случае `split` уже все сделал правильно.
                # `parts[0]` будет содержать `b'lololo\n'`.
                # `parts[1]` будет содержать `b'\n'` и остатки.

            # `raw_output` теперь содержит только данные файла.
            return CMDResult(command, _stdout=raw_output, return_code=0)

        except Exception as e:
            if not log_off:
                log.warning(f"An unexpected error occurred during raw command: {e}")
            return CMDResult(command, _stderr=str(e).encode(), return_code=1)

    def _base_command(self, command, timeout, log_off) -> CMDResult:
        # Добавляем команду 'echo' со случайной меткой в конец,
        # чтобы точно знать, где закончился вывод основной команды.
        ECHO_BOUNDARY = "x_x_x"
        full_cmd = f"{command}; echo {ECHO_BOUNDARY}\n"

        try:
            t0 = time.time()
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                s.connect((self.device.host, self.device.port))
                s.sendall(full_cmd.encode())

                # Читаем ответ в цикле, пока не встретим нашу метку
                response_buffer = ""
                while ECHO_BOUNDARY not in response_buffer:
                    # Читаем данные небольшими порциями, чтобы не блокироваться надолго
                    chunk = s.recv(4096).decode(errors='ignore')
                    if not chunk:
                        # Сокет закрылся раньше времени
                        log.warning("Connection closed")
                        break
                    response_buffer += chunk

                # Убираем нашу команду и метку из ответа для чистоты
                # Сначала убираем метку и все, что после нее
                clean_response = response_buffer.split(ECHO_BOUNDARY)[0]
                # Затем убираем саму команду, которую мы отправили
                if clean_response.startswith(full_cmd.strip()):
                    clean_response = clean_response[len(full_cmd.strip()):].lstrip()

                output = clean_response.strip()
                elapsed = time.time() - t0
                if not log_off:
                    log.trace(f"⚙️ [{elapsed:.2f}] {command} -> {output}")
                return CMDResult(command, _stdout=output.encode(), return_code=0)

        except Exception as e:
            if not log_off:
                log.warning(f"An unexpected error occurred: {e}")
            return CMDResult(command, _stderr=str(e).encode(), return_code=1)

    def _background_command(self, command, log_off):
        if not log_off:
            log.trace(f"⚙️ Background command: {command}")
        # Для фоновой задачи мы хотим, чтобы она не завершилась, когда оболочка закроется.
        # Оборачиваем команду в 'nohup ... &'
        # Добавляем \n для выполнения.
        nohup_cmd = f"nohup {command} > /dev/null 2>&1 &\n"
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                # Для фоновой задачи достаточно короткого таймаута на подключение
                s.settimeout(5)
                s.connect((self.device.host, self.device.port))
                s.sendall(nohup_cmd.encode())
                # Мы не ждем ответа, просто закрываем соединение.
            return CMDResult(command, _stdout="Command sent to background.".encode(), return_code=0)
        except Exception as e:
            if not log_off:
                log.warning(f"Failed to send background command: {e}")
            return CMDResult(command, _stderr=str(e).encode(), return_code=1)

    def _stream_command(self, cmd: str, log_off) -> CMDResult:
        full_cmd = f"{cmd}\n"
        if not log_off:
            log.info(f"Starting real-time stream for: '{cmd}'")
            log.info("Press Ctrl+C to stop.")

        received_data = []
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(10)
                s.connect((self.device.host, self.device.port))
                s.sendall(full_cmd.encode())

                while True:
                    chunk = s.recv(4096)
                    if not chunk:
                        if not log_off:
                            log.warning("\nConnection closed by remote host.")
                        break
                    print(chunk.decode(errors='ignore'), end='', flush=True)
                    received_data.append(chunk)

            output = b"".join(received_data).decode(errors='ignore')
            return CMDResult(cmd, _stdout=output.encode(), return_code=0)

        except socket.timeout:
            if not log_off:
                log.error("\nConnection timed out.")
            output = b"".join(received_data).decode(errors='ignore')
            return CMDResult(cmd, _stdout=output.encode(), _stderr="Connection timed out.".encode(), return_code=1)
        except KeyboardInterrupt:
            print()
            if not log_off:
                log.info("Stopped by user.")
            output = b"".join(received_data).decode(errors='ignore')
            return CMDResult(cmd, _stdout=output.encode(), return_code=0)
        except Exception as e:
            if not log_off:
                log.error(f"\nAn unexpected error occurred during streaming: {e}")
            output = b"".join(received_data).decode(errors='ignore')
            return CMDResult(cmd, _stdout=output.encode(), _stderr=str(e).encode(), return_code=1)
