import sqlite3
from typing import List
from pyvis import network as net
from utils import interp_value
from models import User, Relation


conn = sqlite3.connect("karma.db")
cur = conn.cursor()
MAX_KARMA, MIN_KARMA = cur.execute("""SELECT max(karma), min(karma)
                                      FROM user_karma
                                      JOIN users ON user_id = users.id
                                      WHERE chat_id = -1001399056118 AND users.username notnull""").fetchone()


def get_users() -> List[User]:
    cur.execute("""SELECT uk.user_id, u.username, u.first_name, u.last_name, uk.karma
                   FROM user_karma AS uk
                   JOIN users AS u ON uk.user_id = u.id
                   WHERE uk.chat_id = -1001399056118 AND u.username notnull""")
    users = []
    for row in cur.fetchall():
        *user_data, karma = row
        user = User(*user_data, size=interp_value(karma, (MIN_KARMA, MAX_KARMA), (1, 100)))
        users.append(user)

    return users


def get_user_relations(user: User) -> List[Relation]:
    cur.execute("""SELECT avg(abs(ke.how_match_change)), u.id, u.username, u.first_name, u.last_name, uk.karma
                   FROM karma_events AS ke
                   JOIN users      AS u  ON ke.user_to_id = u.id
                   JOIN user_karma AS uk ON ke.user_to_id = uk.user_id
                   WHERE ke.chat_id = -1001399056118
                   AND ke.user_from_id = ?
                   AND u.username notnull
                   GROUP BY u.id""", [user.id])

    user_relations = []
    for row in cur.fetchall():
        avg_change, *to_user_data, karma = row
        print(f"{karma}\t{to_user_data[1]}")
        to_user = User(*to_user_data, interp_value(karma, (MIN_KARMA, MAX_KARMA), (1, 100)))
        rel = Relation(user, to_user, avg_change)
        user_relations.append(rel)

    return user_relations


# g = net.Network(height='400px', width='50%', heading='')
# g.add_node(1)
# g.add_node(2)
# g.add_node(3)
# g.add_edge(1, 2)
# g.add_edge(2, 3)
# g.show('example.html')


def main():
    for user in get_users():
        user_relations = get_user_relations(user)
        if not user_relations:
            continue
        print(user_relations[:3])


if __name__ == '__main__':
    main()
