from redis_om import HashModel

class Rating(HashModel):
    rating: int
    user_id: str
    post_id: str