import asyncio
from fastapi import APIRouter, HTTPException, status
from models.user import User
import requests
from redis_conf import redis



HOST = "localhost"
PORT = 8001
MS = "user"
CACHE_HOLD = 50

router = APIRouter(
    prefix="/users"
)


@router.get('/{primary_key}', response_model=User, status_code=status.HTTP_200_OK)
async def get_user_by_Id(primary_key: str) -> User:
    key = f"cache:{MS}:{primary_key}"
    key_nx = f"cache-nx:{MS}:{primary_key}"
    if await redis.exists(key):
        return await redis.hgetall(key)
    elif await redis.exists(key_nx):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    else:
        response = requests.get(
            f"http://{HOST}:{PORT}/{primary_key}"
        )
        if response.status_code == status.HTTP_404_NOT_FOUND:
            await redis.set(key_nx, "null")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        else:
            data = response.json()
            user = User(**data)
            print(data)
            await redis.hmset(key, data)
            return user


@router.get('/', response_model=list[User], status_code=status.HTTP_200_OK)
async def get_all_users(offset: int = 0, limit: int = 50) -> list[User]:
    publishion, keys = await asyncio.gather(
        redis.publish("user",f"UPDATE_DB:{CACHE_HOLD}:{offset}:{limit}"), redis.keys(f"cache:{MS}:*")
    )
    corr_arr = []
    for key in keys:
        corr_arr.append(redis.hgetall(key))
    return await asyncio.gather(*corr_arr)


@router.post('/', response_model=User, status_code=status.HTTP_201_CREATED)
async def create(data: User) -> User:
    key = f"cache:{MS}:{data.pk}"
    key_nx = f"cache-nx:{MS}:{data.pk}"
    await asyncio.gather(
        redis.delete(key_nx),
        redis.publish("user:CREATE", f"{key}:{str(data.json())}"),
        redis.hmset(key, data.dict())
    )
    return data


@router.put('/', response_model=User, status_code=status.HTTP_202_ACCEPTED)
async def update(data: User) -> User:
    key = f"cache:{MS}:{data.pk}"
    await asyncio.gather(
        redis.publish("user:UPDATE", f"{key}:{str(data.json())}"),
        redis.hmset(key, data.dict())
    )
    return data


@router.delete('/', status_code=status.HTTP_202_ACCEPTED)
async def delete(primary_key: str) -> int:
    key = f"cache:{MS}:{primary_key}"
    key_nx = f"cache-nx:{MS}:{primary_key}"
    if await redis.exists(key_nx):
        return 0
    else:    
        deletion, store_nx, publishion = await asyncio.gather(
            redis.delete(key),
            redis.set(key_nx, "null"),
            redis.publish("user:DELETE", f"{key}")
        )
        return deletion
