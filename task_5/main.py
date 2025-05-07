import os
import json
import re
from collections import defaultdict
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from task_2.main import tokenize, filter_tokens, delete_duplicates, group_by_lemmas

# Пути к папкам
HTML_DIR = "../task_1/pages"
TOKENS_DIR = "../task_2/tokens"
LEMMAS_DIR = "../task_2/lemmas"
INVERTED_INDEX_FILE = "../task_3/inverted_index.json"
TF_IDF_TOKENS_DIR = "../task_4/tokens"
TF_IDF_LEMMAS_DIR = "../task_4/lemmas"

# Загрузка инвертированного списка
with open(INVERTED_INDEX_FILE, "r", encoding="utf-8") as f:
    inverted_index = json.load(f)


# Загрузка TF-IDF для токенов
def load_tf_idf(directory):
    tf_idf_data = defaultdict(dict)
    for filename in os.listdir(directory):
        if not filename.endswith(".txt"):
            continue
        doc_id = int(filename.split("_")[3].split(".")[0])
        with open(os.path.join(directory, filename), "r", encoding="utf-8") as f:
            for line in f:
                token, tf, idf = line.strip().split()
                tf_idf_data[doc_id][token] = float(tf) * float(idf)  # TF-IDF = TF * IDF
    return tf_idf_data


tf_idf_tokens = load_tf_idf(TF_IDF_TOKENS_DIR)
tf_idf_lemmas = load_tf_idf(TF_IDF_LEMMAS_DIR)


def preprocess_query(query, lemmas_dir=LEMMAS_DIR):
    tokens = tokenize(query)

    filtered_tokens = filter_tokens(tokens)
    filtered_tokens = delete_duplicates(filtered_tokens)

    # Находим леммы для токенов
    lemmas_dict = group_by_lemmas(filtered_tokens)

    return lemmas_dict


def query_to_vector(query, tf_idf_data):
    query_vector = {}

    # Проходим по всем леммам из запроса
    for lemma in query:
        max_tf_idf = max(
            tf_idf_data[doc].get(lemma, 0) for doc in tf_idf_data
        )
        query_vector[lemma] = max_tf_idf

    return query_vector


def calculate_relevance(query_vector, tf_idf_data):
    similarities = {}
    for doc_id, doc_vector in tf_idf_data.items():
        # Создаем вектор документа
        doc_vec = np.array([doc_vector.get(term, 0) for term in query_vector])
        query_vec = np.array([query_vector[term] for term in query_vector])

        # Вычисляем косинусную близость
        similarity = cosine_similarity([query_vec], [doc_vec])[0][0]
        similarities[doc_id] = similarity

    return similarities


def rank_documents(similarities, top_n=5):
    ranked_docs = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
    return ranked_docs[:top_n]


query_examples = [
    "поттер узник азкабана",
    "вселенная волшебников",
    "дары смерти когда появились",
    "все книги гарри поттера",
    "волшебная палочка альбуса дамблдора",
    "гермиона рон"
]

results = ""

for query in query_examples:
    # Предобработка запроса
    lemmas_dict = preprocess_query(query)

    query_lemmas = list(lemmas_dict.keys())

    # Преобразование запроса в вектор
    query_vector = query_to_vector(query_lemmas, tf_idf_lemmas)

    # Расчет релевантности
    similarities = calculate_relevance(query_vector, tf_idf_lemmas)

    # Ранжирование документов
    ranked_docs = rank_documents(similarities, top_n=10)

    # Вывод результатов
    results += f"Запрос: {query}\n"
    results += "Топ-10 документов:\n"

    print("Топ-10 документов:")
    for doc_id, score in ranked_docs:
        print(f"Документ {doc_id}: релевантность = {score:.4f}")
        results += f"Документ {doc_id}: релевантность = {score:.4f}\n"

    results += "\n"


with open("results.txt", "w", encoding="utf-8") as file:
    file.write(results)
