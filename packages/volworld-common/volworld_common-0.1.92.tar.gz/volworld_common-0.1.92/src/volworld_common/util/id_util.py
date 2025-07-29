from typing import Final
from random import randrange, randint
import uuid

ID_PREFIX: Final = 'i'

Min_DB_Id_Series: Final = 1000000
MIN_TEST_Id_Series: Final = 10000
MAX_TEST_Id_Series: Final = 50000


def rand_test_id() -> str:
    return f'{ID_PREFIX}{randint(MIN_TEST_Id_Series, MAX_TEST_Id_Series)}'


def rand_uuid() -> str:
    return str(uuid.uuid4())


def rand_subfix() -> str:
    return f"{randrange(MIN_TEST_Id_Series, MAX_TEST_Id_Series)}"


def new_rand_test_user_name():
    return f"testuseri{randrange(MIN_TEST_Id_Series, MAX_TEST_Id_Series)}"


def int_2_iid(id: int) -> str:
    return f"{ID_PREFIX}{id}"

def iid_2_int(iid: str) -> int:
    return int(iid[1:])


def iid_list_2_int_list(iids: list) -> list:
    res = list()
    for i in iids:
        res.append(iid_2_int(i))
    return res


def int_list_2_iid_list(ids: list) -> list:
    res = list()
    for i in ids:
        res.append(int_2_iid(i))
    return res