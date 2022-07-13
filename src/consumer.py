from redis_conf import redis
import asyncio

async def check_channel():
    pubsub = redis.pubsub()
    await pubsub.subscribe('user:CREATE', 'user:UPDATE', 'user:DELETE')
    try:
        async for message in pubsub.listen():
            print(message)
            if message:
                pass
            elif message:
                pass
            elif message:
                pass
    except Exception as e:
        raise e

if __name__ == '__main__':
    asyncio.run(check_channel())