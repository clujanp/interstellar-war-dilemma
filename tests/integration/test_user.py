from . import user_test
from uuid import uuid4
from typing import List


def test_cases_user(auth_data: dict, roles: List[dict]) -> List[dict]:
    created_user = user_test.create_user(
        auth=auth_data,
        username=f"user_{str(uuid4()):.6}",
        email=f"email_{str(uuid4()):.6}@mail.com",
        first_name="Pepe",
        last_name="Guapo",
        roles=[roles[0]['uid'], roles[1]['uid']],
    )
    # TODO: validate the created user
    user = user_test.read_user(auth=auth_data, uid=created_user['uid'])
    # TODO: validate the readed user
    # TODO: compare readed user with the created
    users = user_test.read_all_users(auth=auth_data)
    # TODO: validate all readed users
    # TODO: search created user in the list of users

    updated_user = user_test.update_user(
        auth=auth_data,
        uid=user['uid'],
        roles=[roles[2]['uid'], roles[4]['uid']],
    )
    # TODO: validate the updated user
    # TODO: compare updated user with the created
    user = user_test.read_user(auth=auth_data, uid=updated_user['uid'])
    # TODO: validate the readed user
    # TODO: compare readed user with the updated
    users = user_test.read_all_users(auth=auth_data)
    # TODO: validate all readed users
    # TODO: search updated user in the list of users

    delete_user = user_test.delete(
        auth=auth_data,
        uid=user['uid'],
    )
    # TODO: validate the delete user
    # TODO: compare delete user with the updated

    created_users = user_test.create_many_users(
        auth=auth_data,
        data=[{
            'username': f"user_{str(uuid4()):.6}",
            'email': f"email_{str(uuid4()):.6}@mail.com",
            'first_name': "masivo",
            'last_name': "sin ley",
            'roles': [roles[-2]['uid'], roles[-1]['uid']],
        } for _ in range(10)]
    )
    # TODO: validate the created users
    users = user_test.read_all_users(auth=auth_data)
    # TODO: validate all readed users
    # TODO: search created users in the list of users

    print(user_test.get_summary())
    return users
