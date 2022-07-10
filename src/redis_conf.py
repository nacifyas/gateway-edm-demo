from redis_om import get_redis_connection

REDIS_HOST = "atomflare.af"
REDIS_PORT = "6388"
ENCODING = "utf-8"

redis = get_redis_connection(
    host=REDIS_HOST,
    port=REDIS_PORT,
    encoding=ENCODING,
    decode_responses=True
)