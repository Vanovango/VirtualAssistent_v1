import os

from vosk_recognition import recognize_speech

POSSIBLE_COMMANDS = ['очистить историю', 'конец работы']


def call_system_command(text: str):
    command = ' '.join(text.split()[1:])

    if command in list(SYSTEM_COMMANDS.keys()):
        SYSTEM_COMMANDS[command]()
    else:
        print('Команда некорректна, попробуйте снова )')
        print(command)
        recognize_speech()


def clean_history():
    """
    Очищает файл result_prompt.json (пересоздает его)
    :return: None
    """
    json_path = './history.json'

    os.remove(json_path)

    with open(json_path, 'w') as file:
        file.write('')

    """
        Очищает файл result_prompt.json (пересоздает его)
        :return: None
    """
    json_path = './result_prompt.json'

    os.remove(json_path)

    with open(json_path, 'w') as file:
        file.write('')

    print("История очищена! Ваши секреты останутся неизвестны ;)")


def close_app():
    """
    Завершает работу программы
    :return: None
    """
    print("До новых встреч, я пошел отдыхать!")
    quit()


SYSTEM_COMMANDS = {
    'очистить историю': clean_history,
    'очистить история': clean_history,
    'очисть историю': clean_history,
    'очисть история': clean_history,
    'очистить историю запросов': clean_history,
    'очистить история запросов': clean_history,
    'очисть историю запросов': clean_history,
    'очисть история запросов': clean_history,
    'очистить историю запросами': clean_history,
    'очистить история запросами': clean_history,
    'очисть историю запросами': clean_history,
    'очисть история запросами': clean_history,

    'конец работы': close_app,
    'конец роботы': close_app,
    'завершение работы': close_app,
    'завершения работы': close_app,
    'завершение роботы': close_app,
    'завершения роботы': close_app,
    'закрой приложение': close_app,
}
