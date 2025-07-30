import tempfile
from pathlib import Path

from r00system import get_file_metadata, set_file_metadata, run


def patch_file(filepath: str | Path, old_text: str, new_text: str, encoding: str = 'utf-8') -> bool:
    """
    Безопасно заменяет все вхождения текстовой строки в файле.

    Работает по принципу "прочитать -> изменить в памяти -> записать во временный файл -> атомарно заменить".
    Это гарантирует, что исходный файл не будет поврежден в случае ошибки.

    :param filepath: Путь к целевому файлу.
    :param old_text: Текстовая строка для поиска (будет закодирована в байты).
    :param new_text: Текстовая строка для замены (будет закодирована в байты).
    :param encoding: Кодировка для преобразования строк в байты. По умолчанию 'utf-8'.
    :return: True в случае успеха или если замена не требовалась, False в случае ошибки.
    """
    target_file = Path(filepath)

    # Проверки входных данных
    if not target_file.is_file():
        print(f"[!] Ошибка: Файл не найден по пути '{target_file}'")
        return False

    if old_text == new_text:
        print(f"[*] Информация: Старый и новый текст идентичны ('{old_text}'). Замена не требуется.")
        return True

    # Сохраняем метаданные оригинального файла и делаем 777
    metadata = get_file_metadata(filepath)
    run(f'sudo chmod 777 {filepath}')

    # Преобразование строк в байты
    try:
        old_bytes = old_text.encode(encoding)
        new_bytes = new_text.encode(encoding)
    except Exception as e:
        print(f"[!] Ошибка кодирования: Не удалось преобразовать строки в байты с кодировкой '{encoding}'. {e}")
        return False

    print(f"\n--- Обрабатываю файл: {target_file}")
    print(f"--- Ищу: {old_bytes!r} | Заменяю на: {new_bytes!r}")

    tmp_path = None
    try:
        # Чтение и замена
        original_data = target_file.read_bytes()

        if old_bytes not in original_data:
            print(f"[*] Информация: Последовательность байт {old_bytes!r} не найдена в файле. Изменения не требуются.")
            return True

        modified_data = original_data.replace(old_bytes, new_bytes)

        # Безопасная запись через временный файл
        with tempfile.NamedTemporaryFile(mode='wb', dir=target_file.parent, delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)
            tmp_file.write(modified_data)

        # Атомарная замена
        tmp_path.rename(target_file)
        print(f"[+] Успех: Файл '{target_file}' обновлен.")
        return True

    except Exception as e:
        print(f"[!] КРИТИЧЕСКАЯ ОШИБКА при работе с файлом '{target_file}': {e}")
        # Гарантированное удаление временного файла в случае сбоя
        if tmp_path and tmp_path.exists():
            tmp_path.unlink()
        return False
    finally:
        # Восстанавливаем метаданные
        set_file_metadata(filepath, metadata)
