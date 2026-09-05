# -*- coding: utf-8 -*-
import random
from collections import deque


def dfs_explore(graph, start, goal):

    visited = {start}
    stack = [start]
    neighbor_order = {}  # cache da ordem embaralhada de vizinhos por nó

    yield {'type': 'move', 'from': None, 'to': start, 'action': 'start', 'stack': list(stack)}

    if start == goal:
        yield {'type': 'goal_reached', 'node': start}
        return

    while stack:
        current = stack[-1]

        if current not in neighbor_order:
            nbrs = list(graph.neighbors(current))
            random.shuffle(nbrs)
            neighbor_order[current] = nbrs

        next_node = None
        while neighbor_order[current]:
            candidate = neighbor_order[current].pop()
            if candidate not in visited:
                next_node = candidate
                break

        if next_node is not None:
            visited.add(next_node)
            stack.append(next_node)
            yield {
                'type': 'move', 'from': current, 'to': next_node,
                'action': 'advance', 'stack': list(stack),
            }
            if next_node == goal:
                yield {'type': 'goal_reached', 'node': next_node}
                return
        else:
            # Beco sem saída: faz backtrack removendo o topo da pilha.
            stack.pop()
            if stack:
                yield {
                    'type': 'move', 'from': current, 'to': stack[-1],
                    'action': 'backtrack', 'stack': list(stack),
                }

    yield {'type': 'exhausted'}


def bfs_shortest_path(graph, start, goal):
    """Percorre *graph* em largura e devolve eventos até achar o menor caminho.

    O algoritmo mantém um pai para cada vértice descoberto. Assim que o
    objetivo é encontrado, a cadeia de pais é reconstruída e emitida no
    evento ``path_found``. Os eventos intermediários carregam a fila e os
    vértices visitados para que a interface possa animar a busca.
    """
    visited = {start}
    parent = {start: None}
    queue = deque([start])

    yield {
        'type': 'visit',
        'node': start,
        'from': None,
        'queue': list(queue),
        'visited': set(visited),
    }

    if start == goal:
        yield {'type': 'path_found', 'path': [start], 'visited': set(visited)}
        return

    while queue:
        current = queue.popleft()

        for neighbor in graph.neighbors(current):
            if neighbor in visited:
                continue

            visited.add(neighbor)
            parent[neighbor] = current
            queue.append(neighbor)
            yield {
                'type': 'visit',
                'node': neighbor,
                'from': current,
                'queue': list(queue),
                'visited': set(visited),
            }

            if neighbor == goal:
                path = []
                node = goal
                while node is not None:
                    path.append(node)
                    node = parent[node]
                path.reverse()
                yield {
                    'type': 'path_found',
                    'path': path,
                    'visited': set(visited),
                }
                return

    yield {'type': 'exhausted', 'visited': set(visited)}

