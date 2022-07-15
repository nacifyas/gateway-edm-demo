import json
from dal.userdal import UserDAL
from models.user import User
from redis_conf import redis, redis_stream
import asyncio


ACTIVE_STREAMS = {
    'user':'$',
    'post':'$'
}


async def get_initial_streams() -> dict[str:str]:
    streams = {}
    for stream in ACTIVE_STREAMS.keys():
        if await redis.exists(f'stream:{stream}'):
            streams[stream] = await redis.get(f'stream:{stream}')
        else:
            streams[stream] = '0'
            await redis.set(f'stream:{stream}', '0')
    return streams


async def inicialize_streams():
    for stream in ACTIVE_STREAMS.keys():
        if not await redis_stream.exists(stream):
            await redis_stream.xadd(
                stream,
                fields={
                    'FLAG':f'CREATE {stream} STREAM',
                    'SENDER':'GATEWAY'
                },
                maxlen=10000
            )


async def stream_broker() -> None:
    await inicialize_streams()
    streams = await get_initial_streams()
    while True:
        print(streams)
        for message in await redis_stream.xread(streams, block=0):
            print(message)
            stream, stream_entry = message
            for entry in stream_entry:
                entry_id, entry_data = entry
                flag = entry_data.pop("FLAG")
                sender = entry_data.pop("SENDER")
                if sender == 'GATEWAY':
                    break
                if stream == 'user':
                    if flag == "UPDATE_DB":
                        corr_arr = [UserDAL().create_user(User(**json.loads(user.replace("'",'"')))) for user in entry_data.values()]
                        await asyncio.gather(*corr_arr)
                    elif flag == "CREATE":
                        status = entry_data.get("STATUS")
                        primary_key = entry_data.get("PRIMARY_KEY")
                        message = entry_data.get("MESSAGE")
                        if status == "SUCCESS":
                            user = await UserDAL().get_user_by_id(primary_key)
                            user.status = status
                # elif stream == 'post':
                #     if flag == "UPDATE_DB":
                        # corr_arr = [PostDAL().create_post(Post(**json.loads(post.replace("'",'"')))) for post in entry_data.values()]
                        # await asyncio.gather(*corr_arr)
                        # pass
            last_entry_id = stream_entry[-1][0]
            await redis.set(f'stream:{stream}', last_entry_id)
        streams = ACTIVE_STREAMS       


if __name__ == '__main__':
    asyncio.run(stream_broker())


# a_message = ['stream',
#         [
#             ('id', {'foo': 'bar'}),
#             ('1657877859857-0', {'key': 'value'}), 
#             ('1657877924620-0', {'key': 'value'})
#         ]
#     ]

# list_of_messages = [
#     ['test2',
#         [
#             ('1657877191536-0', {'shall': 'we'}),
#             ('1657877859857-0', {'key': 'value'}), 
#             ('1657877924620-0', {'key': 'value'})
#         ]
#     ], 
#     ['test', 
#         [
#             ('1657876148555-0', {'foo': 'bar'}),
#             ('1657876164292-0', {'foo': 'bar'}),
#             ('1657876239169-0', {'key': 'value'}),
#             ('1657876459676-0', {'key': 'value'}),
#             ('1657876489402-0', 
#                                   {
#                                     'FLAG': 'UPDATE_DB',
#                                     'User': "doing bussines'"
#                                   }
#              ),
#             ('1657876520882-0', {'12': 'then 4'}),
#             ('1657876996505-0', {'say': 'hellooo'}),
#             ('1657877037118-0', {'key1': 'value1', 'key2': 'value2', 'key3': 'value3'}),
#             ('1657877146757-0', {'satus': 'hello', 'status 2.0': 'hello 2.0'}),
#             ('1657877852438-0', {'key': 'value'}),
#             ('1657877917734-0', {'key': 'value', '': ''})
#         ]
#     ]
# ]


# from dal.userdal import UserDAL
# from redis_conf import redis
# from models.user import User
# import asyncio
# import json

# async def check_channel():
#     pubsub = redis.pubsub()
#     await pubsub.subscribe('user:UPDATE_DB-res', 'user:CREATE-res', 'user:UPDATE-res')
#     async for message in pubsub.listen():
#         data: str = message.get("data")
#         if message.get("type") == 'user:UPDATE_DB-res' and data not in range(4):
#             user_arr = data.split('--')
#             corr_arr = [UserDAL().create_user(User(**json.loads(user.replace("'",'"')))) for user in user_arr]
#             await asyncio.gather(*corr_arr)
#         elif (message.get("channel") == 'user:CREATE-res' or message.get("channel") == 'user:CREATE-res') and data not in range(4):
#             data_arr = data.split(':')
#             status = data_arr[0]
#             key = data_arr[1]
#             details = data_arr[2]
#             if status == 'ERROR':
#                 redis.hmset(key, {'error' : details})

# if __name__ == '__main__':
    # asyncio.run(check_channel())
