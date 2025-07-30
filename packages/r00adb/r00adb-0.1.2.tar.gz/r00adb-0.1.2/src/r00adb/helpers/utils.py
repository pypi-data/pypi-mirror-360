import functools
import pathlib
import threading
import time
from dataclasses import dataclass
from typing import Callable, Any, Union

from r00logger import log
from system.command import exists_process
from ..helpers.constants import MAX_LOG_RESULT_LEN



def wait_close_android_studio():
    """
    Проверяет наличие запущенных процессов IDE (Android Studio, IntelliJ IDEA),
    которые могут мешать управлению ADB сервером.
    Возвращает True, если такой процесс найден, иначе False.
    """
    log.trace("Проверка наличия мешающих IDE...")
    while True:
        pattern = r'\bjava\b.*android-studio.*com\.android\.tools\.idea\.MainWrapper'
        if exists_process(pattern, kill=False):
            log.warning("Найдены процессы Android Studio или IntelliJ IDEA, которые могут мешать ADB. Закрой их!")
            time.sleep(5)
        else:
            return


# --- Контекст потока для отслеживания вложенности ---
_shell_wrap_context = threading.local()

# --- Уровни логирования по умолчанию ---
DEFAULT_OUTER_LOG_LEVEL = "DEBUG"
DEFAULT_INNER_LOG_LEVEL = "TRACE"  # Уровень для вложенных вызовов


# --- Фабрика декораторов (без изменений) ---
def shell_wrap(log_level_or_func: Union[str, Callable, None] = None) -> Callable:
    """
    Декоратор (или фабрика декораторов) для методов, выполняющих shell-команды.
    Учитывает вложенность вызовов для управления уровнем логирования.
    Внешние вызовы используют настроенный уровень (по умолчанию DEBUG).
    Внутренние вызовы (вызванные из другого @shell_wrap метода) используют TRACE.
    """
    configured_outer_log_level = DEFAULT_OUTER_LOG_LEVEL

    if isinstance(log_level_or_func, str) or log_level_or_func is None:
        if isinstance(log_level_or_func, str):
            configured_outer_log_level = log_level_or_func.upper()

        def decorator(func: Callable) -> Callable:
            # Передаем настроенный уровень для внешнего вызова
            return _create_wrapper(func, configured_outer_log_level)

        return decorator
    elif callable(log_level_or_func):
        func = log_level_or_func
        # Используем уровень по умолчанию для внешнего вызова
        return _create_wrapper(func, DEFAULT_OUTER_LOG_LEVEL)
    else:
        raise TypeError("Некорректное использование декоратора shell_wrap")


# --- Вспомогательная функция для создания реального wrapper ---
def _create_wrapper(func: Callable, configured_outer_log_level: str) -> Callable:
    """Создает и возвращает фактическую функцию-обертку с учетом контекста."""

    @functools.wraps(func)
    def wrapper(self, *args: Any, **kwargs: Any) -> Any:
        # --- Инициализация контекста потока, если необходимо ---
        if not hasattr(_shell_wrap_context, 'level_stack'):
            _shell_wrap_context.level_stack = []

        # --- Определение уровня логирования для ТЕКУЩЕГО вызова ---
        is_outer_call = not bool(_shell_wrap_context.level_stack)
        if is_outer_call:
            effective_log_level_name = configured_outer_log_level
        else:
            effective_log_level_name = DEFAULT_INNER_LOG_LEVEL  # Внутренние вызовы всегда TRACE

        # --- Получение метода логирования ---
        log_method = getattr(log, effective_log_level_name.lower(), None)
        if log_method is None:
            # Фоллбэк на DEBUG, если уровень некорректен
            log.warning(
                f"Некорректный уровень логирования '{effective_log_level_name}' в shell_wrap для '{func.__name__}'. Используется DEBUG.")
            effective_log_level_name = "DEBUG"
            log_method = log.debug

        # --- Помещаем текущий уровень в стек ---
        _shell_wrap_context.level_stack.append(effective_log_level_name)

        # --- Подготовка к вызову (как раньше) ---
        processed_args = [str(arg) if isinstance(arg, pathlib.Path) else arg for arg in args]
        processed_kwargs = {k: str(v) if isinstance(v, pathlib.Path) else v for k, v in kwargs.items()}
        arg_parts = [repr(a) for a in args]
        kwarg_parts = [f"{k}={v!r}" for k, v in kwargs.items()]
        args_str = ", ".join(arg_parts + kwarg_parts)
        if len(args_str) > MAX_LOG_RESULT_LEN:
            args_str = args_str[:MAX_LOG_RESULT_LEN] + '...'
        funcname = f'{self.__class__.__name__}.{func.__name__}'
        t_start = time.perf_counter()
        result = None

        try:
            # --- Вызов оригинальной функции ---
            result = func(self, *processed_args, **processed_kwargs)
            elapsed = time.perf_counter() - t_start

            # --- Логирование успеха (используем effective_log_level_name) ---
            result_repr = repr(result)
            if len(result_repr) > MAX_LOG_RESULT_LEN:
                result_repr_truncated = result_repr[:MAX_LOG_RESULT_LEN] + '...'
            else:
                result_repr_truncated = result_repr
            # Используем выбранный метод логирования
            log_method(f"→ [{elapsed:.3f}s] {funcname}({args_str}) → {result_repr_truncated}")
            return result

        except Exception as e:
            elapsed = time.perf_counter() - t_start
            # --- Логирование ошибки (используем effective_log_level_name) ---
            # Логируем саму строку с ошибкой на уровне effective_log_level_name,
            # но traceback будет по-прежнему виден как ERROR.
            log_method(f"→ [{elapsed:.3f}s] {funcname}({args_str}) FAILED: {e.__class__.__name__}: {e}", exc_info=True)
            raise

        finally:
            # --- Восстанавливаем стек уровней в любом случае ---
            if hasattr(_shell_wrap_context, 'level_stack') and _shell_wrap_context.level_stack:
                _shell_wrap_context.level_stack.pop()

    return wrapper
