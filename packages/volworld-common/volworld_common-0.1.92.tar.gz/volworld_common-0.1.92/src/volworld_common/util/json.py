
import json


def convert_json_by_attributes(j, attList) -> str:
    abb_att = {}

    for a in attList:
        for name in a.__dict__:
            abb = a.__dict__[name]
            abb_att[f"\"{abb}\":"] = f"\"{abb}__{name}\":"

    res = json.dumps(j, indent=4, sort_keys=True)
    for att in abb_att.keys():
        res = res.replace(att, abb_att[att])

    return res


def print_json_by_attributes(j, attList, print_long_att: bool = False):
    if not print_long_att:
        print(json.dumps(j, indent=4, sort_keys=True))
        return

    print(convert_json_by_attributes(j, attList))