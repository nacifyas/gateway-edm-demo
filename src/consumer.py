import json
from dal.userdal import EXPIRATION, UserDAL
from models.user import User
from config.redis_conf import redis, redis_stream
import asyncio


ACTIVE_STREAMS = {
    'user':'$'
}


async def get_initial_streams() -> dict[str:str]:
    """ Retrieves the initial stream id for which
    the subscription loop should begins. It searches
    for the last processed id of a stream. If a new
    stream is created in the ACTIVE_STREAMS static
    variable, it will asign to it the id 0.

    Returns:
        dict[str:str]: All streams with their corresponding
        id from which the stream listener should start
        processing events
    """
    streams = {}
    for stream in ACTIVE_STREAMS.keys():
        if await redis.exists(f'stream:{stream}'):
            streams[stream] = await redis.get(f'stream:{stream}')
        else:
            streams[stream] = '0'
            await redis.set(f'stream:{stream}', '0')
    return streams


async def inicialize_streams():
    """ Checks for all streams in ACTIVE_STREAMS
    and creates them if these do not exist.
    
    Since the creation of a stream is an event of
    its own, the specified FLAG is of the type
    "CREATE [stream_name] STREAM"
    """
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


async def update_db_users_event(entry_data: dict[str:str]) -> None:
    """ Reacts to the event "UPDATE_DB". It feeds the DAL
    with all the data within the "entry_data"
    Loads the users array within the string.

    Args:
        entry_data dict[str:str]: A dictionary containing the events data
    """
    corr_arr = [UserDAL().create_user(User(**json.loads(user.replace("'",'"')))) for user in entry_data.values()]
    await asyncio.gather(*corr_arr)


async def create_user_event(entry_data: dict[str:str]) -> None:
    """ Reacts to the event "CREATE". This event contains
    confirmation regarding a creating user at the gateway.
    It changes the user status field its corresponding
    according to the data contained in the event.

    Args:
        entry_data dict[str:str]: A dictionary containing the events data
    """
    status = entry_data.get("STATUS")
    primary_key = entry_data.get("PRIMARY_KEY")
    user = await UserDAL().get_user_by_id(primary_key)
    user.status = status
    if status == "FAIL":
        await user.expire(EXPIRATION)
    await user.save()


async def delete_user_event(entry_data: dict[str:str]) -> None:
    """ Reacts to the event "DELETE". This events contains
    information regarding the deletion of a user. The deletion
    will be conducted through the UserDAL if this event approves
    it with, or it will be aborted, according to the event data.

    Args:
        entry_data dict[str:str]: Event data
    """
    status = entry_data.get("STATUS")
    primary_key = entry_data.get("PRIMARY_KEY")
    if status == "SUCCESS":
        await UserDAL().delete_user(primary_key)
    elif status == "FAIL":
        user = await UserDAL().get_user_by_id(primary_key)
        user.status = "FAILED DELETION"


async def stream_broker() -> None:
    """ Listens to the events broker in a blocking fashion,
    making use of the redis stream, push manner of
    delivering messages.

    Whenever this funcion if first time runned, it will
    always call "inicialize_streams", to check the streams
    existance  and "get_initial_streams" to get the last ids
    in the mentioned order, for its proper functioning.

    After having processed the pending messages from the
    last id, it sets all the streams to the "$" events, 
    which eventually starts the blocking for loop.

    During the processing of the content of the events
    entries, it runs a check for the sender of each message
    so it avoids processing by mistake its own emited events.

    For each operation triggered by an event, it calls a
    function wich performs the requiered operation
    """
    await inicialize_streams()
    streams = await get_initial_streams()
    while True:
        for message in await redis_stream.xread(streams, block=0):
            stream, stream_entry = message
            for entry in stream_entry:
                entry_id, entry_data = entry
                flag = entry_data.pop("FLAG")
                sender = entry_data.pop("SENDER")
                if sender == 'GATEWAY':
                    break
                if stream == 'user':
                    if flag == "UPDATE_DB":
                        asyncio.run(update_db_users_event(entry_data))
                    elif flag == "CREATE":
                        asyncio.run(create_user_event(entry_data))
                    elif flag == "DELETE":
                        asyncio.run(delete_user_event(entry_data))
            last_entry_id = stream_entry[-1][0]
            await redis.set(f'stream:{stream}', last_entry_id)
        streams = ACTIVE_STREAMS       


if __name__ == '__main__':
    asyncio.run(stream_broker())
