from enum import IntEnum

from volsite_postgres_common.api.enum.enum import create_enum_type


class LaneDecoratorType(IntEnum):
    # ====== 1100 - 1200 Cloud ======
    Cloud_01 = 1101,
    Cloud_02 = 1102,
    Cloud_03 = 1103,
    Cloud_05 = 1105,
    Cloud_07 = 1107,
    Cloud_09 = 1109,

    # ====== 2500 - 2999 Sea Monsters ======
    BabyAspidochelone = 2500,

