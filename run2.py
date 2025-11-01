import sys
from collections import deque, defaultdict

def bfs_shortest_paths(graph, start):
    dist = {start: 0}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for nei in sorted(graph[node]):  # sort to ensure lexicographic traversal
            if nei not in dist:
                dist[nei] = dist[node] + 1
                queue.append(nei)
    return dist

def find_target_gateway(graph, virus, gateways):
    dist = bfs_shortest_paths(graph, virus)
    # pick gateways that are still connected
    reachable = [(gw, dist[gw]) for gw in gateways if gw in dist]
    if not reachable:
        return None
    min_dist = min(d for _, d in reachable)
    candidates = [gw for gw, d in reachable if d == min_dist]
    return min(candidates)

def find_next_step(graph, virus, target):
    # BFS from virus, return first step on any shortest path to target
    dist = bfs_shortest_paths(graph, virus)
    path_len = dist.get(target, None)
    if path_len is None:
        return None
    # among virus’s neighbors, pick those on shortest path
    candidates = []
    for nei in sorted(graph[virus]):
        if nei in dist and dist[nei] == 1 and bfs_shortest_paths(graph, nei).get(target, float("inf")) == path_len - 1:
            candidates.append(nei)
    if candidates:
        return min(candidates)
    # fallback: pick any reachable neighbor on path
    next_nodes = [nei for nei in graph[virus] if target in bfs_shortest_paths(graph, nei)]
    return min(next_nodes) if next_nodes else None

def solve(edges: list[tuple[str, str]]) -> list[str]:
    graph = defaultdict(set)
    for u, v in edges:
        graph[u].add(v)
        graph[v].add(u)

    gateways = {n for n in graph if n.isupper()}
    virus = "a"
    result = []

    while True:
        # If virus adjacent to any gateway, we must disconnect immediately
        adjacent = [gw for gw in sorted(graph[virus]) if gw.isupper()]
        if adjacent:
            gw = adjacent[0]
            graph[gw].remove(virus)
            graph[virus].remove(gw)
            result.append(f"{gw}-{virus}")
        else:
            # Choose target gateway
            target = find_target_gateway(graph, virus, gateways)
            if not target:
                break
            # Compute next node along shortest path
            dist = bfs_shortest_paths(graph, virus)
            # Among neighbors of virus, pick those on shortest path to target
            step_candidates = []
            for nei in sorted(graph[virus]):
                if target in bfs_shortest_paths(graph, nei) and bfs_shortest_paths(graph, nei)[target] == dist[target] - 1:
                    step_candidates.append(nei)
            next_node = step_candidates[0] if step_candidates else None

            # choose lexicographically smallest gateway-node edge available
            available_edges = sorted([f"{gw}-{node}" for gw in gateways for node in sorted(graph[gw]) if node.islower()])
            if not available_edges:
                break
            chosen = available_edges[0]
            gw, node = chosen.split("-")
            graph[gw].remove(node)
            graph[node].remove(gw)
            result.append(chosen)

        # move virus
        target = find_target_gateway(graph, virus, gateways)
        if not target:
            break
        dist = bfs_shortest_paths(graph, virus)
        if target not in dist:
            break
        # choose next node on shortest path
        next_step = None
        best_dist = dist[target]
        for nei in sorted(graph[virus]):
            d2 = bfs_shortest_paths(graph, nei).get(target, float("inf"))
            if d2 == best_dist - 1:
                next_step = nei
                break
        if next_step is None:
            break
        virus = next_step

        # stop if no paths to gateways
        if not any(gw in bfs_shortest_paths(graph, virus) for gw in gateways):
            break

    return result

def main():
    edges = []
    for line in sys.stdin:
        line = line.strip()
        if line:
            node1, sep, node2 = line.partition('-')
            if sep:
                edges.append((node1, node2))
    result = solve(edges)
    for edge in result:
        print(edge)

if __name__ == "__main__":
    main()
