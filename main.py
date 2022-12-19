import logging
import typing

from aiogram import Bot, Dispatcher, executor, types

import dbq
import utls
from settings import API_KEY
import settings

from localization import ru

import redis

from utls import kb_factory

ban = types.ReplyKeyboardRemove()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_KEY)
dp = Dispatcher(bot)

redis_connection: redis.client.Redis


async def clear(tg_id: int) -> None:
    """
    очищает стейт пользователя в редисе
    """
    redis_connection.set(tg_id, "home")


async def send_home(tg_id: int) -> None:
    """
    переносит пользователя на стартовую страницу кнопок
    """
    await clear(tg_id)
    kb = await kb_factory(ru.main_menu)
    await bot.send_message(chat_id=tg_id, text=ru.home, reply_markup=kb)


@dp.message_handler(commands=['start', 'help'])
async def start_cmd_handler(message: types.Message):
    """
    Отлавливатель /start
    """
    _id = message.from_user.id
    await message.answer(text=ru.welcome)
    await send_home(_id)


@dp.message_handler(text=[ru.schedule])
async def get_schedule(message: types.Message):
    _id = message.from_user.id
    await bot.send_message(chat_id=_id, text=ru.get_day)
    redis_connection.set(_id, "sch")


@dp.message_handler(text=[ru.home])
async def cmd_send_home(message: types.Message):
    await send_home(message.from_user.id)


@dp.message_handler(text=[ru.choose_type])
async def get_help(message: types.Message):
    kb = {"inline_keyboard": [[{"text": "Группа", "callback_data": "group"}], [{"text": "Студент", "callback_data": "student"}], [{"text": "Преподаватель", "callback_data": "person"}], [{"text": "Аудитория", "callback_data": "auditorium"}]]}
    await bot.send_message(chat_id=message.from_user.id, text=ru.type_text, reply_markup=kb)


@dp.message_handler(text=[ru.change_user])
async def change_user(message: types.Message):
    """
    Когда пользователь пытается изменить наблюдаемое имя
     - его стейт в редисе меняется на name,
     для последующего отлова его сообщения с именем для отслеживания
    """
    _id = message.from_user.id
    await bot.send_message(chat_id=_id, text=ru.give_ur_name)
    redis_connection.set(_id, "name")


@dp.message_handler()
async def all_msg_handler(message: types.Message):
    """
    Отлавливает все сообщения,
    на самом деле нужен в случаях перехода пользователя на 'второй уровень' кнопок,
    так же ловит все непредвиденные случаи
    """
    text = message.text
    # print(text)
    _id = message.from_user.id
    logger.debug('Кнопка %r', text)
    state = redis_connection.get(message.from_user.id).decode()
    match state:
        case "name":
            tp = await dbq.get_type(_id)
            names = await utls.names_factory(text, tp)
            if not names:
                await message.answer(ru.give_ur_name)
                await message.answer(ru.try_again)
                return
            return await message.answer(ru.chose_or_try, reply_markup=names)
        case "sch":
            if not (text.strip()).isdigit():
                await message.answer(ru.get_day)
                await message.answer(ru.try_again)
                return
            sch = await dbq.get_schedule(_id)
            new_sch = await utls.schedule_factory(sch, int(text))
            return await message.answer(new_sch)
        case _:
            await message.answer(ru.smthng_wrong)
            send_home(_id)


@dp.callback_query_handler(utls.user_cb.filter(action='choose'))
async def set_name(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):
    _id = query.from_user.id
    await dbq.set_id(tg_id=_id, hse_id=callback_data["id"])
    await bot.send_message(_id, ru.succes)
    await dbq.add_schedule(_id, tp=await dbq.get_type(_id))
    await send_home(_id)



@dp.callback_query_handler(text='group')
@dp.callback_query_handler(text='person')
@dp.callback_query_handler(text='student')
@dp.callback_query_handler(text='auditorium')
async def set_type(query: types.CallbackQuery):
    _id = query.from_user.id
    text = query.data
    #print(query.message.message_id)
    await bot.delete_message(query.from_user.id, query.message.message_id)
    await bot.send_message(query.from_user.id, "Тип успешно выбран")
    await dbq.set_type(tg_id=_id, tp=text)

async def startup(*args) -> None:
    """
    Запуск подключений к MongoDB и Redis
    :param args: нужно для отлова все параметров котоыре перадаёт executor.start_polling, иначе не запускается
    """
    dbq.start_db()
    global redis_connection
    redis_connection = redis.Redis(host=settings.redis_host, port=settings.redis_port)
    # asyncio.create_task(scheduler())
    logger.info("===================")
    logger.info("Приложение включено")
    logger.info("===================")


async def shutdown(*args):
    global redis_connection
    redis_connection.close()
    logger.info("====================")
    logger.info("Приложение выключено")
    logger.info("====================")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=startup, on_shutdown=shutdown)
