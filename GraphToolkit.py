"""
Graph algorithm toolkit — the four things "connections between points in a
network, distances and reachability" is almost certainly testing.

Pick based on what the question actually asks:

  - "Is X reachable from Y?"                      -> BFS or DFS
  - "Fewest steps / shortest path, UNWEIGHTED"    -> BFS
  - "Shortest path, WEIGHTED (non-negative)"      -> Dijkstra
  - "Are X and Y in the same group?" / many
    connectivity queries on a static graph        -> Union-Find
  - "How many separate clusters/components?"      -> DFS/BFS over all nodes,
                                                      or Union-Find
"""

from collections import deque, defaultdict
import heapq


# ---------------------------------------------------------------------
# 0. Build an adjacency list — the representation everything below uses
# ---------------------------------------------------------------------

def build_graph(edges, directed=False):
    """
    edges: list of (u, v) for unweighted, or (u, v, weight) for weighted.
    Returns dict: node -> list of neighbours (or (neighbour, weight) pairs).
    """
    graph = defaultdict(list)
    for edge in edges:
        if len(edge) == 2:
            u, v = edge
            graph[u].append(v)
            if not directed:
                graph[v].append(u)
        else:
            u, v, w = edge
            graph[u].append((v, w))
            if not directed:
                graph[v].append((u, w))
    return graph


# ---------------------------------------------------------------------
# 1. BFS — shortest path / min steps in an UNWEIGHTED graph, plus reachability
# ---------------------------------------------------------------------

def bfs_shortest_distances(graph, start):
    """Returns dict: node -> fewest edges from start. Unreached nodes absent."""
    dist = {start: 0}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for neighbour in graph[node]:
            if neighbour not in dist:
                dist[neighbour] = dist[node] + 1
                queue.append(neighbour)
    return dist


def is_reachable(graph, start, target):
    return target in bfs_shortest_distances(graph, start)

#ver2

def bfs_shortest_path(graph, start, target):
    dist = {start: 0}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        if node == target:
            return dist[node]
        for neighbour in graph[node]:
            if neighbour not in dist:
                dist[neighbour] = dist[node] + 1
                queue.append(neighbour)
    return None  # target unreachable


# ---------------------------------------------------------------------
# 2. DFS — reachability, connected components, cycle-ish exploration
# ---------------------------------------------------------------------

def dfs_visit(graph, start):
    """Returns the set of all nodes reachable from start."""
    visited = set()
    stack = [start]
    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        for neighbour in graph[node]:
            if neighbour not in visited:
                stack.append(neighbour)
    return visited


def count_connected_components(graph, all_nodes):
    """Works for undirected graphs. all_nodes = every node, including isolated ones."""
    seen = set()
    components = 0
    for node in all_nodes:
        if node not in seen:
            reached = dfs_visit(graph, node)
            seen |= reached
            components += 1
    return components


# ---------------------------------------------------------------------
# 3. Dijkstra — shortest path in a WEIGHTED graph, non-negative weights only
# ---------------------------------------------------------------------

def dijkstra(graph, start):
    """graph[node] = list of (neighbour, weight). Returns dict node -> shortest distance."""
    dist = {start: 0}
    pq = [(0, start)]  # (distance, node)
    while pq:
        d, node = heapq.heappop(pq)
        if d > dist.get(node, float("inf")):
            continue  # stale entry, skip
        for neighbour, weight in graph[node]:
            new_dist = d + weight
            if new_dist < dist.get(neighbour, float("inf")):
                dist[neighbour] = new_dist
                heapq.heappush(pq, (new_dist, neighbour))
    return dist


# ---------------------------------------------------------------------
# 4. Union-Find (Disjoint Set) — fast "same group?" queries, no live traversal needed
# ---------------------------------------------------------------------

class UnionFind:
    def __init__(self, nodes):
        self.parent = {n: n for n in nodes}
        self.rank = {n: 0 for n in nodes}

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # path compression
        return self.parent[x]

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False  # already connected
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True

    def connected(self, a, b):
        return self.find(a) == self.find(b)


# ---------------------------------------------------------------------
# Self-test — run this file directly to sanity-check all four
# ---------------------------------------------------------------------

if __name__ == "__main__":
    # Undirected, unweighted graph with a disconnected node ('f')
    edges = [("a", "b"), ("b", "c"), ("c", "d"), ("d", "a")]
    graph = build_graph(edges)
    all_nodes = ["a", "b", "c", "d", "e", "f"]  # e, f isolated

    print("BFS distances from a:", bfs_shortest_distances(graph, "a"))
    print("Is e reachable from a? (expect False):", is_reachable(graph, "a", "e"))
    print("Is c reachable from a? (expect True):", is_reachable(graph, "a", "c"))
    print("Connected components (expect 3 -> {a,b,c,d}, {e}, {f}):",
          count_connected_components(graph, all_nodes))

    # Weighted directed graph
    weighted_edges = [("a", "b", 4), ("a", "c", 1), ("c", "b", 1), ("b", "d", 1)]
    wgraph = build_graph(weighted_edges, directed=True)
    print("Dijkstra from a (expect b:2 via c, c:1, d:3):", dijkstra(wgraph, "a"))

    # Union-Find
    uf = UnionFind(["a", "b", "c", "d", "e"])
    uf.union("a", "b")
    uf.union("b", "c")
    print("connected(a, c) (expect True):", uf.connected("a", "c"))
    print("connected(a, e) (expect False):", uf.connected("a", "e"))