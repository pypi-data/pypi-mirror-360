import time
from typing import Protocol, List

from r00logger import log, log_script
from ..adbase import adbase
from ..helpers.constants import *
from ..helpers.exceptions import *
from ..modules.twrp import TWRP


# Для тайпхинтинга, чтобы избежать циклических импортов
class Device(Protocol):
    ...


class DefaultShell(Protocol):
    def __init__(self, device: Device):
        self.device = device
        self.twrp = TWRP(self)

    def shell(self,
              command: str,
              timeout: Optional[int] = None,
              ignore_errors: bool = False,
              background: bool = False,
              verbose: bool = False,
              su: bool = False,
              log_off: bool = False,
              stream: bool=False) -> Optional[str]:
        """
        Выполняет команду в shell устройства. Это основной метод для выполнения команд.

        :param command: Строка команды для выполнения.
        :param timeout: Максимальное время ожидания выполнения команды в секундах.
        :param ignore_errors: Если True, ошибки выполнения команды (например, ненулевой код возврата) будут проигнорированы.
        :param background: Если True, команда будет запущена в фоновом режиме, метод вернет управление немедленно.
        :param verbose: Если True, включает подробное логирование процесса выполнения команды.
        :param su: Если True, команда будет выполнена с правами суперпользователя (root) через 'su -c'.
        :param log_off: Если True, логирование для этой конкретной команды будет отключено.
        :param stream: Если True, вывод команды будет потоком.
        :return: Вывод команды в виде строки или None, если команда была запущена в фоне.
        :raises ADBCommandError: В случае ошибки выполнения команды (если ignore_errors=False).
        """
        raise NotImplemented()

    @staticmethod
    def _check_error_patterns_for_shell(output: str, command: str, ignore_errors: bool) -> str:
        for pattern in ERROR_SHELL_PATTERNS:
            if pattern.lower() in output.lower():
                msgerr = f"Найдена ошибка в shell: паттерн '{pattern}'"
                if ignore_errors:
                    log.warning(msgerr + ' -> игнорируем')
                    return output.strip()
                raise ADBCommandError(command=command, result=output, exc=msgerr)
        return output.strip()

    @log_script
    def reboot(self, download_mode: bool = False, recovery_mode: bool = False, sleep: int = 18, force: bool = False,
               su: bool = False) -> bool:
        """
        Перезагружает устройство.

        :param download_mode: Если True, перезагрузка в режим загрузчика (download mode).
        :param recovery_mode: Если True, перезагрузка в режим восстановления если уже не в нём.
        :param sleep: Время ожидания (в секундах) после отправки команды перезагрузки.
        :param force: Принудительно перезагружает устройство.
        :param su: Если True, выполняет команду от имени суперпользователя.
        """
        if download_mode:
            command = 'reboot download'
        elif recovery_mode:
            command = 'reboot recovery'
            if self.get_prop('ro.twrp.boot') and not force:
                return True
        else:
            command = 'reboot'

        try:
            t0 = time.time()
            # Команда перезагрузки часто обрывает соединение, поэтому ошибки игнорируются
            self.shell(command, timeout=sleep, ignore_errors=True, su=su)
            if download_mode:
                adbase.restart_server()
                time.sleep(10)
                return True

            while time.time() - t0 < sleep:
                time.sleep(1)
        except:
            pass

        adbase.restart_server()
        return True

    def _check_path_property(self, path: str, test_flag: str, su: bool = False) -> bool:
        """
        Внутренний метод для проверки свойства пути с использованием `test`.

        :param path: Путь на устройстве.
        :param test_flag: Флаг для команды test (e.g., '-e', '-f', '-d').
        :param su: Если True, выполняет команду от имени суперпользователя (для проверки защищенных путей).
        :return: True или False в зависимости от результата команды test.
        :raises ADBCommandError: при ошибке выполнения команды или неожиданном выводе.
        """
        command = f"test {test_flag} {path} && echo true || echo false"
        output = self.shell(command, timeout=5, ignore_errors=True, su=su).strip()
        if output == 'true':
            return True
        elif output == 'false':
            return False
        else:
            raise ADBError(f"Unexpected output from check ({test_flag}) command: '{output}' for path '{path}'")

    def is_twrp_mode(self) -> bool:
        """Проверяет, находится ли устройство в режиме TWRP."""
        if self.get_prop('ro.twrp.boot') != '1':
            return False
        return True

    def start_app(self, package_name: str, timeout: int = 60, no_wait: bool = False,
                  ignore_errors: bool = False) -> bool:
        """
        Запускает приложение на устройстве.

        :param package_name: Имя пакета приложения.
        :param timeout: Таймаут выполнения команды в секундах.
        :param no_wait: Если True, не ждет запуска приложения (выполняет команду в фоне).
        :param ignore_errors: Если True, игнорировать ошибки при запуске.
        :return: True в случае успешной отправки команды.
        """
        log.debug("Запускаем приложение: " + package_name)
        self.shell(f"monkey -p {package_name} -c android.intent.category.LAUNCHER 1",
                   timeout=timeout, background=no_wait, ignore_errors=ignore_errors)
        return True

    def stop_app(self, package_name: str, timeout: int = 60, su: bool = False, ignore_errors: bool = True) -> None:
        """
        Останавливает приложение на устройстве.

        :param package_name: Имя пакета приложения
        :param timeout: Таймаут выполнения команды в секундах.
        :param su: Если True, пытается остановить приложение с правами root.
        :param ignore_errors: Если True (по умолчанию), игнорирует ошибку, если приложение уже не запущено.
        """
        log.debug("Останавливаем приложение: " + package_name)
        self.shell("am force-stop " + package_name, timeout=timeout, su=su, ignore_errors=ignore_errors)

    def list_dir(self, dir_path: str, su: bool = False, timeout: Optional[int] = 30, ignore_errors: bool = False) -> \
    List[str]:
        """
        Получает список файлов и директорий, включая скрытые.
        Добавляет '/' в конец имен директорий.

        :param dir_path: Путь к директории на устройстве.
        :param su: Если True, выполняет команду от имени суперпользователя (для доступа к защищенным директориям).
        :param timeout: Таймаут выполнения команды в секундах.
        :param ignore_errors: Если True, вернет пустой список в случае ошибки (например, директория не найдена).
        :return: Список строк с именами файлов и папок.
        """
        command = f"ls -1aF {dir_path}"
        output = self.shell(command, su=su, timeout=timeout, ignore_errors=ignore_errors)

        if not output:
            return []

        cleaned_entries = []
        raw_entries = [item for item in output.strip().splitlines() if item not in ('./', '../')]

        for item in raw_entries:
            if item.endswith('/'):
                cleaned_entries.append(item)
            else:
                cleaned_entries.append(item.rstrip('*@=|'))

        return cleaned_entries

    def get_prop(self, prop_name: str, su: bool = False) -> str:
        """
        Получает значение системного свойства Android ('getprop').

        :param prop_name: Имя свойства.
        :param su: Если True, выполняет команду от имени суперпользователя (редко требуется).
        :return: Строковое значение свойства или пустую строку.
        """
        output = self.shell(f"getprop {prop_name}", su=su)
        return output if output else ''

    def get_pid(self, package: str, su: bool = False) -> str:
        """
        Получает PID процесса приложения по его имени пакета.

        :param package: Имя пакета приложения.
        :param su: Если True, выполняет команду от имени суперпользователя (для видимости всех процессов).
        :return: Строковое значение PID или пустую строку, если процесс не найден.
        """
        output = self.shell(f"pidof {package}", su=su).strip()
        if output:
            return output
        return ''

    def push(self, local: str, remote: str, timeout=300) -> str:
        """
        Копирует файл с локальной машины на устройство.

        :param local: Путь к локальному файлу.
        :param remote: Путь назначения на устройстве.
        :param timeout: Таймаут операции в секундах.
        :return: Возвращает путь к файлу на устройстве.
        """
        raise NotImplemented()

    def pull(self, remote: str, local: str, timeout=300) -> str:
        """
        Копирует файл или директорию с устройства на локальную машину.

        :param remote: Путь к файлу/директории на устройстве.
        :param local: Путь назначения на локальной машине.
        :param timeout: Таймаут операции в секундах.
        :return: Возвращает путь к файлу на локальной машине.
        """
        raise NotImplemented()

    def pull_dir(self, remote_dir: str, local_dir: str, timeout: int = 300) -> str:
        """
        Копирует директорию с устройства на локальную машину, сохраняя имя директории.
        Например, pull_dir("/data/local/tmp/folder", "~/temp")
        скопирует содержимое "/data/local/tmp/folder" в "~/temp/folder" на хосте.

        :param remote_dir: Путь к директории на устройстве.
        :param local_dir: Путь к родительской директории на локальной машине,в которую будет скопирована удаленная директория.
        :param timeout: Таймаут операции в секундах.
        :return: Абсолютный путь к скопированной директории на локальной машине.
        :raises ADBError: Если произошла ошибка при проверке путей или копировании.
        :raises OSError: Если локальный родительский путь является файлом.
        """
        raise NotImplemented()

    def chmod(self, path: str, mode: int|str, su: bool = False, ignore_errors: bool = False) -> str:
        """
        Изменяет права доступа к файлу/директории на устройстве ('chmod').

        :param path: Путь к файлу/директории на устройстве.
        :param mode: Режим доступа (например, '777', 'u+x').
        :param su: Если True, выполняет команду от имени суперпользователя.
        :param ignore_errors: Если True, игнорировать ошибки (например, если путь не существует).
        :return: Вывод команды chmod.
        """
        path = str(path)
        log.debug("Изменяем права доступа к файлу: " + path)
        return self.shell(f'chmod {mode} {path}', su=su, ignore_errors=ignore_errors)

    def touch(self, path: str, su: bool = False, ignore_errors: bool = False) -> str:
        """
        Создает пустой файл или обновляет время его модификации ('touch').

        :param path: Путь к файлу.
        :param su: Если True, выполняет команду от имени суперпользователя.
        :param ignore_errors: Если True, игнорировать ошибки (например, нет прав на создание).
        :return: Вывод команды touch.
        """
        if not isinstance(path, str): path = str(path)
        return self.shell(f'touch {path}', su=su, ignore_errors=ignore_errors)

    def exists(self, path: str, su: bool = False) -> bool:
        """
        Проверяет существование файла или директории на устройстве ('test -e').

        :param path: Путь на устройстве.
        :param su: Если True, выполняет проверку от имени суперпользователя (для защищенных путей).
        :return: True, если путь существует, иначе False.
        :raises ADBError: при ошибке выполнения команды или неожиданном выводе - ожидается от реализации.
        """
        if not isinstance(path, str): path = str(path)
        return self._check_path_property(path, "-e", su=su)

    def is_file(self, path: str, su: bool = False) -> bool:
        """
        Проверяет, является ли путь файлом на устройстве ('test -f').

        :param path: Путь на устройстве.
        :param su: Если True, выполняет проверку от имени суперпользователя.
        :return: True, если путь существует и является файлом, иначе False.
        :raises ADBError: при ошибке выполнения команды или неожиданном выводе - ожидается от реализации.
        """
        if not isinstance(path, str): path = str(path)
        return self._check_path_property(path, "-f", su=su)

    def is_dir(self, path: str, su: bool = False) -> bool:
        """
        Проверяет, является ли путь директорией на устройстве ('test -d').

        :param path: Путь на устройстве.
        :param su: Если True, выполняет проверку от имени суперпользователя.
        :return: True, если путь существует и является директорией, иначе False.
        :raises ADBError: при ошибке выполнения команды или неожиданном выводе - ожидается от реализации.
        """
        if not isinstance(path, str): path = str(path)
        return self._check_path_property(path, "-d", su=su)

    def remove(self, path: str, remove_self: bool = False, su: bool = False, ignore_errors: bool = False,
               timeout: Optional[int] = None) -> str:
        """
        Удаляет файл или директорию на устройстве ('rm -rf').

        :param path: Путь к файлу/директории для удаления.
        :param remove_self: Если True и path - директория, удаляет саму директорию.
                            Если False и path - директория, удаляет только ее содержимое ('path/*').
        :param su: Если True, выполняет команду от имени суперпользователя.
        :param ignore_errors: Если True, игнорировать ошибки (например, если путь не существует).
        :param timeout: Таймаут операции в секундах (полезно для удаления больших директорий).
        :return: Вывод команды rm.
        """
        if not isinstance(path, str): path = str(path)
        log.debug("Удаляем файл/директорию: " + path)
        if self.exists(path, su=su):  # Проверять существование тоже с su
            command = 'rm -rf ' + path
            if self.is_dir(path, su=su) and not remove_self:  # Проверять директорию тоже с su
                command += '/*'
            result = self.shell(command, su=su, ignore_errors=ignore_errors, timeout=timeout)
            return result
        else:
            log.trace("Путь не существует, ничего не удаляем")
            return ''

    def mkdir(self, path: str, su: bool = False, ignore_errors: bool = False) -> str:
        """
        Создает директорию на устройстве, включая родительские ('mkdir -p').

        :param path: Путь к создаваемой директории.
        :param su: Если True, выполняет команду от имени суперпользователя.
        :param ignore_errors: Если True, игнорировать ошибки (команда 'mkdir -p' не выдаст ошибку, если путь уже существует).
        :return: Вывод команды mkdir.
        """
        if not isinstance(path, str): path = str(path)
        log.trace("Создаем директорию: " + path)
        return self.shell('mkdir -p ' + path, su=su, ignore_errors=ignore_errors)

    def kill(self, match: str, su: bool = False, ignore_errors: bool = True) -> str:
        """
        Завершает процессы на устройстве, соответствующие шаблону, с помощью 'pkill'.

        :param match: Шаблон для поиска процессов (имя, часть команды и т.д.).
        :param su: Если True, выполняет команду от имени суперпользователя (для завершения системных процессов).
        :param ignore_errors: Если True (по умолчанию), игнорирует ошибку, если процесс не найден.
        :return: Вывод команды kill.
        """
        log.debug("Убиваем процессы по патерну: " + match)
        return self.shell(f'pkill -f {match}', su=su, ignore_errors=ignore_errors)

