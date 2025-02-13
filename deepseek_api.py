import json

import requests
import os
from datetime import datetime

from text_to_sound import tex_to_sound

# внутри скобок свой апи ключ отсюда https://openrouter.ai/settings/keys
API_KEY = "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"
MODEL = "deepseek/deepseek-r1"


def save_qa(question, answer):
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

    print("\nДанные успешно добавлены в файл.")
    tex_to_sound()


def get_prompt_from_json():
    with open('./result_prompt.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    print(data[-1]['text'])
    chat_stream(data[-1]['text'])


def process_content(content):
    return content.replace('<think>', '').replace('</think>', '')


def chat_stream(prompt):
    print("Думаю...")
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": True
    }

    with requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            stream=True
    ) as response:
        if response.status_code != 200:
            print("Ошибка API:", response.status_code)
            return ""

        full_response = []

        for chunk in response.iter_lines():
            if chunk:
                chunk_str = chunk.decode('utf-8').replace('data: ', '')
                try:
                    chunk_json = json.loads(chunk_str)
                    if "choices" in chunk_json:
                        content = chunk_json["choices"][0]["delta"].get("content", "")
                        if content:
                            cleaned = process_content(content)
                            print(cleaned, end='', flush=True)
                            full_response.append(cleaned)
                except:
                    pass

        print()  # Перенос строки после завершения потока
        print("Задавайте новый вопрос, я жду...\n")

        answer = ''.join(full_response)
        save_qa(prompt, answer)
