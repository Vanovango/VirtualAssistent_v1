"""
Функционал

- голосовой ввод
- сохранение в json файл в необходимом формате
- сохраняет промпт после ключевого слова (TRIGGERS)
- сохраняет все что стоит после ключевого слова вне зависимости от длинны
- есть системные команды, которые нужны для расширения функционала

Условия
- работает локально
- необходимо, чтобы был создан файл result_prompt.json, иначе произойдет ошибка
"""

import json
import os
import queue
from datetime import datetime

import pyaudio
import vosk

import deepseek_api
import deepseek_local
import skills

# Настройки
MODEL_PATH = "./vosk_models/small-ru"  # Путь к модели Vosk
CHUNK = 16000  # Размер блока аудио данных
FORMAT = pyaudio.paInt16  # Формат аудио
CHANNELS = 1  # Количество каналов
RATE = 16000  # Частота дискретизации (должна соответствовать модели)
NAME_TRIGGERS = ['фома']  # кодовые слова, после которых начинается запись промптов для NLP модели
SYSTEM_TRIGGERS = ['админ', 'дмин']

# Инициализация очереди для хранения аудио данных
audio_queue = queue.Queue()


def add_data_to_json(new_data: dict) -> None:
    """
    Добавление и сохранение новых данных в существующий файл
    :param new_data: данные, которые надо добавить в json
    :return: None
    """
    file_path = "result_prompt.json"
    try:
        # Проверяем, существует ли файл
        if os.path.exists(file_path):
            # Если файл существует, загружаем его содержимое
            with open(file_path, 'r', encoding='utf-8') as file:
                json_data = json.load(file)  # Читаем существующие данные
    except:
        # Если файл не существует, создаем пустой список или словарь
        json_data = []

    # Добавляем новые данные
    json_data.append(new_data)

    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(json_data, file, ensure_ascii=False, indent=4)

# -----------------------------------------------------------------------------------------------
    # отправляем запрос в NLP модель
    # deepseek_api.get_prompt_from_json()   # deepseek-r1 через api
    deepseek_local.get_prompt_from_json()   # deepseek-r1 через локальную модель
# -----------------------------------------------------------------------------------------------


def save_prompt_to_json(text: str) -> None:
    """
    Сохраняем все что находится после триггера в формате json
    :param text: распознанная строка голосового ввода
    :return: None
    """
    result_dict = {'date': '', 'text': '', 'note': ''}  # словарь для хранения текущих данных
    text_list = list(text.split())

    for word in text_list:
        # проверяем есть ли слово в списке триггеров
        if word in NAME_TRIGGERS:
            # Получаем текущую дату и время
            now = datetime.now()
            # Форматируем дату и время в нужный формат "дд:мм:гг чч:мм"
            result_dict['date'] = now.strftime("%d:%m:%y %H:%M:%S")
            result_dict['text'] = ' '.join(text_list[text_list.index(word) + 1::])
            break

    add_data_to_json(result_dict)


def record_audio(queue) -> None:
    """
    Функция для записи аудио с микрофона
    :param queue: очередь прослушиваемого аудио-потока
    :return: None
    """
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("\nДля вызова системных команд используйте кодовое слово - 'админ'")
    print("Список возможных системных команд:")
    for command in skills.POSSIBLE_COMMANDS:
        print(f"    ---> {command}")
    print()

    while True:
        data = stream.read(CHUNK)
        queue.put(data)


# Основная функция для распознавания голоса
def recognize_speech(recognizer) -> None:
    """
    Функция распознавания речи
    :return: None
    """
    # Начинаем работать с голосом
    while True:
        if not audio_queue.empty():
            data = audio_queue.get()

            # Если данные есть, отправляем их в распознаватель
            if recognizer.AcceptWaveform(data):
                recognize_data = recognizer.Result()
                data_json = json.loads(recognize_data)  # переводим данные в формат json (dict)

                if any([trg in data_json['text'] for trg in NAME_TRIGGERS]):  # отработка произношения кодового слова
                    save_prompt_to_json(data_json['text'])
                elif any([trg in data_json['text'] for trg in SYSTEM_TRIGGERS]):
                    # вызываем системную команду, описанную в файле skills
                    skills.call_system_command(data_json['text'])


def init_vosk():
    # Загрузка модели Vosk
    model = vosk.Model(MODEL_PATH)
    recognizer = vosk.KaldiRecognizer(model, RATE)

    # TODO: автоматизировать процесс запуска сервера ollama
    # # Запускаем сервер с нейронкой через командную строку
    # # это нужно сделать в cmd
    # os.system('ollama serve')

    # Начало записи аудио в отдельном потоке
    import threading
    audio_thread = threading.Thread(target=record_audio, args=(audio_queue,))
    audio_thread.daemon = True
    audio_thread.start()

    recognize_speech(recognizer)


if __name__ == "__main__":
    init_vosk()
