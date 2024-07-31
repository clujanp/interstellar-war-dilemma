from .core.tester import Test as TestBase


class TestUsers(TestBase):
    read_all_users = TestBase.get_all
    read_user = TestBase.get
    create_user = TestBase.create
    update_user = TestBase.update
    delete_user = TestBase.delete
    create_many_users = TestBase.create_many


APP_BASE_URL = "http://localhost:5000/"
AUTH_BASE_URL = "http://localhost:6000/"


user_test = TestUsers('usere', 'users', APP_BASE_URL)


all = [
    user_test,
]
