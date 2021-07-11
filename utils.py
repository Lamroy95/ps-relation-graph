from typing import Tuple, Dict, Set
from numbers import Number

from models import User, Relation


def interp_value(
        value: Number,
        from_interval: Tuple[Number, Number],
        to_interval: Tuple[Number, Number]
    ) -> Number:
    (a1, a2), (b1, b2) = from_interval, to_interval
    return b1 + ((value - a1) * (b2 - b1) / (a2 - a1))


def recalculate_relations(relations_dict: Dict[int, Dict[int, Relation]]) ->  Set[Relation]:
    new_relations = set()
    for user_relations_dict in relations_dict.values():
        for relation in user_relations_dict.values():
            try:
                back_exchange = relations_dict[relation.to_user.id][relation.from_user.id].exchange
            except KeyError:
                back_exchange = 0

            new_relations.add(Relation(
                relation.from_user,
                relation.to_user,
                relation.exchange + back_exchange
            ))

    return new_relations


def normalize_relations(relations: Set[Relation], interval: Tuple[Number, Number], to_interval: Tuple[Number, Number]) -> Set[Relation]:
    new_rels = set()
    for rel in relations:
        new_rel = Relation(
            rel.from_user,
            rel.to_user,
            interp_value(rel.exchange, interval, to_interval)
        )
        new_rels.add(new_rel)

    return new_rels


def clean_nodes(users: Set[User], relations: Set[Relation]) -> Tuple[Set[User], Set[Relation]]:
    pass