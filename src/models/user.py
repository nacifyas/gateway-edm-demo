from aredis_om import HashModel
from redis_conf import redis

class User(HashModel):
    username: str
    age: int
    password: str

    class Meta:
        database = redis
