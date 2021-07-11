from numbers import Number
from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    id: int
    username: str
    first_name: str
    last_name: str
    size: Number

    def __hash__(self):
        return hash((self.id, self.username, self.first_name, self.last_name))

    def __eq__(self, other):
        if isinstance(other, str):
            return hash(self.username) == hash(other)
        return hash(self) == hash(other)


@dataclass(frozen=True)
class Relation:
    from_user: User
    to_user: User
    exchange: Number

    def __hash__(self):
        return hash(self.from_user) & hash(self.to_user)

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __contains__(self, item):
        return item == self.from_user or item == self.to_user
