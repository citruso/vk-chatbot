# -*- coding: utf-8 -*-

from settings import letters_RUS, letters_ENG
import random
import json

def create_answer(text, payload):
    text = text.lower()

    words = {
        'cancel': ['отмена'],
        'art': ['арт'],
        'anime': ['случайное'],
        'gif': ['гифка'],
        'detect': ['угадай'],
        'ads': [
            'ads',
            'реклама',
            'рекламка',
            'вп',
            'впшер',
            'пиар',
            'пропиариться',
            'прайс',
            'сотрудничать',
            'сотрудничество',
            'товар'
        ]
    }

    answers = {
        'start': ['Привет, {}! '],
        'cancel': ['Главное меню'],
        'who': ['Я бот Genius. Лично подбираю аниме арты для этого паблика.'],
        'art': ['Наслаждайся', 'Милашка', 'Лапочка'],
        'anime': [''],
        'gif': ['Вот, держи'],
        'detect': ['Теперь пришли мне картинку и я попробую угадать, что на ней изображено.'],
        'attention': ['&#9888; Внимание, во избежание значительной нагрузки на бота он принимает команды раз в 5 секунд!\n'],
        'ads': ['Администратор скоро свяжется с вами &#128526; \n{}'.format(getServiceNotice('freeze'))],
        'what': ['Я не понимаю тебя...', 'Что?', 'О чем ты?', 13611, 13612, 13614, 13367, 13016, 12967, 12910, 15104]
    }

    smiles = {
        ('key_hello','art','gif','morning','sleep','whatsup'): ['&#128522;','&#128515;','&#128521;','&#128527;','&#128524;','&#128516;'],
        'key_bye': ['&#128530;','&#128532;','&#128546;','&#128543;','&#128577;','&#128542;'],
        'who': ['&#128373;','&#128125;','&#129302;','&#129313;'],
        'what': ['&#128533;','&#128559;','&#128529;','&#129300;','&#128579;','&#128580;']
    }

    for x in text:
        if not (x in letters_RUS or x in letters_ENG):
            text = text.replace(x, '')

    if payload is None:
        for x in words.keys():
            if len(set(text.split(' ')) & set(words[x])) != 0:
                key = x
                break
        else:
            return '', 'notResponse'

        done = random.choice(answers.get(key, ['']))
    else:
        key = json.loads(payload)['command']

        return random.choice(answers.get(key, [''])), key


    if type(done) is str:
        for _ in [x for x in smiles.keys() if key in x]:
            done += random.choices([' ' + random.choice(smiles[[x for x in smiles.keys() if key in x][0]]), ''], weights=[50,50])[0]

    if key is 'start':
        done += '\n'+answers['who'][0]+'\n\n'+answers['attention'][0]

    return done, key

def getServiceNotice(key):
    notices = {
        'ready': '&#9989; Бот ответит Вам прямо сейчас!',
        'wait': '&#9203; Не спеши',
        'freeze': '&#9888; Внимание, для удобства общения с администратором бот будет заморожен!',
        'exception': 'Кажется, что-то пошло не так &#128543; Попробуйте позже.\n Администратор был уведомлён об этом инциденте.',
        'complete': 'Команда выполнена. Лог: ',
        'back': '&#9664; Вы вернулись назад',
        'cancel': '&#10060; Вы отменили команду',
        'ads': 'Важное',
        'posts': 'Проверь посты',
        'notDetected': 'Не удалось распознать изображение.',
        'wrongType': 'Я работаю только с изображениями, а ты отправил мне объект [{}].',
        'manyFiles': 'Мне нужно только одно изображение.',
        'emptyAttachments': 'Ты забыл прикрепить изображение.',
        'tryAgain': 'Попробуй ещё раз.'
    }

    return notices[key]