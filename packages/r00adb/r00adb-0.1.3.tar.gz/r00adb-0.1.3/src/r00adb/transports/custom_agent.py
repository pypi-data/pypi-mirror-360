import socket
from logger import log
from ..helpers.exceptions import *
import time # Добавим для задержек при чтении


# Маркер конца строки, используемый агентом в ответе для SHELL команд
# (Предполагается, что агент заменяет \n в выводе команды на этот маркер)
NEWLINE_MARKER = '|' # Простой пример, лучше использовать менее вероятный символ

class CustomAgentTransport:
    """
    Manages TCP connection and communication with a custom C agent
    running on the Android device, bypassing adbd.
    Implements a simple line-based protocol.
    """
    def __init__(self, host: str, port: int, timeout: float = 10.0):
        self.host = host
        self.port = port
        self.timeout = timeout
        self._socket: socket.socket | None = None
        self._buffer = b"" # Буфер для чтения по одной строке
        log.info(f"CustomAgentTransport created for {host}:{port}")

    def connect(self):
        """Establishes the TCP connection to the agent."""
        if self._socket:
            log.warning("Attempted to connect when already connected.")
            return # Or raise an error? If connection is bad, subsequent calls will fail.

        log.debug(f"Connecting to custom agent at {self.host}:{self.port}...")
        try:
            # socket.create_connection handles getaddrinfo and connect with timeout
            self._socket = socket.create_connection((self.host, self.port), timeout=self.timeout)
            self._socket.settimeout(self.timeout) # Set default timeout for subsequent operations
            self._buffer = b"" # Сброс буфера при новом подключении
            log.info(f"Successfully connected to custom agent at {self.host}:{self.port}")
            # === НЕОБЯЗАТЕЛЬНО: Логика рукопожатия/аутентификации ===
            # Если ваш агент требует какой-то первоначальный обмен данными
            # self._socket.sendall(b"AUTH_SECRET\n")
            # response = self._read_line(timeout=self.timeout) # Читаем ответ на аутентификацию
            # if response != "AUTH_OK":
            #     self.close()
            #     raise ConnectionError("Custom agent authentication failed.")
            # =======================================================
        except socket.timeout:
            self._socket = None
            log.error(f"Connection timed out to custom agent at {self.host}:{self.port}")
            raise ConnectionError(f"Connection timed out to custom agent at {self.host}:{self.port}")
        except socket.error as e:
            self._socket = None
            log.error(f"Socket error connecting to custom agent at {self.host}:{self.port}: {e}", exc_info=True)
            raise ConnectionError(f"Could not connect to custom agent at {self.host}:{self.port}: {e}") from e
        except Exception as e:
             self._socket = None
             log.exception(f"Unexpected error connecting to custom agent at {self.host}:{self.port}: {e}")
             raise ConnectionError(f"Unexpected error connecting to custom agent: {e}") from e


    def close(self):
        """Closes the TCP connection."""
        if self._socket:
            log.debug("Closing connection to custom agent.")
            try:
                # Попытка послать команду EXIT перед закрытием, если сокет еще пригоден
                # Используем короткий таймаут для этой последней команды
                try:
                    # Временно убираем таймаут, чтобы sendall не выкинул socket.timeout сразу
                    self._socket.settimeout(1.0)
                    self._send_command_raw("EXIT") # Используем метод без обработки ответа
                except socket.error:
                    log.warning("Failed to send EXIT command during close, socket likely broken.")
                except Exception as e:
                     log.warning(f"Ignoring error sending EXIT command: {e}")

                # Теперь закрываем сокет
                self._socket.shutdown(socket.SHUT_RDWR) # Gracefully shutdown
                self._socket.close()
            except socket.error as e:
                # Игнорируем ошибки при закрытии, т.к. часто они несущественны после shutdown
                log.warning(f"Socket error during close: {e}")
            except Exception as e:
                 log.warning(f"Unexpected error during socket close: {e}", exc_info=True)
            finally:
                self._socket = None
                self._buffer = b"" # Очистка буфера
                log.info("Connection to custom agent closed.")
        else:
            log.debug("Attempted to close an already closed custom agent connection.")


    def _send_command_raw(self, command: str):
        """Internal helper to send a command string without waiting for a response marker."""
        if not self._socket:
            raise ADBADBTransportError("Not connected to custom agent.")
        # log.debug(f"Sending raw command: {command.strip()}") # Отключаем логгирование чувствительных команд
        try:
            command_bytes = (command + '\n').encode('utf-8')
            self._socket.sendall(command_bytes)
        except socket.timeout:
             log.error("Timeout sending command to custom agent.")
             self.close()
             raise ADBADBTransportError("Timeout sending command to custom agent.")
        except socket.error as e:
            log.error(f"Socket error sending command: {e}", exc_info=True)
            self.close()
            raise ADBADBTransportError(f"Socket error sending command: {e}") from e

    def _read_line(self, timeout: float | None = None) -> str:
        """Internal helper to read a single line ending with \\n from the socket buffer."""
        if not self._socket:
            raise ADBADBTransportError("Not connected to custom agent.")

        effective_timeout = timeout if timeout is not None else self.timeout
        # log.debug(f"Reading line (timeout={effective_timeout}s)...")

        self._socket.settimeout(effective_timeout)
        try:
            while True:
                newline_pos = self._buffer.find(b'\n')
                if newline_pos != -1:
                    line = self._buffer[:newline_pos + 1]
                    self._buffer = self._buffer[newline_pos + 1:]
                    response_str = line.decode('utf-8', errors='replace').strip() # strip() удалит trailing \n
                    # log.debug(f"Read line: '{response_str}'")
                    return response_str

                # Read more data into buffer
                try:
                    chunk = self._socket.recv(4096)
                except socket.timeout:
                    # Если таймаут произошел во время чтения chunk, и в буфере нет \n
                    # Это ошибка, так как ожидалась строка с \n
                    log.error(f"Timeout reading data chunk after {effective_timeout}s, no newline found in buffer.")
                    self.close()
                    raise ADBADBTransportError(f"Timeout waiting for line ending with newline.")
                except socket.error as e:
                    log.error(f"Socket error reading chunk: {e}", exc_info=True)
                    self.close()
                    raise ADBADBTransportError(f"Socket error reading chunk: {e}") from e


                if not chunk:
                    # Сервер закрыл соединение до отправки \n
                    log.error("Connection closed by agent before newline received.")
                    self.close()
                    raise ADBADBTransportError("Connection closed by agent prematurely.")

                self._buffer += chunk

        except socket.timeout:
            # Этот блок уже не должен выполняться, т.к. таймаут ловится внутри while,
            # но оставим на всякий случай.
            log.error(f"Overall read timeout after {effective_timeout}s.")
            self.close()
            raise ADBADBTransportError(f"Read timeout after {effective_timeout}s.")
        except ADBADBTransportError: # Re-raise our own errors
             raise
        except Exception as e:
            log.exception(f"Unexpected error during _read_line: {e}")
            self.close()
            raise ADBADBTransportError(f"Unexpected error reading from agent: {e}") from e
        finally:
            # Восстанавливаем стандартный таймаут сокета
            if self._socket:
                 try: self._socket.settimeout(self.timeout)
                 except socket.error: pass # Игнорируем ошибку, если сокет уже закрыт


    def _send_and_receive_line(self, command: str, read_timeout: float | None = None) -> str:
        """Sends a command and reads a single line response, handling OK/ERROR."""
        log.debug(f"Executing agent command: {command.strip()}")
        try:
            self._send_command_raw(command)
            response_line = self._read_line(timeout=read_timeout)

            # Парсинг ответа по протоколу
            if response_line.startswith("OK"):
                 return response_line[len("OK"):].strip() # Возвращаем остаток строки после OK
            elif response_line.startswith("ERROR"):
                error_message = response_line[len("ERROR"):].strip()
                log.error(f"Agent returned error for command '{command.strip()}': {error_message}")
                raise ADBADBCommandError(f"Agent error: {error_message}")
            else:
                 # Неожиданный формат ответа
                 log.error(f"Agent returned unexpected response format: '{response_line}' for command '{command.strip()}'")
                 raise ADBTransportError(f"Unexpected response format from agent: '{response_line}'")

        except (ADBTransportError, ConnectionError) as e:
            # Ошибки транспорта или соединения уже залогированы внутри _read_line или _send_command_raw
            # или connect(). Перебрасываем как ADBCommandError для унификации API Executor'а.
            raise ADBShellError(f"Failed to communicate with agent for command '{command.strip()}': {e}") from e
        except ADBShellError: # Наша ADBCommandError от ERROR-ответа агента
             raise
        except Exception as e:
            log.exception(f"Unexpected error executing agent command: {e}")
            raise ADBShellError(f"Unexpected error executing agent command '{command.strip()}': {e}") from e


    # --- Методы, использующие протокол для конкретных действий ---

    def execute_shell_command(self, command: str, read_timeout: float | None = None) -> str:
        """
        Sends a shell command via the agent and returns the combined stdout/stderr.
        Handles the '|' marker for newlines.
        """
        # Для shell команд используем префикс SHELL
        full_command = f"SHELL {command}"
        try:
            # Ожидаем ответ OK или ERROR
            raw_result = self._send_and_receive_line(full_command, read_timeout)
            # Заменяем маркеры новой строки обратно
            result = raw_result.replace(NEWLINE_MARKER, '\n')
            log.debug(f"Shell command '{command.strip()}' executed via agent.")
            return result
        except (ADBShellError, ADBTransportError) as e:
             log.error(f"Failed to execute shell command '{command.strip()}' via custom agent: {e}")
             # _send_and_receive_line уже преобразует ошибки в ADBCommandError
             raise # Просто перебрасываем


    def get_sdk_version(self) -> int | None:
        """Attempts to get the Android SDK version via the custom agent."""
        try:
            # Используем специальную команду GET_SDK
            response = self._send_and_receive_line("GET_SDK", read_timeout=3.0) # Короткий таймаут
            if response.isdigit():
                version = int(response)
                log.info(f"Got SDK version {version} from custom agent.")
                return version
            else:
                log.warning(f"Agent returned non-integer SDK version: '{response}'")
                # Это не ошибка протокола, а ошибка данных, поднимаем ADBCommandError
                raise ADBShellError(f"Agent returned invalid SDK format: '{response}'")
        except (ADBShellError, ADBTransportError) as e:
            # Логируем ошибку, но возвращаем None, т.к. метод get_sdk_version допускает неудачу
            log.warning(f"Failed to get SDK version from custom agent: {e}")
            return None


    def start_application(self, component_name: str):
        """Requests the agent to start an application activity."""
        try:
            # Важно: Здесь нет санитизации component_name, предполагаем, что он безопасен
            # В реальном приложении нужна проверка!
            self._send_and_receive_line(f"START_APP {component_name}", read_timeout=15.0)
            log.info(f"Agent requested to start app: {component_name}")
            # Ответ "OK" означает, что команда отправлена агенту и он начал ее выполнять
        except (ADBShellError, ADBTransportError) as e:
            log.error(f"Failed to send start_app command for '{component_name}': {e}")
            raise # Перебрасываем ADBCommandError


    def file_exists(self, path: str) -> bool:
         """Checks if a file exists on the device via the agent."""
         try:
             # Важно: Санитизация path в агенте!
             response = self._send_and_receive_line(f"EXIST_FILE {path}", read_timeout=5.0)
             if response.lower() == 'true':
                 log.debug(f"Agent confirmed file exists: {path}")
                 return True
             elif response.lower() == 'false':
                 log.debug(f"Agent confirmed file does not exist: {path}")
                 return False
             else:
                 # Неожиданный ответ от агента
                 raise ADBShellError(f"Agent returned unexpected boolean value for existence check: '{response}'")
         except (ADBShellError, ADBTransportError) as e:
            log.error(f"Failed to check file existence for '{path}': {e}")
            raise # Перебрасываем ADBCommandError


    # def push_file(self, local_path: str, remote_path: str):
    #     """ Placeholder for file pushing logic. Requires protocol definition. """
    #     # Протокол push/pull по TCP гораздо сложнее простого запроса/ответа.
    #     # Возможно, агент должен открывать отдельный порт или использовать свой бинарный протокол.
    #     raise NotImplementedError("Push not implemented for custom agent yet. Requires complex protocol.")

    # def pull_file(self, remote_path: str, local_path: str):
    #     """ Placeholder for file pulling logic. Requires protocol definition. """
    #     raise NotImplementedError("Pull not implemented for custom agent yet. Requires complex protocol.")

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()