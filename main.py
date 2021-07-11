import sqlite3
from typing import List
from pyvis import network as net
from utils import interp_value
from models import User, Relation


conn = sqlite3.connect("karma.db")
cur = conn.cursor()
graph_options = """
var options = {
  "physics": {
    "barnesHut": {
      "springConstant": 0,
      "avoidOverlap": 0.9
    },
    "minVelocity": 0.75
  }
}
"""
MAX_KARMA, MIN_KARMA = cur.execute("""SELECT max(karma), min(karma)
                                      FROM user_karma
                                      JOIN users ON user_id = users.id
                                      WHERE chat_id = -1001399056118 AND users.username notnull""").fetchone()


def get_users():
    cur.execute("""SELECT uk.user_id, u.username, u.first_name, u.last_name, uk.karma
                   FROM user_karma AS uk
                   JOIN users AS u ON uk.user_id = u.id
                   WHERE uk.chat_id = -1001399056118
                   AND u.username notnull""")
    users = set()
    for row in cur.fetchall():
        *data, karma = row
        user = User(*data, interp_value(karma, (MIN_KARMA, MAX_KARMA)))
        users.add(user)

    return users


def get_user_relations(user):
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


def recalculate_relations(relations_dict):
    new_relations = set()
    max_exchange = float('-inf')
    min_exchange = float('inf')
    for user_relations_dict in relations_dict.values():
        user_back_relations = set()
        for relation in user_relations_dict.values():
            try:
                back_relation = relations_dict[relation.to_user.id][relation.from_user.id]
            except KeyError:
                back_relation = None

            new_rel = Relation(
                relation.from_user,
                relation.to_user,
                relation.exchange + back_relation.exchange if back_relation else 0
            )

            user_back_relations.add(new_rel)
            max_exchange = max(new_rel.exchange, max_exchange)
            min_exchange = min(new_rel.exchange, min_exchange)

        # if 
        new_relations.update(user_back_relations)

    return max_exchange, min_exchange, new_relations


def normalize_relations(relations, interval):
    new_rels = set()
    for rel in relations:
        new_rel = Relation(
            rel.from_user,
            rel.to_user,
            interp_value(rel.exchange, interval, (1, 20))
        )
        new_rels.add(new_rel)

    return new_rels


def clean_nodes(users, relations):
    pass


def draw_graph(nodes, edges, remove_single=False, user=None, filename="graph.html"):
    if user is not None:
        node_edges = {r for r in edges if user in r}
        print(f"Removed {len(edges) - len(node_edges)} edges")
        edges = node_edges
        filename = f"{user}.html" if isinstance(user, str) else f"{user.username}.html"

    if remove_single:
        connected_nodes = {u for u in nodes if any(u in r for r in edges)}
        print(f"Removed {len(nodes) - len(connected_nodes)} nodes")
        nodes = connected_nodes

    g = net.Network(height='100%', width='60%', heading='')
    # g.set_options(graph_options)
    g.show_buttons(filter_=['physics'])
    for node in nodes:
        g.add_node(node.id, node.username, size=node.size)

    for edge in edges:
        g.add_edge(edge.from_user.id, edge.to_user.id, width=edge.exchange)

    g.write_html(filename)


def main():
    users = get_users()
    relations_dict = dict()
    for user in users:
        user_relations = get_user_relations(user)

        if not user_relations:
            continue

        relations_dict[user.id] = user_relations

    max_exchange, min_exchange, relations = recalculate_relations(relations_dict)
    relations = normalize_relations(relations, (min_exchange, max_exchange))
    print(f"Users: {len(users)}, Relations {len(relations)}")

    draw_graph(users, relations, remove_single=True, user="lynulx")


if __name__ == '__main__':
    main()
