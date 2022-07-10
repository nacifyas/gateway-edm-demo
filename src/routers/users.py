from fastapi import APIRouter
from models.user import User
import requests

HOST = "localhost"
PORT = 8001

router = APIRouter(
    prefix="/users"
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
async def create(data: User):
    return requests.post(
        f"http://{HOST}:{PORT}/",
        data.json()
    ).json()

@router.put('/')
async def update(data: User):
    return requests.put(
        f"http://{HOST}:{PORT}/",
        data.json()
    ).json()

@router.delete('/')
async def delete(pk: str):
    return requests.delete(
        f"http://{HOST}:{PORT}/{pk}"
    ).json()
