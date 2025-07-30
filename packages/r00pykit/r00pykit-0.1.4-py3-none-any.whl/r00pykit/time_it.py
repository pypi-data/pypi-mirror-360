import time
from functools import wraps
from r00logger import log


class TimeIT:
    def __init__(self, name=None):
        self._name = name
        self._start_time = None
        self._func_name = None # Для хранения имени декорируемой функции

    def __enter__(self):
        self._start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._start_time is None:
            # На случай если __exit__ вызван без __enter__ (маловероятно в 'with')
            return False # Не подавляем исключение

        end_time = time.time()
        elapsed_time = end_time - self._start_time
        if self._name:
            log.trace(f"'{self._name}' выполнен за {elapsed_time:.6f} секунд")
        else:
            log.trace(f"выполнен за {elapsed_time:.6f} секунд")
        self._start_time = None
        return False

    # --- Метод для использования как Декоратор ---
    def __call__(self, func):
        """
        Вызывается, когда экземпляр используется как декоратор (@time_it).
        Принимает декорируемую функцию и возвращает обертку.
        """
        self._func_name = func.__name__

        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                end_time = time.time()
                elapsed_time = end_time - start_time
                log.trace(f"'{self._func_name}' выполнен за {elapsed_time:.6f} секунд")

        return wrapper

time_it = TimeIT()