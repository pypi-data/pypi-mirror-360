import base64
import io
import tarfile
import time
from pathlib import Path

from r00logger import log
from ..default import DefaultShell
from ...helpers.constants import Device
from ...helpers.exceptions import *
from ...sshbase import SSHBase


class SSHExecutor(DefaultShell):
    def __init__(self, device: Device):
        self.device = device
        self.ssh = SSHBase(device)
        super().__init__(device)

    def shell(self,
              command: str,
              timeout: Optional[int] = None,
              ignore_errors=False,
              background: bool = False,
              stream: bool = False,
              log_off: bool = False,
              raw: bool = False,
              **kwargs) -> str | bytes:
        cmdres = self.ssh.exec(command, timeout, background, stream, log_off, raw)
        if cmdres.failed and not ignore_errors:
            raise ADBError(cmdres.output)
        if raw:
            return cmdres.stdout_bytes
        return cmdres.output

    def connect(self):
        msg = f"Невозможно подключиться к устройству: {self.device}"
        t0 = time.time()
        timeout = 180
        while time.time() - t0 < timeout:
            check = self.shell('id', timeout=5)
            if 'uid=' not in check:
                log.warning(msg)
                time.sleep(3)
                continue
            return True
        raise ADBError(msg)

    def pull(self, remote: str, local: str, timeout: int = 300) -> str:
        """
        Скачивает файл или директорию с удаленного устройства через SSH.
        """
        if not self.exists(remote):
            raise ADBError(f"Удаленный путь '{remote}' не существует на устройстве.")

        local_path = Path(local).expanduser().resolve()
        is_remote_dir = self.is_dir(remote)

        if is_remote_dir:
            # --- Логика для директории (используем tar) ---
            log.debug(f"Скачивание директории через SSH (tar): {remote} -> {local}")
            local_path.mkdir(parents=True, exist_ok=True)

            # -C <path> - сменить директорию перед архивацией, чтобы избежать полных путей в архиве
            remote_parent = Path(remote.strip('/')).parent
            remote_name = Path(remote.strip('/')).name

            cmd = f"tar -c -f - -C '{remote_parent}' '{remote_name}'"
            tar_bytes = self.shell(cmd, timeout=timeout, raw=True, log_off=True)

            if not tar_bytes:
                raise ADBError(f"Не удалось получить данные для директории '{remote}'. Ответ пуст.")

            with io.BytesIO(tar_bytes) as tar_stream:
                with tarfile.open(fileobj=tar_stream, mode='r:') as tar:
                    tar.extractall(path=local_path)

            final_path = local_path / remote_name
            log.debug(f"Директория успешно распакована в '{final_path}'")
            return str(final_path)
        else:
            # --- Логика для файла (используем cat) ---
            log.debug(f"Скачивание файла через SSH (cat): {remote} -> {local}")

            final_local_path = local_path
            if local_path.is_dir():
                final_local_path = local_path / Path(remote).name
            else:
                final_local_path.parent.mkdir(parents=True, exist_ok=True)

            file_bytes = self.shell(f"cat '{remote}'", timeout=timeout, raw=True, log_off=True)
            print(f'{file_bytes=}')

            if file_bytes is None:
                raise ADBError(f"Не удалось получить данные для файла '{remote}'.")

            final_local_path.write_bytes(file_bytes)
            log.debug(f"Файл успешно сохранен в '{final_local_path}'")
            return str(final_local_path)

    def push(self, local: str, remote: str, timeout: int = 300) -> str:
        """
        Загружает файл или директорию на удаленное устройство через SSH.
        """
        local_path = Path(local).expanduser().resolve()
        if not local_path.exists():
            raise FileNotFoundError(f"Локальный путь '{local_path}' не существует.")

        if local_path.is_dir():
            # --- Логика для директории (используем tar и base64) ---
            log.debug(f"Загрузка директории через SSH (tar+base64): {local} -> {remote}")

            # Создаем tar архив в памяти
            with io.BytesIO() as tar_stream:
                with tarfile.open(fileobj=tar_stream, mode='w:') as tar:
                    tar.add(str(local_path), arcname=local_path.name)
                tar_bytes = tar_stream.getvalue()

            # Кодируем в base64 для безопасной передачи
            b64_tar_data = base64.b64encode(tar_bytes).decode('ascii')

            # Создаем удаленную директорию и распаковываем
            self.shell(f"mkdir -p '{remote}'", timeout=timeout, log_off=True)
            cmd = f"cd '{remote}' && echo '{b64_tar_data}' | base64 -d | tar -xf -"
            self.shell(cmd, timeout=timeout, log_off=True)

            final_path = str(Path(remote) / local_path.name)
            log.debug(f"Директория успешно загружена и распакована в '{final_path}'")
            return final_path
        else:
            # --- Логика для файла (используем cat и base64) ---
            log.debug(f"Загрузка файла через SSH (cat+base64): {local} -> {remote}")

            # Если remote - директория, формируем полный путь
            remote_path_final = remote
            if self.exists(remote) and self.is_dir(remote):
                remote_path_final = str(Path(remote) / local_path.name)

            # Создаем родительскую директорию на удаленном устройстве
            remote_parent = str(Path(remote_path_final).parent)
            self.shell(f"mkdir -p '{remote_parent}'", timeout=timeout, log_off=True)

            file_bytes = local_path.read_bytes()
            b64_data = base64.b64encode(file_bytes).decode('ascii')

            # Передаем и декодируем
            # Использование кавычек 'EOF' для `cat` более надежно для больших файлов
            cmd = f"echo '{b64_data}' | base64 -d > '{remote_path_final}'"
            self.shell(cmd, timeout=timeout, log_off=True)

            log.debug(f"Файл успешно загружен в '{remote_path_final}'")
            return remote_path_final
