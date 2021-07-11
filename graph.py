from typing import Set, Optional
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
        user: Optional[str] = None,
    ) -> Path:

    if user:
        node_edges = {r for r in edges if user in r}
        print(f"Removed {len(edges) - len(node_edges)} edges")
        edges = normalize_relations(node_edges, get_exchange_bounds(node_edges), (1, 50))

    nodes = {u for u in nodes if any(u in r for r in edges)}

    g = net.Network(width="100%", height="100%")
    g.set_options(graph_options)
    # g.show_buttons(filter_=['physics'])

    for node in nodes:
        g.add_node(node.id, node.username, size=node.size)

    for edge in edges:
        try:
            g.add_edge(edge.from_user.id, edge.to_user.id, width=edge.exchange)
        except AssertionError as e:
            print(e)

    print(f"Nodes in graph: {len(g.get_nodes())}")
    print(f"Edges in graph: {len(g.get_edges())}")

    filename = HTML_DIR / f"{token_urlsafe(16)}.html"
    g.save_graph(str(filename))
    return filename
