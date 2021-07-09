from dataclasses import dataclass


@dataclass
class User:
    id: int
    username: str
    first_name: str
    last_name: str
    karma: float


@dataclass
class Relation:
    from_user: User
    to_user: User
    strength: float
