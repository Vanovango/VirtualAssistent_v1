import json
import os
import re
from datetime import datetime

import ollama

from text_to_sound import tex_to_sound

# скаченные модели
# "deepseek-r1:8b" | "deepseek-r1:32b" | "deepseek-r1:14b" | "qwen2.5:14b" | "deepseek-r1"
MODEL = "deepseek-r1:8b"

# Дополнительные параметры для запроса в gpt модель
PROMPT_PARAMETERS = ".  Ответ пиши на русском языке. " \
                    "Все числа пиши словами (не используй римские или арабские цифры). " \
                    "Ответ предоставь в виде текста, записанного в строку, " \
                    "не используй таблицы, различные выделения ответа. " \
                    "Объясни простым языком без формул и примеров. "


def clean_answer(answer):
    """
        Очищает текст от нежелательных символов и маркеров.

        :param answer: Исходный текст.
        :return: Очищенный текст.
        """
    # Удаляем маркеры и лишние символы
    cleaned_text = re.sub(r'[*#]', '', answer)  # Удаляем все тексты в квадратных скобках
    cleaned_text = cleaned_text.strip()  # Удаляем лишние пробелы
    return cleaned_text


def get_prompt_from_json():
    """
    Достаем последний сохраненный вопрос из result_prompt.json
    :return: None
    """
    with open('./result_prompt.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    question = data[-1]['text'] + PROMPT_PARAMETERS
    answer = clean_answer(deepseek_predict(question))

    save_qa(question, answer)


def save_qa(question, answer):
    """
    Сохраняем вопрос и ответ в history.json
    :param question: Задаваемый модели вопрос
    :param answer: Полученный от модели ответ
    :return: None
    """
    print(f"\n --> Вопрос: {question}\n")
    file_path = "./history.json"
    try:
        # Проверяем, существует ли файл
        if os.path.exists(file_path):
            # Если файл существует, загружаем его содержимое
            with open(file_path, 'r', encoding='utf-8') as file:
                history = json.load(file)  # Читаем существующие данные
    except:
        # Если файл не существует, создаем пустой список или словарь
        history = []

    # Получаем текущую дату и время
    now = datetime.now()
    new_data = {
        'date': now.strftime("%d:%m:%y %H:%M:%S"),
        'question': question,
        'answer': answer
    }
    # Добавляем новые данные
    history.append(new_data)

    # Записываем новые данные в файл
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(history, file, ensure_ascii=False, indent=4)

    print(f"\n --> Ответ: {answer}")
    tex_to_sound()


def deepseek_predict(prompt):
    """
    Функция получения ответа от модели
    :param prompt: Запрос, отправляемый в модель.
    :return: Возвращает полученный ответ от gpt
    """
    print("\n Думаю...")

    client = ollama.Client()

    model_reply = client.generate(model=MODEL, prompt=prompt)

    tmp = []
    flag = False
    for word in list(model_reply.response.split()):
        if flag:
            tmp.append(word)
        if word == "</think>":
            flag = True

    return ' '.join(tmp)
