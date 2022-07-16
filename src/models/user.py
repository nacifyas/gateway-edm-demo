from aredis_om import HashModel, Field
from redis_conf import redis


class UserRead(HashModel):
    username: str
    age: int
    password: str

    class Meta:
        database = redis

class User(UserRead):
    status: str = "PROCESSING"

    class Meta:
        database = redis
