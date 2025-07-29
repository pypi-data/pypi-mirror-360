from enum import IntEnum

from volsite_postgres_common.api.enum.enum import create_enum_type


class LaneDestinationType(IntEnum):
    TrinityCircle = 1021,
    TrinityEdge = 1022,

    Oak = 1031,
    Shield = 1032,
    Dara = 1033,
    DaraEdge = 1034,
    DaraFour = 1035,

    # def insert_enum(conn):
    #     create_enum_type(E.LaneDestinationType, LaneDestinationType, conn)
