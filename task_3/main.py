import os
import re
from collections import defaultdict

# Получаем путь к родительской папке
parent_dir = os.path.dirname(os.getcwd())

# Путь к папке с выкачанными страницами
tokens_dir = os.path.join(parent_dir, 'task_2/tokens')
lemmas_dir = os.path.join(parent_dir, 'task_2/lemmas')


# 1. Загрузка данных
def load_tokens_and_lemmas(tokens_dir, lemmas_dir):
    """
    Загружает токены и леммы из файлов.
    :param tokens_dir: Папка с файлами токенов.
    :param lemmas_dir: Папка с файлами лемм.
    :return: Словарь лемм -> множество документов.
    """
    tokens_inverted_index = defaultdict(set)
    lemmas_inverted_index = defaultdict(set)

    for filename in os.listdir(tokens_dir):
        base_name = filename[len("tokens_"):-len(".txt")]  # Убираем префикс и расширение
        doc_id = int(base_name)  # Предполагаем, что имя файла - это ID документа

        # Читаем леммы
        with open(os.path.join(tokens_dir, filename), "r", encoding="utf-8") as file:
            for line in file:
                token = line.strip()
                tokens_inverted_index[token].add(doc_id)

    for key in tokens_inverted_index:
        tokens_inverted_index[key] = tokens_inverted_index[key]

    for filename in os.listdir(lemmas_dir):
        base_name = filename[len("lemmas_"):-len(".txt")]  # Убираем префикс и расширение
        doc_id = int(base_name)  # Предполагаем, что имя файла - это ID документа

        # Читаем леммы
        with open(os.path.join(lemmas_dir, filename), "r", encoding="utf-8") as file:
            for line in file:
                lemma, *tokens = line.strip().split()
                lemmas_inverted_index[lemma].add(doc_id)

    for key in lemmas_inverted_index:
        lemmas_inverted_index[key] = lemmas_inverted_index[key]

    return tokens_inverted_index, lemmas_inverted_index


# 2. Булев поиск
def boolean_search(query, inverted_index, total_docs):
    """
    Выполняет булев поиск по инвертированному индексу.
    :param query: Строка запроса.
    :param inverted_index: Инвертированный индекс.
    :param total_docs: Общее количество документов.
    :return: Множество ID документов, соответствующих запросу.
    """
    def evaluate(expression):
        """
        Рекурсивно вычисляет выражение для булева поиска.
        """
        if isinstance(expression, str):
            term = expression.lower()
            return inverted_index.get(term, set())

        operator, *operands = expression
        if operator == 'and':
            return set.intersection(*[evaluate(op) for op in operands])
        elif operator == 'or':
            return set.union(*[evaluate(op) for op in operands])
        elif operator == 'not':
            operand = evaluate(operands[0])
            return set(range(total_docs)) - operand

    # Парсинг запроса в дерево выражений
    def parse_query(query_string):
        """
        Преобразует строку запроса в дерево выражений.
        """
        tokens = re.findall(r'\(|\)|not|and|or|\w+', query_string)
        output = []
        operators = []

        precedence = {'not': 3, 'and': 2, 'or': 1}

        def apply_operator():
            operator = operators.pop()
            if operator == 'not':
                operand = output.pop()
                output.append((operator, operand))
            else:
                right = output.pop()
                left = output.pop()
                output.append((operator, left, right))

        for token in tokens:
            if token in ('and', 'or', 'not'):
                while (operators and operators[-1] != '(' and
                       precedence[operators[-1]] >= precedence[token]):
                    apply_operator()
                operators.append(token)
            elif token == '(':
                operators.append(token)
            elif token == ')':
                while operators[-1] != '(':
                    apply_operator()
                operators.pop()
            else:
                output.append(token)

        while operators:
            apply_operator()

        return output[0]

    parsed_query = parse_query(query)
    return evaluate(parsed_query)


def custom_json_dump(data, fp, indent=4):
    """
    Записывает JSON с отступами для основных ключей,
    но без отступов для вложенных списков.
    """

    def format_value(value):
        if isinstance(value, list):
            # Вложенные списки записываем в одну строку
            return "[" + ", ".join(map(str, value)) + "]"
        elif isinstance(value, set):
            return "{" + ", ".join(map(str, value)) + "}"
        return json.dumps(value, ensure_ascii=False)

    lines = []
    for key, value in data.items():
        # Основные ключи с отступами
        lines.append(f'"{key}": {format_value(value)}')

    # Объединяем строки с заданным отступом
    result = "{\n" + ",\n".join([f'{" " * indent}{line}' for line in lines]) + "\n}"
    fp.write(result)


# 3. Пример использования
if __name__ == "__main__":
    # Загрузка инвертированного индекса
    tokens_inverted_index, lemmas_inverted_index = load_tokens_and_lemmas(tokens_dir, lemmas_dir)

    # Сохранение инвертированного индекса
    import json
    with open("tokens_inverted_index.json", "w") as fp:
        custom_json_dump(tokens_inverted_index, fp)

    with open("lemmas_inverted_index.json", "w") as fp:
        custom_json_dump(lemmas_inverted_index, fp)

    # Определяем общее количество документов
    total_tokens_docs = len(os.listdir(tokens_dir))
    total_lemmas_docs = len(os.listdir(lemmas_dir))

    # Ввод запроса
    query_help = "Введите запрос (например, '(Клеопатра AND Цезарь) OR Помпей'): "
    query = input(query_help)

    # Выполнение поиска
    result_tokens = boolean_search(query.lower(), tokens_inverted_index, total_tokens_docs)
    result_lemmas = boolean_search(query.lower(), lemmas_inverted_index, total_lemmas_docs)

    main_result = (
        f"\nРезультаты поиска по запросу {query}:"
        f"\nДокументы для инвентированного индекса токенов: {', '.join(list(map(str, sorted(result_tokens))))}"
        f"\nДокументы для инвентированного индекса лемм: {', '.join(list(map(str, sorted(result_lemmas))))}"
    )
    print(main_result)





