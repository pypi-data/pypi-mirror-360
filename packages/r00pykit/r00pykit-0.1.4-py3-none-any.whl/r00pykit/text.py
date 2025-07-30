import os
import re
from typing import List


def is_ipv4_addres(text) -> bool:
    """
    Проверяет, является ли строка IPv4-адресом.

    :param text: строка для проверки
    :return:
    """
    match = re.search(r'\b(?:(?:25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})\.){3}(?:25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})\b', text)
    if match:
        return True
    return False


def find_ipv4_addresses(text: str) -> List[str]:
    """
    Находит все IPv4-адреса в тексте.

    :param text: текст для поиска
    :return: список IPv4-адресов
    """
    pattern = r'(?:(?:25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})\.){3}' \
              r'(?:25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})'
    return re.findall(pattern, text)


def get_absolute_path(text_path: str) -> str:
    """
    Если text_path похож на путь к файлу в стиле Linux, возвращает его абсолютный путь.
    В противном случае возвращает оригинальную строку.

    "Похож" означает:
    - Не пустая строка.
    - Не содержит нулевых байтов.
    - Не является очевидным абсолютным путем Windows (например, C:\...).
    - Не использует обратный слеш как основной разделитель каталогов.
    - Может быть абсолютным (/foo/bar), относительным (foo/bar, ./foo, ../bar),
      содержать ~ (для домашнего каталога) или быть просто именем файла.
    """
    if not isinstance(text_path, str):
        return text_path

    stripped_path = text_path.strip()
    if not stripped_path:
        return text_path

    # 1. Проверка на нулевые байты (недопустимы в именах файлов/путях Unix)
    if '\0' in stripped_path:
        return text_path

    # 2. Проверка на явные признаки пути Windows, которые несовместимы с Linux-стилем
    if re.match(r"^[a-zA-Z]:[\\/]", stripped_path) or stripped_path.startswith("\\\\"):
        return text_path

    # 3. Обработка обратных слешей.
    #    В Linux обратный слеш может быть частью имени файла, но не разделителем.
    #    Если обратные слеши используются как разделители, это не "Linux-like".
    #    Простая эвристика: если есть обратный слеш, но нет прямого,
    #    и это не одиночный обратный слеш (который мог бы быть экранированием),
    #    то считаем, что это не Linux-путь.
    #    Более сложная логика может потребоваться для имен файлов с '\'.
    if "\\" in stripped_path:
        if "/" not in stripped_path and stripped_path.count("\\") > 0 :
             # Если есть только '\' и их больше одного или это не просто экранированный символ в конце
             # Пример: "path\\to\\file" - не Linux-like
             # Пример: "file\ name" - может быть Linux, но эта функция может его отсеять.
             # Для простоты, если есть '\', считаем его нетипичным для "чистого" Linux пути.
            print(f"Debug: '{text_path}' contains backslashes in a way not typical for Linux paths.")
            return text_path
        # Если есть и / и \ , например /foo/bar\ baz.txt - это валидный путь на Linux,
        # где 'bar\ baz.txt' - имя файла. os.path.abspath должен справиться.

    try:
        # 4. Расширение тильды (~) до домашнего каталога пользователя
        path_after_tilde_expansion = os.path.expanduser(stripped_path)

        # 5. Получение абсолютного пути
        absolute_path = os.path.abspath(path_after_tilde_expansion)
        return absolute_path
    except Exception as e:
        print(f"Debug: Exception for '{text_path}': {e}")
        return text_path
