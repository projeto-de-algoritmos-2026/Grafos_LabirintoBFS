# -*- coding: utf-8 -*-
import random
from collections import deque


def dfs_explore(graph, start, goal, seed=None):
    """Explora o grafo com DFS, usando uma ordem reproduzível quando pedida."""

    visited = {start}
    stack = [start]
    neighbor_order = {}  # cache da ordem embaralhada de vizinhos por nó
    rng = random if seed is None else random.Random(seed)

    yield {'type': 'move', 'from': None, 'to': start, 'action': 'start', 'stack': list(stack)}

    if start == goal:
        yield {'type': 'goal_reached', 'node': start}
        return

    while stack:
        current = stack[-1]

        if current not in neighbor_order:
            nbrs = list(graph.neighbors(current))
            rng.shuffle(nbrs)
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
    """Retorna o menor caminho entre ``start`` e ``goal``.

    A busca usa uma fila FIFO e um mapa de predecessores. O retorno é uma
    lista na ordem origem -> destino. Quando a origem e o destino são iguais,
    retorna ``[start]``; quando o destino é inalcançável, retorna ``None``.
    """
    if start == goal:
        return [start]

    visited = {start}
    predecessors = {start: None}
    queue = deque([start])

    while queue:
        current = queue.popleft()

        for neighbor in graph.neighbors(current):
            if neighbor in visited:
                continue

            visited.add(neighbor)
            predecessors[neighbor] = current
            queue.append(neighbor)

            if neighbor == goal:
                path = []
                node = goal
                while node is not None:
                    path.append(node)
                    node = predecessors[node]
                path.reverse()
                return path

    return None


def bfs_explore(graph, start, goal):
    """Percorre *graph* em largura e devolve eventos para a animação.

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


def bidirectional_bfs_shortest_path(graph, start, goal):
    """Versão "pura" (sem eventos) do BFS bidirecional, útil para testes.

    Expande alternadamente uma camada da fila que sai de ``start`` e uma
    camada da fila que sai de ``goal``, até uma delas alcançar um nó que a
    outra já visitou. Como as duas frentes crescem em largura, o primeiro
    encontro garante o caminho mais curto — só muda quantos nós, no total,
    precisam ser visitados até isso acontecer (normalmente bem menos que um
    BFS de mão única, já que cada frente cobre menos território).
    """
    if start == goal:
        return [start]

    visited_a = {start}
    visited_b = {goal}
    parent_a = {start: None}
    parent_b = {goal: None}
    queue_a = deque([start])
    queue_b = deque([goal])

    def build_path(meeting):
        left = []
        node = meeting
        while node is not None:
            left.append(node)
            node = parent_a[node]
        left.reverse()

        right = []
        node = parent_b[meeting]
        while node is not None:
            right.append(node)
            node = parent_b[node]

        return left + right

    while queue_a and queue_b:
        for _ in range(len(queue_a)):
            current = queue_a.popleft()
            for neighbor in graph.neighbors(current):
                if neighbor in visited_a:
                    continue
                visited_a.add(neighbor)
                parent_a[neighbor] = current
                queue_a.append(neighbor)
                if neighbor in visited_b:
                    return build_path(neighbor)

        for _ in range(len(queue_b)):
            current = queue_b.popleft()
            for neighbor in graph.neighbors(current):
                if neighbor in visited_b:
                    continue
                visited_b.add(neighbor)
                parent_b[neighbor] = current
                queue_b.append(neighbor)
                if neighbor in visited_a:
                    return build_path(neighbor)

    return None


def bidirectional_bfs_explore(graph, start, goal):
    """Percorre *graph* com BFS bidirecional e devolve eventos para animação.

    Mantém duas buscas em largura simultâneas: uma frente ``'a'`` saindo de
    ``start`` e uma frente ``'b'`` saindo de ``goal``. As duas frentes
    avançam uma camada por vez, alternando; assim que uma frente alcança um
    nó que a outra já visitou ("encontro"), o caminho é reconstruído
    juntando a cadeia de pais de cada lado.

    Eventos emitidos:
      {'type': 'visit', 'side': 'a'|'b', 'node':.., 'from':..,
       'queue_a':[...], 'queue_b':[...],
       'visited_a': set, 'visited_b': set}
      {'type': 'path_found', 'path': [start,...,goal], 'meeting_node':..,
       'visited_a': set, 'visited_b': set}
      {'type': 'exhausted', 'visited_a': set, 'visited_b': set}

    O caminho devolvido em ``path_found`` já vem na ordem start -> goal,
    igual ao formato de ``bfs_explore``, então o restante do app (animação
    de ida/volta) não precisa saber qual algoritmo foi usado.
    """
    visited_a = {start}
    visited_b = {goal}
    parent_a = {start: None}
    parent_b = {goal: None}
    queue_a = deque([start])
    queue_b = deque([goal])

    def snapshot(side, node, frm):
        return {
            'type': 'visit',
            'side': side,
            'node': node,
            'from': frm,
            'queue_a': list(queue_a),
            'queue_b': list(queue_b),
            'visited_a': set(visited_a),
            'visited_b': set(visited_b),
        }

    def build_path(meeting):
        left = []
        node = meeting
        while node is not None:
            left.append(node)
            node = parent_a[node]
        left.reverse()

        right = []
        node = parent_b[meeting]
        while node is not None:
            right.append(node)
            node = parent_b[node]

        return left + right

    yield snapshot('a', start, None)
    yield snapshot('b', goal, None)

    if start == goal:
        yield {
            'type': 'path_found', 'path': [start], 'meeting_node': start,
            'visited_a': set(visited_a), 'visited_b': set(visited_b),
        }
        return

    while queue_a and queue_b:
        for _ in range(len(queue_a)):
            current = queue_a.popleft()
            for neighbor in graph.neighbors(current):
                if neighbor in visited_a:
                    continue
                visited_a.add(neighbor)
                parent_a[neighbor] = current
                queue_a.append(neighbor)
                yield snapshot('a', neighbor, current)

                if neighbor in visited_b:
                    path = build_path(neighbor)
                    yield {
                        'type': 'path_found', 'path': path, 'meeting_node': neighbor,
                        'visited_a': set(visited_a), 'visited_b': set(visited_b),
                    }
                    return

        for _ in range(len(queue_b)):
            current = queue_b.popleft()
            for neighbor in graph.neighbors(current):
                if neighbor in visited_b:
                    continue
                visited_b.add(neighbor)
                parent_b[neighbor] = current
                queue_b.append(neighbor)
                yield snapshot('b', neighbor, current)

                if neighbor in visited_a:
                    path = build_path(neighbor)
                    yield {
                        'type': 'path_found', 'path': path, 'meeting_node': neighbor,
                        'visited_a': set(visited_a), 'visited_b': set(visited_b),
                    }
                    return

    yield {'type': 'exhausted', 'visited_a': set(visited_a), 'visited_b': set(visited_b)}