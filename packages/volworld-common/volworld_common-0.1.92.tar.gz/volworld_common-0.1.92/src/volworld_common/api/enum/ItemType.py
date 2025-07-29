from enum import IntEnum

class ItemType(IntEnum):
    Empty = 0,

    PlaceHolder = 1,

    SkyCompass = 11,
    LinkedCompass = 12,
    PuzzlePiece = 16,
    # CreatureBattle = 19,  # ==> remove
    Animal = 17,
    Beast = 18,
    Monster = 19,
    HermesStatue = 21,
    MuseStatue = 22,

    # ====== Hermestatue ======
    # ====== MuseStatue ======

    # ========= Resources > 1000 =========

    # ====== Flowers ======
    SmallDogViolet = 101,
    RedRose = 102,
    SingleRedRose = 103,
    WildGarlic = 104,
    WoodAnemoneBranch = 105,
    YellowPrimrose = 106,
    # ====== ConiferTree ======
    MountainPine = 201,
    Pine = 202,
    MacedonianPine = 203,
    GreenScotsPine = 204,
    YoungScotsPine = 205,
    # ====== BroadLeafTrees ======
    Beech = 301,
    LittleBranch = 302,
    SmallAppleTree = 303,
    YoungBeech = 304,
    # ====== Bushes ======
    CommonBoxBush = 401,
    CommonBoxSphereBush = 402,
    PrivetBush = 403,
    WildPrivetBush = 404,
    # ====== Grass ======
    CommonButterbu = 501,
    CommonCouchGrass = 502,
    SkunkCabbage = 503,
    WildGarlicGrass = 504,
    WoodMelick = 505,
    # ====== Mushrooms ======
    Champignon = 601,
    FlyAmanita = 602,
    Lactarius = 603,
    PholiotaMicrospora = 604,
    SulphurTuft = 605,
    TallFlyAmanita = 606,
    # ====== Stones ======
    DirtMossedStone = 701,
    MossedStone = 702,
    WhiteMossedStone = 703,
    WhiteSharpStone = 704,
    WhiteStone = 705,

    MidDirtStone = 721,
    # ====== Houses ======
    AdorableRedWoodenHouseWithTree = 801,
    ThatchedHut = 802,


