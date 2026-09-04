# -*- coding: utf-8 -*-
"""
Estrutura de grafo genérica, implementada como lista de adjacências.

Essa mesma classe é usada para representar:
  1) o grafo COMPLETO do labirinto (todas as células e passagens possíveis)
  2) o grafo EXPLORADO pelo personagem (só o que ele efetivamente percorreu)

Não depende de nenhuma biblioteca externa de grafos — é só um dict de listas.
"""


class Graph:
    def __init__(self):
        # node -> list[node]
        self._adj = {}

    def add_node(self, node):
        if node not in self._adj:
            self._adj[node] = []

    def add_edge(self, a, b, bidirectional=True):
        self.add_node(a)
        self.add_node(b)
        if b not in self._adj[a]:
            self._adj[a].append(b)
        if bidirectional and a not in self._adj[b]:
            self._adj[b].append(a)

    def neighbors(self, node):
        return self._adj.get(node, [])

    def nodes(self):
        return self._adj.keys()

    def edges(self):
        """Retorna lista de arestas únicas (a, b) sem duplicar (b, a)."""
        seen = set()
        result = []
        for a, neighs in self._adj.items():
            for b in neighs:
                key = frozenset((a, b))
                if key not in seen:
                    seen.add(key)
                    result.append((a, b))
        return result

    def __contains__(self, node):
        return node in self._adj

    def __len__(self):
        return len(self._adj)

    def num_edges(self):
        return len(self.edges())
