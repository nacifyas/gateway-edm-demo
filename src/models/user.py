from redis_om import HashModel

class User(HashModel):
    username: str
    age: int
    password: str