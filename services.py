from typing import Tuple, Set, Dict
import sqlite3

from models import User, Relation
from utils import interp_value, recalculate_relations


conn = sqlite3.connect("karma.db")
cur = conn.cursor()


def get_karma_bounds() -> Tuple[float, float]:
    return cur.execute("""
        SELECT min(karma), max(karma)
        FROM user_karma
        JOIN users ON user_id = users.id
        WHERE chat_id = -1001399056118 AND users.username notnull
    """).fetchone()


def get_exchange_bounds(relations: Set[Relation]) -> Tuple[float, float]:
    key = lambda x: x.exchange
    return min(relations, key=key).exchange, max(relations, key=key).exchange


def get_users() -> Set[User]:
    cur.execute("""SELECT uk.user_id, u.username, u.first_name, u.last_name, uk.karma
                   FROM user_karma AS uk
                   JOIN users AS u ON uk.user_id = u.id
                   WHERE uk.chat_id = -1001399056118
                   AND u.username notnull""")
    users = set()
    for row in cur.fetchall():
        *data, karma = row
        user = User(*data, interp_value(karma, get_karma_bounds(), (10, 100)))
        users.add(user)

    print(f"Total users: {len(users)}")
    return users


def get_users_relations(users: Set[User]) -> Set[Relation]:
    relations_dict = dict()
    for user in users:
        user_relations = get_user_relations(user)

        if not user_relations:
            continue

        relations_dict[user.id] = user_relations

    return recalculate_relations(relations_dict)


def get_user_relations(user: User) -> Dict[int, Relation]:
    cur.execute("""SELECT sum(ke.how_match_change), u.id, u.username, u.first_name, u.last_name, uk.karma
                   FROM karma_events AS ke
                   JOIN users AS u  ON ke.user_to_id = u.id
                   JOIN user_karma AS uk ON ke.user_to_id = uk.user_id
                   WHERE ke.chat_id = -1001399056118
                   AND uk.chat_id = -1001399056118
                   AND ke.user_from_id = ?
                   AND u.username notnull
                   GROUP BY uk.user_id""", [user.id])

    user_relations = dict()
    for row in cur.fetchall():
        total_change, *to_user_data = row
        to_user = User(*to_user_data)
        rel = Relation(user, to_user, total_change)
        user_relations[to_user.id] = rel

    return user_relations
