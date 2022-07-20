from dal.userdal import UserDAL
import pytest


@pytest.mark.asyncio
async def test_get_all_users():
    user_arr = 0
    user_arr = await UserDAL().gat_all_users()
    assert user_arr is not None
