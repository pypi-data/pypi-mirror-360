from typing import Final

class NullUser:
    BIGINT: Final[int] = 0
    UUID: Final[str] = 'ae5b3e33-8176-45f0-bf91-5ddaef367637'
    NAME: Final = 'null'

class SystemUser:
    BIGINT: Final[int] = 1
    UUID: Final[str] = '35be7c40-5a98-457c-bccb-d2dbd8da1cb8'
    NAME: Final = 'sys'

class RootUser:
    BIGINT: Final[int] = 9
    UUID: Final[str] = '26101fe2-f8e8-4ab9-8524-d3caaa01bac0'
    NAME: Final = 'root'

class Hermes:
    BIGINT: Final[int] = 16
    UUID: Final[str] = '075c6600-13c2-4444-9da3-199c2e75300f'
    NAME: Final = 'hermes'

class Athena:
    BIGINT: Final[int] = 17
    UUID: Final[str] = 'de9f22f8-a908-40f0-a43e-2404c159ea34'
    NAME: Final = 'athena'

class Gaia:
    BIGINT: Final[int] = 18
    UUID: Final[str] = 'b9ce741d-02c6-4317-aa52-0b67cac561df'
    NAME: Final = 'gaia'

class Urania:
    BIGINT: Final[int] = 21
    UUID: Final[str] = '91b34a69-cb6e-4ef3-a46f-e96ea5cebf3f'
    NAME: Final = 'urania'

class Calliope:
    BIGINT: Final[int] = 22
    UUID: Final[str] = 'fa2c68e4-393d-4d04-aab9-d53f1a362032'
    NAME: Final = 'calliope'

class Melpomene:
    BIGINT: Final[int] = 23
    UUID: Final[str] = '000e4d34-34e9-49e1-b06e-169408d6dae6'
    NAME: Final = 'melpomene'

class Thalia:
    BIGINT: Final[int] = 24
    UUID: Final[str] = '72cffac1-8869-499d-bb18-16b91a595aa2'
    NAME: Final = 'thalia'

class Mnemosyne:
    BIGINT: Final[int] = 31
    UUID: Final[str] = '2566f3df-8151-47a2-a2fd-a23845eabbb9'
    NAME: Final = 'mnemosyne'

class Metis:
    BIGINT: Final[int] = 32
    UUID: Final[str] = '9ca7ecaf-543e-4a3a-b01b-7f4a39780373'
    NAME: Final = 'metis'


AllAuthUsers = [NullUser, SystemUser, RootUser, Hermes, Athena, Gaia, Urania, Calliope, Melpomene, Thalia, Mnemosyne, Metis]

GreekDeities = [Hermes, Athena, Gaia, Urania, Calliope, Melpomene, Thalia, Mnemosyne, Metis]

