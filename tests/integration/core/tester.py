from . import TestBank
from .requester import Requester
from typing import List, Dict
import logging


class Test(TestBank):
    TITLE = {
        'post': 'post {1}',
        'all': 'get all {1}',
        'add': 'add new {0}',
        'get': 'get {0} with uid {2:.3}',
        'update': 'update {0} with uid {2:.3}',
        'delete': 'delete {0} with uid {2:.3}',
        'add_many': 'add new {1}',
        'fail_auth': 'fail auth {0}',
    }
    SHOW_DETAILS = True
    SHOW_TRACBACK = False
    LOGGING_LEVEL = logging.WARNING

    test_counter = {'ok': 0, 'fail': 0}

    def __init__(
        self, entity: str, plural: str, base_url: str, path: str = None
    ):
        path = path or f"{plural}/"
        self.requester = Requester(base_url, path)
        self.r_get, self.r_post, self.r_put, self.r_delete = [
            getattr(self.requester, _)
            for _ in ('get', 'post', 'put', 'delete',)
        ]
        self.entity = (entity, plural,)
        super().__init__()

    # auth start
    def simple_post(self, status_code: int = 201, **data: dict) -> dict:
        return self.test_bank(
            self.TITLE['post'].format(*self.entity),
            self.r_post, status_code, data
        )

    def build_auth(self, authorizer: dict) -> Dict[str, str]:
        assert isinstance(authorizer, dict) and (
            ('email' in authorizer and 'password' in authorizer)
            or 'AccessToken' in authorizer
        )
        if 'email' in authorizer:
            authorizer = self.auth(**authorizer)
        return {'Authorization': f"Bearer {authorizer['AccessToken']}"}

    def auth(self, email: str, password: str) -> Dict[str, str]:
        return self.r_post(data={'email': email, 'password': password})

    def headers(self, auth: dict) -> Dict[str, str]:
        return {'headers': self.build_auth(auth)}
    # auth end

    def get_all(self, auth: dict, status_code: int = 200) -> List[dict]:
        return self.test_bank(
            self.TITLE['all'].format(*self.entity),
            self.r_get, status_code, **self.headers(auth)
        )

    def create_many(
        self, data: List[dict], auth: dict, status_code: int = 201
    ) -> dict:
        return self.test_bank(
            self.TITLE['add_many'].format(*self.entity),
            self.r_post, status_code, data, **self.headers(auth)
        )

    # CRUD start
    def get(self, uid: str, auth: dict, status_code: int = 200) -> dict:
        return self.test_bank(
            self.TITLE['get'].format(*self.entity, str(uid)),
            self.r_get, status_code, uid, **self.headers(auth)
        )

    def create(self, auth: dict, status_code: int = 201, **data: dict) -> dict:
        return self.test_bank(
            self.TITLE['add'].format(*self.entity),
            self.r_post, status_code, data, **self.headers(auth)
        )

    def update(
        self, uid: str, auth: dict, status_code: int = 200, **data: dict
    ) -> dict:
        return self.test_bank(
            self.TITLE['update'].format(*self.entity, str(uid)),
            self.r_put, status_code, uid, data, **self.headers(auth)
        )

    def delete(self, uid: str, auth: dict, status_code: int = 200) -> dict:
        return self.test_bank(
            self.TITLE['delete'].format(*self.entity, str(uid)),
            self.r_delete, status_code, uid, **self.headers(auth)
        )
    # CRUD end

    # FAIL start
    def fail_auth_get(
        self, uid: str, status_code: int = 401
    ) -> dict:
        return self.test_bank(
            self.TITLE['fail_auth'].format(*self.entity, str(uid)),
            self.r_get, status_code, uid
        )

    def fail_auth_create(
        self, status_code: int = 401, **data: dict
    ) -> dict:
        return self.test_bank(
            self.TITLE['fail_auth'].format(*self.entity),
            self.r_post, status_code, data
        )
    # FAIL end
