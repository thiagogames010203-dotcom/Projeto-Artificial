"""Executa a comparação e exporta os trajetos e as métricas."""
import csv
from collections import defaultdict
from functools import cache
from heapq import heappop, heappush
from itertools import permutations
from math import dist
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEPOT = "2:0"


def read_csv(name):
    with (ROOT / "data" / name).open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def point(node):
    return tuple(map(int, node.split(":")))


def kmeans(nodes, k):
    """Método de Lloyd, com sementes determinísticas e afastadas."""
    points = list(map(point, nodes))
    if not 1 <= k <= len(set(points)):
        raise ValueError("k deve estar entre 1 e o número de locais distintos")
    centers = [min(points)]
    while len(centers) < k:
        centers.append(max(points, key=lambda p: min(dist(p, c) for c in centers)))
    previous = None
    for _ in range(100):
        groups = [[] for _ in centers]
        for node, p in zip(nodes, points):
            index = min(range(k), key=lambda i: dist(p, centers[i]))
            groups[index].append(node)
        if groups == previous:
            break
        previous = groups
        centers = [
            tuple(sum(axis) / len(group) for axis in zip(*map(point, group)))
            if group else center
            for group, center in zip(groups, centers)
        ]
    return groups


def make_search(streets, period):
    graph = defaultdict(list)
    for row in streets:
        graph[row["origem"]].append(
            (row["destino"], int(row[f"min_{period}"]), float(row["km"]))
        )
    lower_bound = min(cost for edges in graph.values() for _, cost, _ in edges)

    def heuristic(node, goal):
        return lower_bound * sum(abs(a - b) for a, b in zip(point(node), point(goal)))

    @cache
    def astar(start, goal, use_heuristic=True):
        estimate = heuristic if use_heuristic else lambda node, goal: 0
        queue = [(estimate(start, goal), 0, start)]
        best = {start: 0}
        parent = {}
        expanded = 0
        while queue:
            _, cost, node = heappop(queue)
            if cost != best[node]:
                continue
            expanded += 1
            if node == goal:
                path = [node]
                km = 0
                while node != start:
                    node, distance = parent[node]
                    km += distance
                    path.append(node)
                return cost, km, path[::-1], expanded
            for neighbor, minutes, km in graph[node]:
                new_cost = cost + minutes
                if new_cost < best.get(neighbor, float("inf")):
                    best[neighbor] = new_cost
                    parent[neighbor] = (node, km)
                    heappush(queue, (new_cost + estimate(neighbor, goal), new_cost, neighbor))
        raise ValueError(f"Sem caminho de {start} a {goal}")

    return astar


def route(order, search):
    stops = (DEPOT, *order, DEPOT)
    minutes = km = 0
    path = [DEPOT]
    for start, goal in zip(stops, stops[1:]):
        leg_minutes, leg_km, leg_path, _ = search(start, goal)
        minutes += leg_minutes
        km += leg_km
        path.extend(leg_path[1:])
    return minutes, km, path


def optimize(group, search):
    if len(group) > 7:
        # Vizinho mais próximo para evitar crescimento fatorial.
        remaining = list(group)
        order = []
        current = DEPOT
        while remaining:
            current = min(remaining, key=lambda node: search(current, node)[0])
            remaining.remove(current)
            order.append(current)
        return order
    return min(permutations(group), key=lambda order: route(order, search)[:2])


def write_csv(name, header, rows):
    with (ROOT / "outputs" / name).open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(rows)


def main():
    streets = read_csv("ruas.csv")
    orders = [row["no"] for row in read_csv("entregas.csv")]
    half = (len(orders) + 1) // 2
    fixed = [orders[:half], orders[half:]]
    clustered = kmeans(orders, 2)
    details, metrics, searches = [], [], []
    for period in ("normal", "pico"):
        search = make_search(streets, period)
        nodes = sorted({DEPOT, *orders})
        a_expanded = d_expanded = 0
        for start in nodes:
            for goal in nodes:
                if start == goal:
                    continue
                a, d = search(start, goal), search(start, goal, False)
                if a[0] != d[0]:
                    raise RuntimeError(f"A* e Dijkstra divergiram em {start} → {goal}")
                a_expanded += a[3]
                d_expanded += d[3]
        searches.append((period, len(nodes) * (len(nodes) - 1), a_expanded, d_expanded))
        plans = {
            "ordem_de_chegada": fixed,
            "ordem_otimizada": [optimize(group, search) for group in fixed],
            "kmeans_e_ordem_otimizada": [optimize(group, search) for group in clustered],
        }
        for scenario, groups in plans.items():
            times, distances = [], []
            for courier, order in enumerate(groups, 1):
                minutes, km, path = route(order, search)
                times.append(minutes)
                distances.append(km)
                details.append((period, scenario, courier, " > ".join(order),
                                minutes, round(km, 2), " > ".join(path)))
            metrics.append((period, scenario, sum(times), max(times), round(sum(distances), 2)))
    (ROOT / "outputs").mkdir(exist_ok=True)
    write_csv("rotas.csv", ("periodo", "cenario", "entregador", "ordem",
                            "min", "km", "trajeto"), details)
    write_csv("metricas.csv", ("periodo", "cenario", "min_total", "min_ultima_rota",
                               "km_total"), metrics)
    write_csv("buscas.csv", ("periodo", "pares", "expansoes_astar", "expansoes_dijkstra"), searches)
    for row in metrics:
        print(*row, sep=" | ")


if __name__ == "__main__":
    main()

