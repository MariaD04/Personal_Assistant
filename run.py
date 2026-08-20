import os
import time
import subprocess
import sys


def install_dependencies():
    """
    Устанавливает зависимости из requirements.txt

    Returns:
        None
    """
    try:
        #subprocess.check_call([sys.executable, "-m", "pip", "install", "Cython==3.1.2"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Все зависимости успешно установлены!")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при установке зависимостей: {e}")
        sys.exit(1)


def run_files(max_attempts=3, delay=5):
    """
    Запускает файлы проекта с повторными попытками

    Args:
        max_attempts (int): количество попыток запуска файлов
        delay (int): задержка между попытками

    Returns:
        None
    """
    files_to_run = [
        "RAG_data.py",
        "bot.py"
    ]

    for file in files_to_run:
        if not os.path.exists(file):
            print(f"⚠ Файл {file} не найден, пропускаем...")
            continue

        attempt = 1
        while attempt <= max_attempts:
            try:
                print(f"🚀 Попытка {attempt}/{max_attempts} запуска {file}...")
                subprocess.check_call([sys.executable, file])
                print(f"✅ {file} успешно запущен!")
                break
            except subprocess.CalledProcessError as e:
                print(f"❌ Ошибка при запуске {file}: {e}")
                if attempt < max_attempts:
                    print(f"⏳ Ожидание {delay} секунд перед повторной попыткой...")
                    time.sleep(delay)
                attempt += 1
        else:
            print(f"🔥 Не удалось запустить {file} после {max_attempts} попыток")
            sys.exit(1)


if __name__ == "__main__":
    print("Установка зависимостей...")
    install_dependencies()

    print("\nЗапуск файлов проекта...")
    run_files()

    print("\nПроект успешно запущен!")