# -*- coding: utf-8 -*-
"""
Geração do labirinto e construção do "grafo completo" (grafo 1).

O labirinto é gerado com o algoritmo clássico "recursive backtracker",
que também é, na essência, uma DFS: começa numa célula, escava um caminho
aleatório derrubando paredes, e faz backtrack quando trava num beco sem saída.

Depois de gerado, percorremos todas as células e, para cada parede que NÃO
existe entre duas células vizinhas, adicionamos uma aresta no grafo completo.
Esse grafo completo é o "mundo real" do labirinto — o personagem não o vê
por inteiro, só usa ele para saber quais movimentos são fisicamente possíveis.
"""

import random
from graph import Graph

DX = {'N': 0, 'S': 0, 'E': 1, 'W': -1}
DY = {'N': -1, 'S': 1, 'E': 0, 'W': 0}
OPPOSITE = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}


class Cell:
    __slots__ = ('walls',)

    def __init__(self):
        self.walls = {'N': True, 'S': True, 'E': True, 'W': True}


def generate_maze_grid(cols, rows, seed=None):
    """Gera a grade de células com paredes, usando DFS randomizado (recursive backtracker)."""
    rng = random.Random(seed)
    grid = [[Cell() for _ in range(cols)] for _ in range(rows)]
    visited = [[False] * cols for _ in range(rows)]

    def in_bounds(x, y):
        return 0 <= x < cols and 0 <= y < rows

    start = (0, 0)
    stack = [start]
    visited[0][0] = True

    while stack:
        x, y = stack[-1]
        dirs = ['N', 'S', 'E', 'W']
        rng.shuffle(dirs)
        moved = False
        for d in dirs:
            nx, ny = x + DX[d], y + DY[d]
            if in_bounds(nx, ny) and not visited[ny][nx]:
                grid[y][x].walls[d] = False
                grid[ny][nx].walls[OPPOSITE[d]] = False
                visited[ny][nx] = True
                stack.append((nx, ny))
                moved = True
                break
        if not moved:
            stack.pop()

    return grid


def build_graph_from_grid(grid, cols, rows):
    """Constrói o grafo completo (grafo 1) a partir da grade de células/paredes."""
    g = Graph()
    for y in range(rows):
        for x in range(cols):
            g.add_node((x, y))

    for y in range(rows):
        for x in range(cols):
            cell = grid[y][x]
            for d, has_wall in cell.walls.items():
                if not has_wall:
                    nx, ny = x + DX[d], y + DY[d]
                    g.add_edge((x, y), (nx, ny))
    return g


def generate_maze(cols, rows, seed=None):
    """Atalho: gera a grade e já devolve também o grafo completo montado a partir dela."""
    grid = generate_maze_grid(cols, rows, seed=seed)
    graph_completo = build_graph_from_grid(grid, cols, rows)
    start = (0, 0)
    goal = (cols - 1, rows - 1)
    return grid, graph_completo, start, goal
