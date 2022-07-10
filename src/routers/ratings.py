from fastapi import APIRouter
from models.rating import Rating
import requests

router = APIRouter(
    prefix="/ratings"
)

HOST = "localhost"
PORT = 8004


@router.get('/{pk}')
async def get(pk: str):
    return requests.get(
        f"http://{HOST}:{PORT}/{pk}"
    ).json()

@router.get('/')
async def get_all():
    return requests.get(
        f"http://{HOST}:{PORT}"
    ).json()

@router.post('/')
async def create(data: Rating):
    return requests.post(
        f"http://{HOST}:{PORT}",
        data.json()
    ).json()

@router.put('/')
async def update(data: Rating):
    return requests.put(
        f"http://{HOST}:{PORT}",
        data.json()
    ).json()

@router.delete('/')
async def delete(pk: str):
    return requests.delete(
        f"http://{HOST}:{PORT}/{pk}"
    ).json()


@router.get('/post/{post_pk}')
async def post_ratings(post_pk: str):
    return requests.get(
        f"http://{HOST}:{PORT}/post/{post_pk}"
    )
