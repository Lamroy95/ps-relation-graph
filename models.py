from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    id: int
    username: str
    first_name: str
    last_name: str
    size: float


@dataclass
class Relation:
    from_user: User
    to_user: User
    strength: int
