
class BehaveUtil:
    @staticmethod
    def clear_string(ori: str) -> str:
        return ori.replace('"', '').strip()

    @staticmethod
    def clear_int(ori: str) -> int:
        return int(BehaveUtil.clear_string(ori))

    @staticmethod
    def clear_float(ori: str) -> float:
        return float(BehaveUtil.clear_string(ori))
