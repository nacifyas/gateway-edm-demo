from dal.userdal import UserDAL
from redis_conf import redis
from models.user import User
import asyncio
import json

async def check_channel():
    pubsub = redis.pubsub()
    await pubsub.subscribe('user:UPDATE_DB-res', 'user:CREATE-res', 'user:UPDATE-res')
    try:
        async for message in pubsub.listen():
            print(f"channel: {message.get('channel')} ; data: {message.get('data')}")
            data: str = message.get("data")
            if message.get("channel") == 'user:UPDATE_DB-res' and data not in range(4):
                user_arr = data.split('--')
                corr_arr = [UserDAL().create_user(User(**json.loads(user.replace("'",'"')))) for user in user_arr]
                await asyncio.gather(*corr_arr)
            elif (message.get("channel") == 'user:CREATE-res' or message.get("channel") == 'user:CREATE-res') and data not in range(4):
                data_arr = data.split(':')
                status = data_arr[0]
                key = data_arr[1]
                details = data_arr[2]
                if status == 'ERROR':
                    redis.hmset(key, {'error' : details})

    except Exception as e:
        raise e

if __name__ == '__main__':
    asyncio.run(check_channel())
