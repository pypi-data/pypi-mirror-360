import re
import time
from pathlib import Path
from typing import Union, List

from r00logger import log


class TWRP:
    def __init__(self, executor):
        self._executor = executor
        self.allow_list_names = ['boot', 'cache', 'data', 'recovery', 'r00system', 'efs']

    def _get_partition_path(self, name: str):
        """
        Получение пути к разделу
        :param name: [boot|cache|data|recovery|r00system|efs]
        :return:
        """
        assert name in self.allow_list_names, "Deny word in allow_list_names"
        result = self._executor.shell(f'ls -l /dev/block/platform/*/by-name/ | grep -i " {name} "')
        partition_path = result.split('->')[1].strip()
        if '\n' in partition_path:
            partition_path = partition_path.split('\n')[0].strip()
        return partition_path

    def install_zip(self, devicepath: Union[str, Path]):
        """
        Установка zip файла
        :param devicepath: Путь к zip на телефоне
        :return:
        """
        self._executor.shell(f'twrp install {devicepath}', timeout=900)

    def wipe(self):
        """ Очистка разделов телефона """
        cmds = [
            "twrp format data",
            "twrp wipe cache",
            "twrp wipe r00system",
            "twrp wipe dalvik",
            "twrp wipe data",
        ]
        for cmd in cmds:
            for _ in range(3):
                wait = 10 if 'twrp format data' in cmd else 4
                output = self._executor.shell(cmd, timeout=wait, ignore_errors=True)
                if output and 'Done processing script file' in output:
                    break

    def backup(self, partitions: Union[List, str]) -> str:
        """
        Резервное копирование разделов
        :param partitions: Список разделов для бэкапа
        [boot|cache|data|recovery|r00system|efs]
        """
        if isinstance(partitions, str):
            partitions = [partitions]

        for partition in partitions:
            match partition.lower():
                case 'boot':
                    #self._executor.shell('twrp backup B boot')
                    partiton_path = self._get_partition_path('boot')
                    output_img_path = '/sdcard/boot_backup.img'
                    self._executor.shell(f'dd if={partiton_path} of={output_img_path} bs=4096')
                    return output_img_path
                case 'cache':
                    self._executor.shell("twrp backup C cache")
                case 'data':
                    self._executor.shell('twrp backup D boot')
                case 'recovery':
                    self._executor.shell('twrp backup R recovery')
                case 'r00system':
                    self._executor.shell('twrp backup S r00system')
                case 'efs':
                    partiton_path = self._get_partition_path('efs')
                    output_img_path = '/sdcard/efs_backup.img'
                    self._executor.shell(f'dd if={partiton_path} of={output_img_path} bs=4096')
                    return output_img_path
                case _:
                    log.warning(f"Unknown partition: {partition}")

    def restore(self, partitions: list[str], backup_name: str = None):
        """
        Восстановление разделов из бэкапа
        :param partitions: Список разделов для восстановления
        [boot|cache|data|recovery|r00system|efs]
        :param backup_name: Имя папки с бэкапом (по умолчанию последняя)
        """
        for partition in partitions:
            match partition.lower():
                case 'boot':
                    self._executor.shell(f'twrp restore boot')
                case 'cache':
                    self._executor.shell('twrp restore cache')
                case 'data':
                    self._executor.shell('twrp restore data')
                case 'recovery':
                    self._executor.shell('twrp restore recovery')
                case 'r00system':
                    self._executor.shell('twrp restore r00system')
                case 'efs':
                    # Получаем актуальный путь к разделу EFS
                    partition_path = self._get_partition_path('efs')

                    # Проверяем существование бэкапа
                    check_cmd = 'ls /sdcard/efs_backup.img || echo "not_found"'
                    if "not_found" in self._executor.shell(check_cmd).stdout:
                        log.error("EFS backup file not found")
                        continue

                    # Восстанавливаем через dd с проверкой
                    self._executor.shell(f'dd if=/sdcard/efs_backup.img of={partition_path} bs=4096')
                    log.info("EFS restored successfully")

                case _:
                    log.warning(f"Unknown partition: {partition}")

    def mount(self, partition: str):
        """
        Монтирует раздел в указанную точку
        :param partition: [cache|data|r00system|efs|preload]
        """
        # Проверка partition
        allow_word = ['cache', 'data', 'r00system', 'efs', 'preload']
        assert partition in allow_word, "Deny word in allow_word"

        result = self._executor.shell(f'twrp mount {partition.lower()}')
        if 'mounted' in result.lower():
            log.info(f"Successfully mounted {partition}")
            return True
        else:
            log.error(f"Failed to mount {partition}: {result}")
            return False

    def unmount(self, partition: str):
        """
        Размонтирует раздел в указанную точку
        :param partition: [cache|data|r00system|efs|preload]
        """
        # Проверка partition
        allow_word = ['cache', 'data', 'r00system', 'efs', 'preload']
        assert partition in allow_word, "Deny word in allow_word"

        result = self._executor.shell(f'twrp unmount {partition.lower()}')
        if 'unmounted' in result.lower():
            log.info(f"Successfully mounted {partition}")
            return True
        else:
            log.error(f"Failed to unmount {partition}: {result}")
            return False

    def overwrite_boot_partition(self, device_boot_img: str):
        """
        Перезаписывает раздел BOOT на Android устройстве через r00adb shell в режиме TWRP.
        :param device_boot_img: Путь к boot.img на телефоне
        :return:
        """
        for _ in range(2):
            try:
                output = self._executor.shell("ls -l /dev/block/platform/*/by-name/")
                for line in output.splitlines():
                    if 'BOOT' in line:
                        p = re.compile('-> (.*)')
                        boot_partition_path = p.search(line).group(1).strip()
                        break
                else:
                    raise ValueError("BOOT partition not found in /dev/block/platform/*/by-name/")

                output = self._executor.shell(f"dd if={device_boot_img} of={boot_partition_path}")
                if 'copied' in output:
                    log.info("Успешно перезаписан раздел BOOT")
                    return True

                log.error(f"Failed to overwrite boot partition: {output}")
                raise ValueError("Failed to overwrite boot partition")
            except Exception as e:
                log.error(f"Ошибка при перезаписи BOOT раздела, повторяем: {e}")
                time.sleep(5)
        raise

    def overwrite_efs_partition(self, device_efs_img: str):
        """
        Перезаписывает раздел EFS на Android устройстве через r00adb shell в режиме TWRP.
        :param device_efs_img: Путь к efs.img на телефоне
        :return:
        """
        for _ in range(2):
            try:
                output = self._executor.shell("ls -l /dev/block/platform/*/by-name/")
                for line in output.splitlines():
                    if ' EFS' in line:
                        p = re.compile('-> (.*)')
                        efs_partition_path = p.search(line).group(1).strip()
                        break
                else:
                    raise ValueError("BOOT partition not found in /dev/block/platform/*/by-name/")

                output = self._executor.shell(f"dd if={device_efs_img} of={efs_partition_path}")
                if 'copied' in output:
                    log.info("Успешно перезаписан раздел EFS")
                    return True
                raise
            except Exception as e:
                log.error(f"Ошибка при перезаписи EFS раздела, повторяем: {e}")
                time.sleep(5)
        raise
