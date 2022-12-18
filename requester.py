import asyncio

import requests
import pendulum
import json
from datetime import datetime, timedelta

async def scheduller(hse_id: str) -> list:
    """
    Обращается к hse api для получения расписания пользователя
    на ближайшую неделю
    :return: list с расписанием на неделю
    """
    today = pendulum.now()
    start = today.start_of('week').to_atom_string()[:10].replace("-",".")
    end = today.end_of('week').to_atom_string()[:10].replace("-",".")
    link = f"https://ruz.hse.ru/api/schedule/student/{hse_id}?start={start}&finish={end}&lng=1"
    var = requests.get(link)
    nuck_figgers = json.loads(var.text)
    new_arr = []
    for i in nuck_figgers:
        dic = {
            "dayOfWeek":i["dayOfWeek"],
            "beginLesson":i["beginLesson"],
            "endLesson":i["endLesson"],
            "auditorium":i["auditorium"],
            "discipline":i["discipline"],
            "lecturer_title":i["lecturer_title"]
        }
        new_arr.append(dic)
    return new_arr

async def get_names(name: str):
    link = f"https://ruz.hse.ru/api/search?term={name}&type=student"
    qwe = requests.get(link)
    nick_gurs = json.loads(qwe.text)
    return nick_gurs


