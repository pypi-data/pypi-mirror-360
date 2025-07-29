
from uuid import UUID

def assert_json(check: dict, expt: dict):
    for e_key in expt:
        assert e_key in check, f"Key[{e_key}] is not exists. expect =>  \n{expt}\ncheck => \n{check}"
        expt_elm = expt[e_key]
        if isinstance(expt_elm, dict):
            assert_json(check[e_key], expt_elm)
        else:
            assert check[e_key] == expt_elm, f"\nkey = [{e_key}]\nexpect =>  \n{expt_elm}\ncheck => \n{check[e_key]}" \
                                             f"\n------\nexpect_json =>  \n{expt}\ncheck_json => \n{check}"


# ref https://stackoverflow.com/questions/53847404/how-to-check-uuid-validity-in-python

def is_uuid(uuid_to_test, version=4):
    try:
        uuid_obj = UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_to_test


def is_db_id(did: str) -> bool:
    if did is None:
        return False
    if len(did) == 0:
        return False
    if did[0] != 'i':
        return False
    try:
        n = int(did[1:])
        return True
    except ValueError:
        return False
