from fastapi import APIRouter
from models.comment import Comment
import requests

HOST = "localhost"
PORT = 8003

router = APIRouter(
    prefix="/comments"
)

@router.get('/{pk}')
async def get(pk: str):
    return requests.get(
        f"http://{HOST}:{PORT}/{pk}"
    ).json()

@router.get('/')
async def get_all():
    return requests.get(
        f"http://{HOST}:{PORT}:8003/"
    ).json()

@router.post('/')
async def create(data: Comment):
    return requests.post(
        f"http://{HOST}:{PORT}/",
        data.json()
    ).json()

@router.put('/')
async def update(data: Comment):
    return requests.put(
        f"http://{HOST}:{PORT}/",
        data.json()
    ).json()

@router.delete('/')
async def delete(pk: str):
    return requests.delete(
        f"http://{HOST}:{PORT}/{pk}"
    ).json()
