from enum import IntEnum

from volsite_postgres_common.api.enum.enum import create_enum_type


class SiteMarkType(IntEnum):
    Location = 1001,
    Focus = 1002,
    FlagFlying = 1003,
    Flag = 1004,
    Water = 1005,
    Cloud = 1006,

    Island = 1011,

    Mountain = 1021,
    Grass = 1022,
    Ice = 1023,
    Forest = 1024,
    Conifertree = 1025,

    Fort = 1051,
    Cottage = 1052,
    Castle = 1053,

    Monster = 1091,
    Animal = 1092,

    # def insert_enum(conn):
    #     create_enum_type(E.LaneSiteMarkType, LaneSiteMarkType, conn)
