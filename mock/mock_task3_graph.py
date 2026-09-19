"""
MOCK TASK 3 — Graph-Based Problem Solving          (suggested time: ~40 min)
=============================================================================

PROBLEM: Network Latency Analysis

You're given a set of servers and the latency (in ms) of the direct
connections between them. Connections are bidirectional (undirected) and
all weights are non-negative.

Implement TWO functions:

1. shortest_latency(edges, start, target) -> int | None
   Returns the minimum total latency to get from `start` to `target`,
   travelling along any sequence of connections. Return None if `target`
   is unreachable from `start`.

2. reachable_within(edges, start, max_latency) -> set
   Returns the set of ALL servers reachable from `start` where the total
   latency along the shortest path to that server is <= max_latency.
   `start` itself is always included (distance 0). Do NOT just return
   every reachable node — a node reachable only via a longer, indirect
   path might be reachable, but not within max_latency.

INPUT FORMAT
  edges: list of (server_a: str, server_b: str, latency: int)
  Servers are just string identifiers, e.g. "S1", "S2".

EXAMPLE

  edges = [
      ("A", "B", 4),
      ("A", "C", 1),
      ("C", "B", 1),
      ("B", "D", 5),
      ("C", "D", 8),
  ]

  shortest_latency(edges, "A", "D")       -> 7   (A -> C -> B -> D = 1+1+5)
  shortest_latency(edges, "A", "Z")       -> None (Z doesn't exist)
  reachable_within(edges, "A", 2)         -> {"A", "C", "B"}   (B's shortest path is A->C->B = 2,
                                                                  not the direct A->B edge, which is 4)

THINK ABOUT:
  - Which single algorithm answers BOTH questions, just used two different ways?
  - `shortest_latency` needs an exact target's distance; `reachable_within`
    needs to filter or early-stop a full distance computation by a threshold.
  - What if `start` isn't in the graph at all?
  - What if `edges` contains a duplicate edge between the same pair with a
    different weight — which one should count?
"""
import heapq

def build_adj_dict(edges):
    adj_dict = {}
    for a,b, weight in edges:
        if a not in adj_dict:
            adj_dict[a] = [(b,weight)]
        else:
            adj_dict[a].append((b,weight))
        if b not in adj_dict:
            adj_dict[b] = [(a,weight)]
        else:
            adj_dict[b].append((a,weight))
    return adj_dict

def dijkstra(graph, start):
    dist = {start:0}
    queue = [(start,0)]
    while queue:
        node,d = heapq.heappop(queue)
        for neighbor, weight in graph[node]:
            new_dist = d + weight
            if new_dist < dist.get(neighbor,float("inf")):
                dist[neighbor] = new_dist
                heapq.heappush(queue,(neighbor, new_dist))
    return dist


def shortest_latency(edges, start, target):
    # TODO: implement
    adj_dict = build_adj_dict(edges)
    if start not in adj_dict:
            return None
    latency_list = dijkstra(adj_dict,start)
    return latency_list[target] if target in latency_list else None


def reachable_within(edges, start, max_latency):
    # TODO: implement
    adj_dict = build_adj_dict(edges)
    latency_list = dijkstra(adj_dict,start)
    reachable = set()
    for node in latency_list:
        if latency_list[node] <= max_latency:
            reachable.add(node)
    return reachable if reachable else None


# ---------------------------------------------------------------------
# Self-check harness
# ---------------------------------------------------------------------

def _run():
    results = []

    def check(name, fn, args, expected):
        try:
            got = fn(*args)
            ok = (got == expected)
            results.append((name, "PASS" if ok else f"FAIL (got {got!r}, expected {expected!r})"))
        except NotImplementedError:
            results.append((name, "NOT IMPLEMENTED"))
        except Exception as e:
            results.append((name, f"ERROR: {e}"))

    edges = [
        ("A", "B", 4),
        ("A", "C", 1),
        ("C", "B", 1),
        ("B", "D", 5),
        ("C", "D", 8),
    ]

    check("shortest_A_to_D", shortest_latency, (edges, "A", "D"), 7)
    check("shortest_A_to_A", shortest_latency, (edges, "A", "A"), 0)
    check("shortest_A_to_unknown_node", shortest_latency, (edges, "A", "Z"), None)
    check("shortest_from_unknown_start", shortest_latency, (edges, "Z", "A"), None)

    check("reachable_within_0", reachable_within, (edges, "A", 0), {"A"})
    check("reachable_within_1", reachable_within, (edges, "A", 1), {"A", "C"})
    check("reachable_within_2", reachable_within, (edges, "A", 2), {"A", "C", "B"})
    check("reachable_within_6", reachable_within, (edges, "A", 6), {"A", "C", "B"})
    check("reachable_within_7", reachable_within, (edges, "A", 7), {"A", "C", "B", "D"})

    # Disconnected component
    edges_disconnected = edges + [("X", "Y", 1)]
    check("disconnected_component_shortest", shortest_latency, (edges_disconnected, "A", "X"), None)
    check("disconnected_component_reachable", reachable_within, (edges_disconnected, "A", 100), {"A", "B", "C", "D"})

    # Zero-weight edge
    edges_zero = [("P", "Q", 0), ("Q", "R", 5)]
    check("zero_weight_edge", shortest_latency, (edges_zero, "P", "R"), 5)
    check("zero_weight_reachable_within_0", reachable_within, (edges_zero, "P", 0), {"P", "Q"})

    for name, result in results:
        print(f"{name:40} {result}")


if __name__ == "__main__":
    _run()
