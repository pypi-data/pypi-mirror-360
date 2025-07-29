from volworld_common.api.CA import CA

names = [attr for attr in vars(CA) if not attr.startswith("__")]
names.sort()
values = []

att = "Attributes = {"
init = "A"
for name in names:
    curr_init = name[0]
    if curr_init != init:
        att += "\n"
        init = curr_init
    value = getattr(CA, name)
    assert value not in values, f"{value} is already in values"
    att += f"\n\"{name}\": \"{value}\","

att += "\n\"___Error___\": \"err\""
att += "\n}"

print(f"\n\n\n{att}\n\n\n")