from typing import Optional, Union


class ADBError(Exception):
    def __init__(self, message: str | None = None):
        super().__init__(message)


class ADBConnectionError(ADBError):
    pass


class ADBFatalError(ADBError):
    pass


class ADBCommandError(ADBError):
    def __init__(self, command: str, result: Optional[str] = None, exc: Union[Exception, str] = None):
        self.command_str = command  # Исходная строка команды
        self.raw_result = result  # Исходный вывод команды (stdout/stderr)
        self.original_exception = exc  # Исходное исключение (например, RuntimeError от system.command.run)

        # Формируем сообщение для лога
        # 1. Команда: выводим как есть, обернув в одинарные кавычки для читаемости.
        message = f"\n🔥 Команда: {self.command_str}"

        # 2. Информация об ошибке из `exc` (если есть)
        if self.original_exception:
            error_source_message = str(self.original_exception).strip()
            if isinstance(self.original_exception, str):  # Если exc - это просто строка
                message += f"\n🔥 Ошибка: {error_source_message}"
            else:  # Если exc - это объект исключения
                message += f"\n🔥 Ошибка ({self.original_exception.__class__.__name__}): {error_source_message}"

        # 3. Отдельный вывод команды `raw_result`, если он есть, не пустой,
        #    и (важно!) еще не содержится в сообщении `original_exception` (чтобы избежать дублирования).
        cleaned_raw_result = self.raw_result.strip() if self.raw_result else None

        print_raw_result_separately = False
        if cleaned_raw_result:  # Если есть что выводить
            if not self.original_exception:
                print_raw_result_separately = True
            elif isinstance(self.original_exception, str):  # Если exc - строка, она не содержит вывод команды
                print_raw_result_separately = True
            else:  # original_exception это объект исключения
                # Проверяем, не содержится ли вывод уже в сообщении исключения
                # (RuntimeError от system.command.run обычно включает вывод)
                if cleaned_raw_result not in str(self.original_exception):
                    print_raw_result_separately = True

        if print_raw_result_separately and cleaned_raw_result:
            MAX_RESULT_DISPLAY_LEN = 1000  # Ограничение длины для лога
            display_output = cleaned_raw_result
            if len(display_output) > MAX_RESULT_DISPLAY_LEN:
                display_output = display_output[:MAX_RESULT_DISPLAY_LEN] + "..."
            message += f"\n🔥 Результат (stdout/stderr): '{display_output}'"

        super().__init__(message.strip())