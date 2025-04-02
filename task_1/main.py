import os
import requests
from urls import find_content_links
from config import BASE_URL, SEARCH_URL


# Поиск ссылок на странице
urls = find_content_links(BASE_URL, SEARCH_URL)

print(f"Найдено {len(urls)} ссылок.")


# Создаем папку для сохранения выкачанных страниц
output_dir = "выкачка"
os.makedirs(output_dir, exist_ok=True)

# Файл для хранения индекса
index_file = "index.txt"


# Очистка файла index.txt перед началом работы
open(index_file, "w").close()

# Счетчик для нумерации файлов
file_counter = 1

# Проходим по каждой ссылке
for url in urls:
    try:
        # Отправляем GET-запрос к странице
        response = requests.get(url)
        response.raise_for_status()  # Проверяем статус ответа

        # Сохраняем содержимое страницы в файл
        filename = f"{file_counter}.html"
        with open(os.path.join(output_dir, filename), "w", encoding="utf-8") as output:
            output.write(response.text)

        # Записываем номер файла и ссылку в index.txt
        with open(index_file, "a", encoding="utf-8") as index:
            index.write(f"{file_counter} {url}\n")

        print(f"Скачан: {url} -> {filename}")
        file_counter += 1

    except Exception as e:
        print(f"Ошибка скачивания {url}: {e}")


print("Скачивание завершено")
