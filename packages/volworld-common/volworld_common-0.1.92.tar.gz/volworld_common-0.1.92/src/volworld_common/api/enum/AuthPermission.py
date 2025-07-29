from aenum import IntEnum


class AuthPermission(IntEnum):

    User = 0
    Tester = 64
    Administrator = 128
    Root = 255

    
