import uvicorn
from fastapi import FastAPI
from fastapi.background import BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from routers import users, posts, comments, ratings
from redis_conf import redis


app = FastAPI()

app.include_router(users.router)
app.include_router(posts.router)
app.include_router(comments.router)
app.include_router(ratings.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*']
)


@app.get('/pubsub')
def check_channel():
    pubsub = redis.pubsub()
    pubsub.subscribe('test')
    try:
        for message in pubsub.listen():
            print(message)
    except Exception as e:
        raise e


if __name__ == '__main__':
    uvicorn.run("main:app", port=8000, reload=True, host="127.0.0.1")
