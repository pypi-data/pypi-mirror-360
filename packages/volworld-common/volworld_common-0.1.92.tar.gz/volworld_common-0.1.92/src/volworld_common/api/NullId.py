from typing import Final

class NullId:
    BIGINT: Final[int] = 0
    UUID: Final[int] = "7e87861c-e9fe-47c5-b6f3-a11a7d4ecb5f"
    NAME: Final[str] = "null"

class EmptyId:
    BIGINT: Final[int] = -1
    UUID: Final[int] = "67728fba-ad15-49ed-b8c4-37971134175a"
    NAME: Final[str] = "empty"