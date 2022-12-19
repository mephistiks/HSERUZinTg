import aiogram.utils.callback_data
from aiogram import types
from aiogram.types import InlineKeyboardMarkup

import requester

user_cb = aiogram.utils.callback_data.CallbackData('post', 'id', 'action')


async def schedule_factory(arr: list, n: int) -> str:
    """
    Если расписание содержит >=1 элемента, вызвращает текст с ним на определённый день недели, если 0, возвращается False
    :param arr: ответ от hse api с массивом расписания пользователя
    :param n: день недели
    :return: текст с расписание готовый к отправке
    """
    print(type(n))
    print(arr)
    new_arr = []
    for i in arr:
        if i["dayOfWeek"] == n:
            new_arr.append(i)
    message = ""
    for ind, i in enumerate(new_arr):
        tmp = f"{ind}) {i['auditorium']} в {i['beginLesson']}\n"
        tmp += f"{i['discipline']}\n"
        tmp += f"{i['lecturer_title']}\n\n"
        message += tmp
    return message


async def names_factory(name) -> bool | InlineKeyboardMarkup:
    """
    Возвращает inline клавиатуру с доступными именами
    :param name: ФИО
    :return: types.InlineKeyboardMarkup c ФИО | bool в случае ошибки
    """
    arr = await requester.get_names(name)
    if len(arr) == 0:
        return False
    names_arr = ((i["id"], i["label"]) for i in arr[:3])
    markup = types.InlineKeyboardMarkup()
    for _id, text in names_arr:
        markup.add(
            types.InlineKeyboardButton(
                text,
                callback_data=user_cb.new(id=_id, action="choose")),
        )
    return markup


async def kb_factory(btns: list):
    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    keyboard.add(*(types.KeyboardButton(text) for text in btns))
    return keyboard
