from ast import Not
import asyncio
from fastapi import status
from redis_conf import redis
from redis_om import NotFoundError
from models.user import User
import requests


MS = "user"
HOST = "localhost"
PORT = 8001
EXPIRATION = 360

class UserDAL:
    """Data Access Layer for Users. This API handles the access to data
    and simplifies the process for CRUD operations. All the below methods
    do exactly what they are intended to do, with no side effects operations
    (no events are triggered). The exclusivly handle CRUD operations, with
    some caching mecanism for optimization 
    """

    async def get_user_by_id(self, primary_key: str) -> User:
        """Retrieves the User from the redis database given its
        primary_key

        Args:
            primary_key (str): given a primary key

        Raises:
            NotFoundError: Raised if there is a cached entry
            about the non-existence of such user with the given
            primary_key
            NotFoundError: If the cache cannot prove the non-existence
            of a user an http request will be made to the users MS, thus
            if it return a 404 not found error, such non-existance is 
            cached and therefore, a redis NotFoundError is raised


        Returns:
            User: The querried user
        """
        try:
            return await User.get(primary_key)
        except:
            pass

        key_nx = f"cache-nx:{MS}:{primary_key}"
        if await redis.exists(key_nx):
            await redis.expire(key_nx, EXPIRATION)
            raise NotFoundError
        else:
            request = requests.get(
                f"http://{HOST}:{PORT}/{primary_key}"   
            )
            if request.status_code == status.HTTP_404_NOT_FOUND:
                await redis.set(key_nx, "null", ex=EXPIRATION)
                raise NotFoundError
            else:
                data = request.json()
                user = User(**data)
                await user.save()
                return user

    
    async def gat_all_users(self, offset: int = 0, limit: int = 50) -> list[User]:
        """Retrieves all users in the database and returns those within
        the range by offser and limit
        Args:
            offset (int, optional): users to skip in the array. Defaults to 0.
            limit (int, optional): max amount of users to return. Defaults to 50.

        Returns:
            list[User]: A list of all the users according to the argument's range
        """
        corr_arr = [self.get_user_by_id(key) async for key in await User.all_pks()]
        user_arr = await asyncio.gather(*corr_arr)
        return user_arr[offset:limit]

    
    async def create_user(self, user: User) -> User:
        """Given a User object, it proceeds with storing it into the redis database.
        If the user has no primary key, it will be created

        Args:
            user (User): the user to store

        Returns:
            User: the stored user
        """
        key_nx = f"cache-nx:{MS}:{user.pk}"
        await asyncio.gather(
            redis.delete(key_nx),
            user.save()
        )
        return user


    async def update_user(self, user: User) -> User:
        """Given a User object, it proceeds with storing it, overwriting the existing
        user.

        Args:
            user (User): with the new modified fileds

        Returns:
            User: the new user
        """
        await asyncio.gather(
            user.save()
        )
        return user


    async def delete_user(self, primary_key: str) -> int:
        """Given a user primary key, it deletes the user, and
        it generates a cache entry about the non-existence of it.

        Args:
            primary_key (str): primary_key of the user to delete

        Returns:
            int: The number of entried deleted on the database.
            Since primary keys are unique, it will return:
                1: if such primary keys exists and its user got deleted
                0: if such primary key does not exist, thus no deletion
                was performed
        """
        key_nx = f"cache-nx:{MS}:{primary_key}"
        deletion, nx_cache = await asyncio.gather(
            User.delete(primary_key),
            redis.set(key_nx, "null", ex=EXPIRATION)
        )
        return deletion

        