from requests import get, post, put, delete


class Requester:
    def __init__(self, base_url: str, path: str):
        self.base_url = base_url
        self.path = path

    def _(self, id): return f"{self.base_url}{self.path}{id or ''}"
    def get(self, id=None, **kwa): return get(self._(id), **kwa)
    def post(self, data, **kwa): return post(self._(None), json=data, **kwa)
    def put(self, id, data, **kwa): return put(self._(id), json=data, **kwa)
    def delete(self, id, **kwa): return delete(self._(id), **kwa)
