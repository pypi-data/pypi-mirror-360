from typing import Final

class Ngsl:
    class Book1:
        TITLE: Final[str] = "NGSL Book 1 of 4 (New General Service List v1.01)"
        UUID: Final[str] = "b7091029-cc77-4616-990f-a21f142a5590"
        VERSION_UUID: Final[str] = "ff8fcc39-cfd8-4679-9672-9faf80bdee2f"
    class Book2:
        TITLE: Final[str] = "NGSL Book 2 of 4 (New General Service List v1.01)"
        UUID: Final[str] = "eda14e15-86f9-4f30-b77b-a307e2a9a7e4"
        VERSION_UUID: Final[str] = "06fb2ded-17b2-498e-a24e-d01635452091"
    class Book3:
        TITLE: Final[str] = "NGSL Book 3 of 4 (New General Service List v1.01)"
        UUID: Final[str] = "61a33310-a0e6-4ac2-a2f2-099a864c0dc4"
        VERSION_UUID: Final[str] = "b3f5174d-974c-4302-b717-e80683f886fc"
    class Book4:
        TITLE: Final[str] = "NGSL Book 4 of 4 (New General Service List v1.01)"
        UUID: Final[str] = "9a8601a6-caa1-484c-8111-e890634997c0"
        VERSION_UUID: Final[str] = "a595cd4d-8289-47a0-ae90-cef10142301b"

class NgslSpoken:
    TITLE: Final[str] = "NGSL-Spoken v1.2 (New General Service List-Spoken)"
    UUID: Final[str] = "5849035d-a37a-4dec-9498-677885e5d43f"
    VERSION_UUID: Final[str] = "f9d61b9f-e1fe-4fb7-b7d1-eb9dcb5ab4d5"

AllDefaultBooks = [NgslSpoken, Ngsl.Book1, Ngsl.Book2, Ngsl.Book3, Ngsl.Book4]

