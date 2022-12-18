import asyncio
import unittest
import redis
from aiogram.types import ReplyKeyboardMarkup

import dbq
import requester
import utls
from motor import motor_asyncio

import settings

class Tests(unittest.IsolatedAsyncioTestCase):
    async def test_connection_mongo(self):
        client = motor_asyncio.AsyncIOMotorClient(settings.DB_LINK)
        db = client.HSERUZ
        var = await db["tests"].find_one({"_id": 0})
        self.assertEqual(var["data"], "test")

    def test_connection_redis(self):
        redis_connection = redis.Redis(host=settings.redis_host, port=settings.redis_port)
        redis_connection.set("test", "ok")
        var = redis_connection.get("test")
        self.assertEqual(var, b"ok")
        pass

    async def test_kb_factory(self):
        neight_higgers= {"keyboard": [[{"text": "a"}, {"text": "b"}]]}
        var = dict(await utls.kb_factory(["a", "b"]))
        self.assertEqual(neight_higgers, var)

    async def test_name_factory(self):
        name = "kljasdkjlasdkljdajklasdjklsad"
        pass




async def main():
    #names = await requester.get_names("qwe")
    #print(names)
    #var = await utls.kb_factory(["a", "b"])
    #print(var)
    #dbq.start_db()
    #await dbq.add_schedule(609110006)
    pairs = await requester.scheduller("366440")
    print(pairs)
    pass


if __name__ == "__main__":
    #unittest.main()
    asyncio.run(main())
