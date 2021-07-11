from typing import Set, Union
from pathlib import Path
from secrets import token_urlsafe

from pyvis import network as net

from models import User, Relation
from services import get_exchange_bounds
from utils import normalize_relations
from data import users, relations
from config import HTML_DIR


graph_options = """
var options = {
  "autoResize": true,
  "edges": {
    "color": {
      "color": "#848484",
      "highlight": "#FF0000"
    }
  },
"physics": {
    "barnesHut": {
      "springConstant": 0,
      "damping": 0.5,
      "avoidOverlap": 0.75
    },
    "maxVelocity": 10,
    "minVelocity": 0.75
  }
}
"""


def html_graph(
        nodes: Set[User] = users.copy(),
        edges: Set[Relation] = relations.copy(),
        user: Union[str, User, None] = None,
    ) -> Path:

    if user is not None:
        user_edges = {r for r in edges if user in r}
        print(f"[User filter] Removed {len(edges) - len(user_edges)} edges")
        edges = user_edges

    connected_nodes = {u for u in nodes if any(u in r for r in edges)}
    print(f"Removed {len(nodes) - len(connected_nodes)} nodes")
    nodes = connected_nodes

    edges = normalize_relations(edges, get_exchange_bounds(edges), (1, 30))

    g = net.Network(width="100%", height="100%")
    g.set_options(graph_options)
    # g.show_buttons(filter_=['physics'])

    for node in nodes:
        g.add_node(node.id, node.username, size=node.size)

    for edge in edges:
        try:
            g.add_edge(edge.from_user.id, edge.to_user.id, width=edge.exchange)
        except AssertionError as e:
            print(f"{e}")

    print(f"Nodes in graph: {len(nodes)}")
    print(f"Edges in graph: {len(edges)}")

    filename = HTML_DIR / f"{token_urlsafe(16)}.html"
    g.save_graph(str(filename))
    return filename
