import json
import os
import math
from collections import defaultdict, Counter
from task_2.main import clean_html, tokenize, filter_tokens

# Путь к родительской папке
parent_dir = os.path.dirname(os.getcwd())

# Пути к папкам
TOKENS_DIR = os.path.join(parent_dir, "task_2/tokens")
LEMMAS_DIR = os.path.join(parent_dir, "task_2/lemmas")
PAGES_DIR = os.path.join(parent_dir, "task_1/pages")
INVERTED_LEMMAS_DIR = os.path.join(parent_dir, "task_3/inverted_index.json")

# Общее количество документов
N = len(os.listdir(PAGES_DIR))

# Загрузка инвертированного списка
with open(INVERTED_LEMMAS_DIR, "r", encoding="utf-8") as file:
    inverted_index = json.load(file)


# Функция для подсчета TF
def calculate_tf(tokens, all_tokens_count, all_tokens_counter):

    # Расчет TF для каждого токена
    tf = {}
    for token in tokens:
        temp_tf = all_tokens_counter.get(token, 0) / all_tokens_count
        tf[token] = temp_tf

    return tf


# Функция для подсчета IDF
def calculate_idf(tokens, inverted_index, N):
    idf = {}
    for token in tokens:
        doc_ids = inverted_index.get(token, set())
        temp_idf = math.log(N / len(doc_ids)) if len(doc_ids) > 0 else 0
        idf[token] = temp_idf

    return idf


# Функция для подсчета TF для лемм
def calculate_tf_for_lemmas(tf_tokens, lemmas):
    tf = {}

    for lemma in lemmas:
        lemma, *lemmas_tokens = lemma.split()
        sum_tf = 0
        for token in lemmas_tokens:
            if token in tf_tokens:
                sum_tf += tf_tokens[token]
        tf[lemma] = sum_tf

    return tf


# Функция для подсчета IDF для лемм
def calculate_idf_for_lemmas(lemmas, inverted_index, N):
    idf = {}
    for lemma in lemmas:
        lemma, *lemmas_tokens = lemma.split()
        doc_ids = set()
        for token in lemmas_tokens:
            token_doc_ids = inverted_index.get(token, set())
            token_doc_ids = set(token_doc_ids)
            doc_ids.update(token_doc_ids)

        temp_idf = math.log(N / len(doc_ids)) if len(doc_ids) > 0 else 0
        idf[lemma] = temp_idf

    return idf


if __name__ == '__main__':

    tokens_dir = "tokens"
    lemmas_dir = "lemmas"

    # Создаем папки для результатов
    os.makedirs(tokens_dir, exist_ok=True)
    os.makedirs(lemmas_dir, exist_ok=True)

    # Основной цикл обработки документов
    for doc_id in range(1, N + 1):
        # Чтение токенов
        with open(os.path.join(TOKENS_DIR, f"tokens_{doc_id}.txt"), "r", encoding="utf-8") as f:
            tokens = f.read().splitlines()

        # Чтение лемм
        with open(os.path.join(LEMMAS_DIR, f"lemmas_{doc_id}.txt"), "r", encoding="utf-8") as f:
            lemmas = f.readlines()

        with open(os.path.join(PAGES_DIR, f"{doc_id}.html"), "r", encoding="utf-8") as f:
            html = f.read()
            clean_text = clean_html(html)

        all_tokens_in_text = filter_tokens(tokenize(clean_text))

        all_tokens_count = len(all_tokens_in_text)
        all_tokens_counter = Counter(all_tokens_in_text)

        # Расчет TF для токенов
        tf_tokens = calculate_tf(tokens, all_tokens_count, all_tokens_counter)

        # Расчет IDF для токенов
        idf_tokens = calculate_idf(tokens, inverted_index, N)

        # Расчет TF для лемм
        tf_lemmas = calculate_tf_for_lemmas(tf_tokens, lemmas)

        # Расчет IDF для лемм
        idf_lemmas = calculate_idf_for_lemmas(lemmas, inverted_index, N)

        # Вывод результатов
        output_tokens_file = os.path.join(tokens_dir, f"tokens_tf_idf_{doc_id}.txt")
        output_lemmas_file = os.path.join(lemmas_dir, f"lemmas__tf_idf_{doc_id}.txt")

        result_tokens = ""
        result_lemmas = ""

        for key in tf_tokens.keys():
            tf = tf_tokens[key]
            idf = idf_tokens[key]
            result_tokens += f"{key} {tf} {idf}\n"

        for key in tf_lemmas.keys():
            tf = tf_lemmas[key]
            idf = idf_lemmas[key]
            result_lemmas += f"{key} {tf} {idf}\n"

        with open(output_tokens_file, "w", encoding="utf-8") as file:
            file.write(result_tokens)

        with open(output_lemmas_file, "w", encoding="utf-8") as file:
            file.write(result_lemmas)

        print(f"Сохранен {output_tokens_file} and {output_lemmas_file} для документа {doc_id}")

