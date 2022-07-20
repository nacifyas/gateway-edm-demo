import requests
from fastapi import status

ROOT_USERS = "http://127.0.0.1:8000/users/"

def test_get_all_users():
    """Tests the endpoint
    http://127.0.0.1:8000/users
    which return a list of users.

    Requieres that FastAPI is running
    """
    r = requests.get(ROOT_USERS)
    assert r.status_code == status.HTTP_200_OK


def test_get_non_existing_user():
    """Tests the endpoint
    http://127.0.0.1:8000/users/[non_existing_id]
    which raises a http 404 error
    Requieres that FastAPI is running
    """
    no_user_id = "no_such_user_ id!"
    r = requests.get(f"{ROOT_USERS}/{no_user_id}")
    assert r.status_code == status.HTTP_404_NOT_FOUND
