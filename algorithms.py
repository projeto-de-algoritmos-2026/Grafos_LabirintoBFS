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


