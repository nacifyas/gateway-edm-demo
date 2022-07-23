import json
import asyncio
from models.user import User
from config.variables import THIS_SERVICE
from dal.userdal import UserDAL
from config.redis_conf import redis, redis_stream

""" The events topology
consists of the following
structure:
    event: dict[str:str] = {
        SENDER [<MICROSERVICE NAME>]: Specifies who is behind
        the sent event. It serves useful to avoid retrofeeding
        its own events.
        
        OP [CREATE, READ, UPDATE, DELETE]: Represents
        the operation regarding the event.

        DATA: Data in key-value pairs, added as
        more entries, or as a large string, that will
        be parssed when retrieved. It could contain
        the keys separated by commas, that need to be
        retrieved to get the needed data
    }
"""

ACTIVE_STREAMS = {
    'user':'$'
}
STREAM_MAX_LENGHT = 10000


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
    its own, the specified its fields will consist
    of:
        event = {
            SENDER: The microservice who created the
            missing streams

            OP: CREATE_STREAM
            It uses this special variant of CREATE
            to avoid this event being accidentally
            processed

            DATA: <stream name>
        }
    """
    for stream in ACTIVE_STREAMS.keys():
        if not await redis_stream.exists(stream):
            event = {
                'SENDER': THIS_SERVICE,
                'OP': 'CREATE_STREAM',
                'DATA': stream
            }
            await redis_stream.xadd(
                name=stream,
                fields=event,
                maxlen=STREAM_MAX_LENGHT
            )


async def read_user_event(entry_data: dict[str:str]) -> None:
    """ Reacts to the event "READ", which contains updates
    or information regarding a service database.
    It feeds the DAL with all the data within the "entry_data"
    Loads the users array within the string.

    Args:
        entry_data dict[str:str]: A dictionary containing db entries
        for each of its values
    """
    entry_data.pop('DATA', '')
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
    key = entry_data.get("DATA")
    user_str = entry_data.pop(key)
    user = User(**json.loads(user_str.replace("'",'"')))
    await UserDAL().create_user(user)


async def delete_user_event(entry_data: dict[str:str]) -> None:
    """ Reacts to the event "DELETE". This events contains
    information regarding the deletion of a user. The deletion
    will be conducted through the UserDAL if this event approves
    it with, or it will be aborted, according to the event data.

    Args:
        entry_data dict[str:str]: Event data
    """
    primary_key = entry_data.get("DATA")
    await UserDAL().delete_user(primary_key)


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
                sender = entry_data.pop("SENDER")
                operation = entry_data.pop("OP")
                if sender == THIS_SERVICE:
                    break
                if stream == 'user':
                    if operation == "READ":
                        asyncio.run(read_user_event(entry_data))
                    elif operation == "CREATE":
                        asyncio.run(create_user_event(entry_data))
                    elif operation == "DELETE":
                        asyncio.run(delete_user_event(entry_data))
            last_entry_id = stream_entry[-1][0]
            await redis.set(f'stream:{stream}', last_entry_id)
        streams = ACTIVE_STREAMS       


if __name__ == '__main__':
    asyncio.run(stream_broker())
