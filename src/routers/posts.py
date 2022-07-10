from fastapi import APIRouter
from models.post import Post
import requests

HOST = "localhost"
PORT = 8002

router = APIRouter(
    prefix="/posts"
)

@router.get('/{pk}')
async def get(pk: str):
    return requests.get(
        f"http://{HOST}:{PORT}/{pk}"
    ).json()

@router.get('/')
async def get_all():
    return requests.get(
        f"http://{HOST}:{PORT}/"
    ).json()

@router.post('/')
async def create(data: Post):
    return requests.post(
        f"http://{HOST}:{PORT}/",
        data.json()
    ).json()

@router.put('/')
async def update(data: Post):
    return requests.put(
        f"http://{HOST}:{PORT}/",
        data.json()
    ).json()

@router.delete('/')
async def delete(pk: str):
    return requests.delete(
        f"http://{HOST}:{PORT}/{pk}"
    ).json()
