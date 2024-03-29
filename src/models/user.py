from aredis_om import HashModel
from config.redis_conf import redis


class UserCreate(HashModel):
    username: str
    age: int
    password: str

    class Meta:
        database = redis

class User(UserCreate):
    status: str = "PROCESSING"
