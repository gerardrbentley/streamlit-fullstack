from dataclasses import dataclass
@dataclass
class BaseNote:
    """Note Entity for Creation / Handling without database ID"""

    created_timestamp: int
    updated_timestamp: int
    username: str
    body: str


@dataclass
class Note(BaseNote):
    """Note Entity to model database entry"""

    rowid: int
