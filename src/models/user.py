from aredis_om import HashModel, Field
from redis_conf import redis

class User(HashModel):
    username: str = Field(index=True, full_text_search=True)
    age: int
    password: str
    status: str = "PROCESSING"

    class Meta:
        database = redis
