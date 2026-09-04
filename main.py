# -*- coding: utf-8 -*-
"""
Ponto de entrada. Contém a máquina de estados que orquestra a simulação.

ESTADO ATUAL DO PROJETO (commit atual): só a exploração por DFS está ativa.
O personagem anda pelo grafo completo (grafo 1) usando DFS, construindo o
grafo explorado (grafo 2) em tempo real, e para assim que acha a saída.

A parte de BFS (calcular o menor caminho de volta ao início, e depois ir de
novo até a saída) já está implementada em `algorithms.py`, mas aqui no
main.py ela está toda comentada, marcada com blocos "=== BFS (desativado por
enquanto) ===" — é só descomentar essas partes num commit futuro para
reativar o fluxo completo (DFS -> BFS volta -> BFS vai pra saída).

Rode com:  python main.py
"""

import sys
import pygame

import config as cfg
from maze import generate_maze
from graph import Graph
from algorithms import dfs_explore
# === BFS (desativado por enquanto) ===
# from algorithms import bfs_shortest_path
# === fim BFS ===


class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("DFS explorando o labirinto (grafo)")
        self.screen = pygame.display.set_mode((cfg.WINDOW_WIDTH, cfg.WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()

        from visualizer import Visualizer
        self.viz = Visualizer(self.screen)

        self.speed = cfg.DEFAULT_STEPS_PER_SEC
        self.paused = False
        self.running = True

        self.new_maze()

    # ------------------------------------------------------------------ #
    # (Re)inicialização de uma rodada
    # ------------------------------------------------------------------ #
    def new_maze(self, seed=None):
        self.grid, self.graph_completo, self.start, self.goal = generate_maze(
            cfg.COLS, cfg.ROWS, seed=seed
        )

        # Grafo 2: começa vazio, só com o nó inicial. É preenchido conforme
        # o DFS avança (cada 'advance' vira uma aresta nova aqui).
        self.graph_explorado = Graph()
        self.graph_explorado.add_node(self.start)

        self.dfs_gen = dfs_explore(self.graph_completo, self.start, self.goal)

        # === BFS (desativado por enquanto) ===
        # self.bfs_gen = None
        # self.path = None
        # self.path_index = 0
        # === fim BFS ===

        self.character_pos = self.start
        self.visited_cells = {self.start}
        self.frontier_cells = set()
        self.dfs_steps = 0
        self._last_stack = [self.start]
        self.phase = 'DFS_EXPLORANDO'
        self.time_accumulator = 0.0
        self.done_message = ""

    # ------------------------------------------------------------------ #
    # Avanço de um "passo lógico" do algoritmo ativo
    # ------------------------------------------------------------------ #
    def step_dfs(self):
        try:
            event = next(self.dfs_gen)
        except StopIteration:
            self.phase = 'CONCLUIDO'
            self.done_message = "DFS terminou sem achar a saída (não deveria acontecer aqui)."
            return

        if event['type'] == 'move':
            to_node = event['to']
            from_node = event['from']
            self.character_pos = to_node
            self.visited_cells.add(to_node)
            self.dfs_steps += 1
            if 'stack' in event:
                self._last_stack = event['stack']
            if event['action'] == 'advance' and from_node is not None:
                # Cada avanço do DFS vira uma aresta nova no grafo explorado.
                self.graph_explorado.add_edge(from_node, to_node)
        elif event['type'] == 'goal_reached':
            self.character_pos = event['node']
            self.dfs_finished()
        elif event['type'] == 'exhausted':
            self.phase = 'CONCLUIDO'
            self.done_message = "O DFS explorou tudo e não achou a saída."

    def dfs_finished(self):
        """
        Chamado assim que o DFS chega na saída. Por enquanto, o fluxo
        simplesmente para aqui (fase CONCLUIDO). No commit em que o BFS for
        reativado, é aqui que a gente chama start_bfs_phase() em vez de
        marcar CONCLUIDO direto.
        """
        print(f"\n[DFS] Saída encontrada em {self.dfs_steps} passos (incluindo backtracks).")
        print(f"[DFS] Grafo explorado: {len(self.graph_explorado)} nós, "
              f"{self.graph_explorado.num_edges()} arestas.")

        self.phase = 'CONCLUIDO'
        self.done_message = "Saída encontrada pelo DFS!"



    # ------------------------------------------------------------------ #
    # Loop principal
    # ------------------------------------------------------------------ #
    def run(self):
        while self.running:
            dt = self.clock.tick(cfg.FPS) / 1000.0
            self.handle_events()
            if not self.paused:
                self.update(dt)
            self.draw()
            pygame.display.flip()
        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_r:
                    self.new_maze()
                    self.paused = False
                elif event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                    self.speed = min(cfg.MAX_STEPS_PER_SEC, self.speed * 1.4)
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    self.speed = max(cfg.MIN_STEPS_PER_SEC, self.speed / 1.4)

    def update(self, dt):
        if self.phase == 'CONCLUIDO':
            return

        speed = self.speed


        self.time_accumulator += dt * speed
        while self.time_accumulator >= 1.0:
            self.time_accumulator -= 1.0
            if self.phase == 'DFS_EXPLORANDO':
                self.step_dfs()
            else:
                break

    # ------------------------------------------------------------------ #
    # Desenho
    # ------------------------------------------------------------------ #
    def build_cell_states(self):
        states = {}
        for node in self.visited_cells:
            states[node] = 'dfs_visited'


        states[self.start] = 'start'
        states[self.goal] = 'goal'

        if self.phase == 'DFS_EXPLORANDO':
            states[self.character_pos] = 'dfs_current'

        return states

    def draw(self):
        self.viz.draw_background()
        self.viz.draw_cells(self.build_cell_states())
        self.viz.draw_walls(self.grid, cfg.COLS, cfg.ROWS)
        self.viz.draw_start_goal_labels(self.start, self.goal)
        if self.phase != 'DFS_EXPLORANDO':
            self.viz.draw_character(self.character_pos)

        state = {
            'speed': self.speed,
        }
        self.viz.draw_sidebar(state)


if __name__ == '__main__':
    App().run()
