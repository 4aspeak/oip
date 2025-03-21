import requests
from bs4 import BeautifulSoup
from config import MIN_TEXT_LENGTH, TARGET_LANGUAGE
from langdetect import detect, LangDetectException


def find_content_links(base_url, search_url):
    try:
        # Отправляем GET-запрос к указанному URL
        response = requests.get(search_url)
        response.raise_for_status()  # Проверяем статус ответа (например, 404 или 500 ошибки)

        # Парсим HTML-код страницы с помощью BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Находим все теги <a> с атрибутом href
        all_links = []
        for a_tag in soup.find_all('a', href=True):
            link = a_tag['href']
            # Обрабатываем абсолютные и относительные ссылки
            if link.startswith('/'):
                all_links.append(base_url + link)
            elif link.startswith(base_url):
                all_links.append(link)

        all_links = list(set(all_links))

        content_links = []
        for link in all_links:
            try:
                # Загружаем страницу по ссылке
                response = requests.get(link, timeout=5)
                response.raise_for_status()
                page_soup = BeautifulSoup(response.text, 'html.parser')

                # Извлекаем текст со страницы
                text = page_soup.get_text(strip=True)

                # Проверяем длину текста
                if len(text) < MIN_TEXT_LENGTH:
                    continue

                try:
                    detected_language = detect(text)
                except LangDetectException:
                    detected_language = None

                # Если язык совпадает с целевым, добавляем ссылку
                if detected_language == TARGET_LANGUAGE:
                    content_links.append(link)

            except requests.exceptions.RequestException as e:
                print(f"Ошибка при запросе к {link}: {e}")

        return content_links

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к {search_url}: {e}")
        return []

