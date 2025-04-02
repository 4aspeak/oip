import os
import re
from collections import defaultdict
from pymorphy2 import MorphAnalyzer
from natsort import natsorted


# Инициализация лемматизатора
morph = MorphAnalyzer()


# Функция для очистки текста от HTML-разметки
def clean_html(html_content):
    clean_text = re.sub(r'<[^>]+>', '', html_content)
    return clean_text


# Функция для токенизации текста
def tokenize(text):
    tokens = re.findall(r'\b[а-яА-ЯёЁ]+\b', text)  # разбиваем текст на слова, оставляя только буквы
    return tokens


# Функция для фильтрации слов
def filter_tokens(tokens):
    filtered_tokens = []
    for token in tokens:
        parsed = morph.parse(token)[0]
        # Исключаем предлоги, союзы, частицы, междометия, числительные и стоп-слова
        if (
            parsed.tag.POS not in {'PREP', 'CONJ', 'PRCL', 'INTJ', 'NUMR'}
        ):
            filtered_tokens.append(token.lower())  # Приводим к нижнему регистру
    return set(filtered_tokens)  # Убираем дубликаты


# Функция для группировки токенов по леммам
def group_by_lemmas(tokens):
    lemmas_dict = defaultdict(list)
    for token in tokens:
        lemma = morph.parse(token)[0].normal_form
        lemmas_dict[lemma].append(token)
    return lemmas_dict


# Основной код
if __name__ == "__main__":
    # Получаем путь к родительской папке
    parent_dir = os.path.dirname(os.getcwd())

    # Путь к папке с выкачанными страницами
    input_dir = os.path.join(parent_dir, 'task_1/выкачка')
    tokens_dir = "tokens"
    lemmas_dir = "lemmas"

    # Создаем папки для результатов
    os.makedirs(tokens_dir, exist_ok=True)
    os.makedirs(lemmas_dir, exist_ok=True)

    # Проходим по всем файлам в папке
    for filename in natsorted(os.listdir(input_dir)):
        file_path = os.path.join(input_dir, filename)

        # Читаем содержимое файла
        with open(file_path, "r", encoding="utf-8") as file:
            html_content = file.read()

        # Очистка HTML-разметки
        clean_text = clean_html(html_content)

        # Токенизация
        tokens = tokenize(clean_text)

        # Фильтрация токенов (включая удаление стоп-слов и дубликатов)
        filtered_tokens = filter_tokens(tokens)

        # Группировка токенов по леммам
        lemmas_dict = group_by_lemmas(filtered_tokens)

        # Создаем имя файла для токенов и лемм
        base_name = os.path.splitext(filename)[0]  # Убираем расширение .html
        output_tokens_file = os.path.join(tokens_dir, f"tokens_{base_name}.txt")
        output_lemmas_file = os.path.join(lemmas_dir, f"lemmas_{base_name}.txt")

        # Запись списка токенов в файл
        with open(output_tokens_file, "w", encoding="utf-8") as file:
            for token in sorted(filtered_tokens):
                file.write(f"{token}\n")

        # Запись списка лемматизированных токенов в файл
        with open(output_lemmas_file, "w", encoding="utf-8") as file:
            for lemma, tokens in sorted(lemmas_dict.items()):
                file.write(f"{lemma} {' '.join(tokens)}\n")

        print(f"Процесс для файла: {filename} -> tokens_{base_name}.txt, lemmas_{base_name}.txt")

    print("Завершено")