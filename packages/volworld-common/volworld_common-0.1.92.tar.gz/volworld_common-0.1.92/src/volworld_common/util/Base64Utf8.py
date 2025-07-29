import base64


class Base64Utf8:
    @staticmethod
    def encode(txt: str) -> str:
        return base64.b64encode(bytes(txt, 'utf-8')).decode("utf-8")

    @staticmethod
    def decode(b64: str) -> str:
        return base64.b64decode(b64).decode('utf-8')
