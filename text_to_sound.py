import json

import pyttsx3


def tex_to_sound():
    # Инициализация движка озвучки
    engine = pyttsx3.init()

    with open('./history.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    # Текст для озвучивания
    text = data[-1]['answer']

    # Установка скорости речи (необязательно)
    engine.setProperty('rate', 200)  # Скорость речи (по умолчанию 200)

    # Озвучиваем текст
    engine.say(text)
    engine.runAndWait()
