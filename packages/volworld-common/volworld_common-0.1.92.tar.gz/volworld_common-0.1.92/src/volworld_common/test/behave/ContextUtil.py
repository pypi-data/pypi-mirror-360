def int_list_str_to_int_list(int_list: str) -> list:
    int_list = int_list.replace('"', "")
    lst = int_list.split(',')
    res = list()
    for elm in lst:
        res.append(int(elm.strip()))
    return res


def list_str_to_list(int_list: str) -> list:
    int_list = int_list.replace('"', "")
    lst = int_list.split(',')
    res = list()
    for elm in lst:
        res.append(elm.strip())
    return res