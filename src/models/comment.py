from redis_om import HashModel

class Comment(HashModel):
    content: str
    user_id: str
    post_id: str