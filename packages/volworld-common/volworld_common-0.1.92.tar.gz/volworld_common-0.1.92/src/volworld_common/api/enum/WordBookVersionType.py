from enum import IntEnum

class WordBookVersionType(IntEnum):
    System = 0
    Snapshot = 1
    UserSaved = 11
    UserPublished = 21
