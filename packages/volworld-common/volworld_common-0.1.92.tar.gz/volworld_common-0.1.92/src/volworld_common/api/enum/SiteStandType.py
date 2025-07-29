from enum import IntEnum

class SiteStandType(IntEnum):

    DnaTile = 11,
    FocusTile = 12,
    GravelTile = 13,
    MarbleStand = 14,
    StonePlatform = 15,
    StoneStand = 16,

    # def insert_enum(conn):
    #     create_enum_type(E.SiteStandType, SiteStandType, conn)
