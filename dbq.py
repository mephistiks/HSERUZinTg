from motor import motor_asyncio

import requester
from settings import DB_LINK

db: motor_asyncio.AsyncIOMotorDatabase


def start_db():
    global db
    client = motor_asyncio.AsyncIOMotorClient(DB_LINK)
    db = client.HSERUZ


async def set_id(*, tg_id: int, hse_id: str) -> None:
    """
    Приниммает на вход id телеграм пользователя, и id в hse системе
    и связывает их
    """
    if (var := await db["user"].find_one({"_id": tg_id})) is not None:
        await db["user"].update_one({"_id": tg_id}, {"$set": {"hse_id": hse_id}})
    else:
        data = {"_id": tg_id, "hse_id": hse_id}
        await db["user"].insert_one(data)


async def set_type(*, tg_id: int, tp: str) -> bool | None:
    """
    Сохраняет пользователю тип поиска (группа, аудитория, студент, преподаватель)
    :param tp: тип поиска
    """
    if (var := await db["user"].find_one({"_id": tg_id})) is not None:
        await db["user"].update_one({"_id": tg_id}, {"$set": {"type": tp}})
    else:
        return False

async def get_type(tg_id: int):
    if (var := await db["user"].find_one({"_id": tg_id})) is not None:
        return var["type"]
    else:
        return False

async def get_schedule(tg_id: int):
    if (var := await db["user"].find_one({"_id": tg_id})) is not None:
        return var["schedule"]
    else:
        return False

async def add_schedule(tg_id: int, tp:str):
    # get full_name
    # get schedule
    if (var := await db["user"].find_one({"_id": tg_id})) is not None:
        hse_id = var["hse_id"]
        sch = await requester.scheduller(hse_id, tp)
        await db["user"].update_one({"_id": tg_id}, {"$set": {"schedule": sch}})
        return True
    else:
        return False
