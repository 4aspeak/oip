import os
import random
import json
from main import boolean_search


def generate_random_queries(
    inverted_index,
    num_queries=10,
    min_terms=3,
    max_terms=8,
    max_depth=3
):
    """
    Генерирует случайные корректные запросы на основе инвертированного списка слов.
    :param inverted_index: Инвертированный индекс (словарь термин -> множество документов).
    :param num_queries: Количество запросов для генерации.
    :param min_terms: Минимальное количество терминов в запросе.
    :param max_terms: Максимальное количество терминов в запросе.
    :param max_depth: Максимальная глубина вложенности скобок.
    :return: Список случайно сгенерированных запросов.
    """
    # Список всех уникальных терминов из индекса
    terms = list(inverted_index.keys())

    # Возможные операторы
    operators = ["and", "or"]

    queries = []
    for _ in range(num_queries):
        # Случайное количество терминов в запросе (между min_terms и max_terms)
        num_terms = random.randint(min_terms, max_terms)

        # Генерируем выражение с заданным количеством терминов
        query = generate_expression(terms, operators, num_terms, max_depth)
        queries.append(query)

    return queries


def generate_expression(terms, operators, num_terms, depth):
    """
    Рекурсивно генерирует случайное логическое выражение.
    :param terms: Список терминов.
    :param operators: Список операторов.
    :param num_terms: Требуемое количество терминов в выражении.
    :param depth: Текущая глубина вложенности.
    :return: Строка с логическим выражением.
    """
    if num_terms == 1 or depth == 0:
        # Базовый случай: возвращаем случайный термин
        return random.choice(terms)

    # Выбираем случайный оператор
    operator = random.choice(operators)

    # Разделяем оставшееся количество терминов между левой и правой частями
    left_terms = random.randint(1, num_terms - 1)
    right_terms = num_terms - left_terms

    # Генерируем левую и правую части выражения
    left = generate_expression(terms, operators, left_terms, depth - 1)
    right = generate_expression(terms, operators, right_terms, depth - 1)

    # Случайно добавляем NOT к одной из частей
    if random.random() < 0.3:  # 30% вероятность добавления NOT
        left = add_not(left)
    if random.random() < 0.3:
        right = add_not(right)

    # Объединяем части с оператором
    expression = f"{left} {operator} {right}"

    # Случайно оборачиваем выражение в скобки
    if random.random() < 0.5:  # 50% вероятность добавления скобок
        expression = f"({expression})"

    return expression


def add_not(expression):
    """
    Добавляет оператор NOT к выражению, если это допустимо.
    :param expression: Исходное выражение.
    :return: Выражение с добавленным NOT.
    """
    # Если выражение уже начинается с NOT, не добавляем второй NOT
    if expression.startswith("NOT"):
        return expression
    return f"NOT {expression}"


# Пример использования
if __name__ == "__main__":
    # Получаем путь к родительской папке
    parent_dir = os.path.dirname(os.getcwd())

    # Путь к папке с выкачанными страницами
    tokens_dir = os.path.join(parent_dir, 'task_2/tokens')

    total_tokens_docs = len(os.listdir(tokens_dir))

    # Пример инвертированного индекса
    with open("inverted_index.json", "r", encoding="utf-8") as file:
        inverted_index = json.load(file)

    for key in inverted_index:
        inverted_index[key] = set(inverted_index[key])

    # Генерация случайных запросов
    random_queries = generate_random_queries(
        inverted_index,
        num_queries=50,
        min_terms=10,
        max_terms=20,
        max_depth=3
    )

    result_str = ""

    # Вывод запросов
    print("Случайно сгенерированные запросы:")
    for query in random_queries:
        print(query)
        result_tokens = boolean_search(query.lower(), inverted_index, total_tokens_docs)
        main_result = (
            f"Результаты поиска по запросу {query}:"
            f"\nДокументы: {', '.join(list(map(str, sorted(result_tokens))))}\n\n"
        )
        result_str += f"{main_result}"

    with open("random_queries.txt", "w", encoding="utf-8") as file:
        file.write(result_str)
