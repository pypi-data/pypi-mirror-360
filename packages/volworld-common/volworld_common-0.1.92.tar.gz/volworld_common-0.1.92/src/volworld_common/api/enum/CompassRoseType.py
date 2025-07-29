from enum import IntEnum

from volsite_postgres_common.api.enum.enum import create_enum_type


class CompassRoseType(IntEnum):
    EarthStar = 1001,
    Lotus = 1002,
    Plate = 1003,
    PocketWatch = 1004,
    RoundShield = 1005,
    StarShield = 1006,
    Sun = 1007,
    TwelveRays = 1008,
    VerginaSun = 1009,

    # def insert_enum(conn):
    #     create_enum_type(E.CompassRoseType, CompassRoseType, conn)
