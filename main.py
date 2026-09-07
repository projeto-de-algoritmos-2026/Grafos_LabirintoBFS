# -*- coding: utf-8 -*-
"""
Ponto de entrada. Contém a máquina de estados que orquestra a simulação.

O personagem anda pelo grafo completo (grafo 1) usando DFS, construindo o
grafo explorado (grafo 2) em tempo real. Quando encontra a saída, o BFS
calcula o menor caminho no grafo explorado e anima a volta ao início e a nova
ida até a saída.

Rode com:  python main.py
"""

import random
import sys
import time
import pygame

import config as cfg
from maze import generate_maze
from graph import Graph
from algorithms import bfs_explore, dfs_explore


class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("DFS explora, BFS resolve — labirinto")
        self.screen = pygame.display.set_mode((cfg.WINDOW_WIDTH, cfg.WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()

        from visualizer import Visualizer
        self.viz = Visualizer(self.screen)

        self.speed = cfg.DEFAULT_STEPS_PER_SEC
        self.paused = False
        self.running = True

        self.new_maze(seed=cfg.DEFAULT_SEED)

    # ------------------------------------------------------------------ #
    # (Re)inicialização de uma rodada
    # ------------------------------------------------------------------ #
    def new_maze(self, seed=None):
        if seed is None:
            seed = random.SystemRandom().randrange(0, 2 ** 32)
        self.seed = seed

        self.grid, self.graph_completo, self.start, self.goal = generate_maze(
            cfg.COLS, cfg.ROWS, seed=self.seed
        )

        # Grafo 2: começa vazio, só com o nó inicial. É preenchido conforme
        # o DFS avança (cada 'advance' vira uma aresta nova aqui).
        self.graph_explorado = Graph()
        self.graph_explorado.add_node(self.start)

        self.dfs_gen = dfs_explore(
            self.graph_completo, self.start, self.goal, seed=self.seed
        )

        self.bfs_gen = None
        self.path = []
        self.path_index = 0

        self.character_pos = self.start
        self.visited_cells = {self.start}
        self.dfs_visited_cells = {self.start}
        self.bfs_visited_cells = set()
        self.frontier_cells = set()
        self.frontier_queue = []
        self.dfs_steps = 0
        self.bfs_steps = 0
        self.path_steps = 0
        self._last_stack = [self.start]
        self.phase = 'DFS_EXPLORANDO'
        self.time_accumulator = 0.0
        self.done_message = ""

        # --- Timer das etapas ---
        # Tempo de parede (não compensa a velocidade de animação escolhida):
        # só marca o instante em que a rodada começou e, mais adiante,
        # o instante (relativo a esse início) em que cada etapa termina.
        self.round_start_time = time.perf_counter()
        self.stage_times = {}  # ex.: {'dfs': 1.23, 'bfs': 1.87, ...}

    # ------------------------------------------------------------------ #
    # Timer das etapas
    # ------------------------------------------------------------------ #
    def _record_stage_time(self, key):
        """
        Guarda, em `self.stage_times[key]`, quantos segundos (reais, de
        parede) se passaram desde o início da rodada até agora. Não mexe
        de novo numa etapa que já foi marcada.
        """
        if key not in self.stage_times:
            self.stage_times[key] = time.perf_counter() - self.round_start_time

    # ------------------------------------------------------------------ #
    # Avanço de um "passo lógico" do algoritmo ativo
    # ------------------------------------------------------------------ #
    def step_dfs(self):
        try:
            event = next(self.dfs_gen)
        except StopIteration:
            self.phase = 'CONCLUIDO'
            self.done_message = "DFS terminou sem achar a saída (não deveria acontecer aqui)."
            self._record_stage_time('total')
            return

        if event['type'] == 'move':
            to_node = event['to']
            from_node = event['from']
            self.character_pos = to_node
            self.visited_cells.add(to_node)
            self.dfs_visited_cells.add(to_node)
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
            self._record_stage_time('total')

    def dfs_finished(self):
        # A transição só pode acontecer uma vez por rodada. Isso também
        # protege contra chamadas repetidas ao handler de conclusão do DFS.
        if self.phase != 'DFS_EXPLORANDO':
            return

        self._record_stage_time('dfs')
        print(f"\n[DFS] Saída encontrada em {self.dfs_steps} passos (incluindo backtracks).")
        print(f"[DFS] Grafo explorado: {len(self.graph_explorado)} nós, "
              f"{self.graph_explorado.num_edges()} arestas.")
        print(f"[TIMER] DFS achou a saída em {self.stage_times['dfs']:.3f}s.")

        self.start_bfs_phase()

    def start_bfs_phase(self):
        """Inicializa uma única busca BFS da saída até o início."""
        if self.phase != 'DFS_EXPLORANDO':
            return

        self.bfs_gen = bfs_explore(
            self.graph_explorado, self.goal, self.start
        )
        self.path = []
        self.path_index = 0
        self.bfs_steps = 0
        self.frontier_cells = {self.goal}
        self.frontier_queue = [self.goal]
        self.phase = 'BFS_CALCULANDO'
        self.done_message = "DFS encontrou a saída. BFS calculando o menor caminho..."

    def step_bfs(self):
        """Processa um evento da busca em largura e prepara a caminhada."""
        try:
            event = next(self.bfs_gen)
        except StopIteration:
            self.phase = 'CONCLUIDO'
            self.done_message = "BFS terminou sem encontrar um caminho."
            self._record_stage_time('total')
            return

        self.bfs_steps += 1
        self.frontier_queue = list(event.get('queue', []))
        self.frontier_cells = set(self.frontier_queue)

        if event['type'] == 'visit':
            self.visited_cells.update(event.get('visited', set()))
            self.bfs_visited_cells.update(event.get('visited', set()))
        elif event['type'] == 'path_found':
            self.path = event['path']
            self.path_index = 0
            self.frontier_cells.clear()
            self.frontier_queue.clear()
            self.character_pos = self.path[0]
            self.phase = 'VOLTANDO_AO_INICIO'
            self._record_stage_time('bfs')
            print(f"[TIMER] BFS achou o menor caminho em {self.stage_times['bfs']:.3f}s.")
            self.done_message = (
                f"Menor caminho encontrado: {len(self.path) - 1} arestas. "
                "Voltando ao início..."
            )
        elif event['type'] == 'exhausted':
            self.phase = 'CONCLUIDO'
            self.done_message = "BFS não encontrou um caminho até o início."
            self._record_stage_time('total')

    def step_path(self):
        """Anda uma célula no caminho calculado pelo BFS."""
        if not self.path:
            self.phase = 'CONCLUIDO'
            self.frontier_cells.clear()
            self.frontier_queue.clear()
            self.done_message = "Nenhum caminho foi encontrado; retorno encerrado com segurança."
            self._record_stage_time('total')
            return

        if self.path_index + 1 >= len(self.path):
            self.finish_path_leg()
            return

        self.path_index += 1
        self.character_pos = self.path[self.path_index]
        self.path_steps += 1

        # A chegada à última célula já conclui esta perna, sem emitir um
        # segundo evento de movimento para a mesma posição.
        if self.path_index + 1 >= len(self.path):
            self.finish_path_leg()

    def finish_path_leg(self):
        """Transiciona após concluir uma das pernas do caminho do BFS."""
        if self.phase == 'VOLTANDO_AO_INICIO':
            self._record_stage_time('volta')
            print(f"[TIMER] Personagem chegou ao início em {self.stage_times['volta']:.3f}s.")
            self.path = list(reversed(self.path))
            self.path_index = 0
            self.character_pos = self.path[0]
            self.phase = 'INDO_PARA_SAIDA'
            self.done_message = "De volta ao início. Seguindo o menor caminho até a saída..."
        else:
            self.phase = 'CONCLUIDO'
            self.character_pos = self.goal
            self._record_stage_time('saida')
            self._record_stage_time('total')
            print(f"[TIMER] Personagem chegou de volta na saída em {self.stage_times['saida']:.3f}s.")
            self.done_message = (
                f"Concluído! DFS: {self.dfs_steps} passos; "
                f"menor caminho: {len(self.path) - 1} arestas."
            )



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
                elif event.key == pygame.K_s:
                    self.new_maze(seed=self.seed)
                    self.paused = False
                elif event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                    self.speed = min(cfg.MAX_STEPS_PER_SEC, self.speed * 1.4)
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    self.speed = max(cfg.MIN_STEPS_PER_SEC, self.speed / 1.4)

    def update(self, dt):
        if self.phase == 'CONCLUIDO':
            return

        speed = self.speed
        if self.phase == 'BFS_CALCULANDO':
            speed *= cfg.BFS_SPEED_MULTIPLIER
        self.time_accumulator += dt * speed
        while self.time_accumulator >= 1.0:
            self.time_accumulator -= 1.0
            if self.phase == 'DFS_EXPLORANDO':
                self.step_dfs()
            elif self.phase == 'BFS_CALCULANDO':
                self.step_bfs()
            elif self.phase in ('VOLTANDO_AO_INICIO', 'INDO_PARA_SAIDA'):
                self.step_path()
            else:
                break

    # ------------------------------------------------------------------ #
    # Desenho
    # ------------------------------------------------------------------ #
    def build_cell_states(self):
        states = {}
        for node in self.dfs_visited_cells:
            states[node] = 'dfs_visited'

        for node in self.bfs_visited_cells:
            states[node] = 'bfs_visited'

        if self.phase == 'BFS_CALCULANDO':
            for node in self.frontier_cells:
                states[node] = 'bfs_frontier'
        elif self.phase in ('VOLTANDO_AO_INICIO', 'INDO_PARA_SAIDA'):
            for node in self.path:
                states[node] = 'path'

        states[self.start] = 'start'
        states[self.goal] = 'goal'

        if self.phase == 'DFS_EXPLORANDO':
            states[self.character_pos] = 'dfs_current'

        return states

    def build_sidebar_state(self):
        """Monta o snapshot de dados exibido pelo painel lateral."""
        return {
            'speed': self.speed,
            'seed': self.seed,
            'phase': self.phase,
            'dfs_steps': self.dfs_steps,
            'bfs_steps': self.bfs_steps,
            'path_length': max(0, len(self.path) - 1),
            'stack': list(self._last_stack),
            'queue': list(self.frontier_queue),
            'visited': sorted(self.visited_cells),
            'done_message': self.done_message,
            'stage_times': dict(self.stage_times),
            'elapsed_now': time.perf_counter() - self.round_start_time,
        }

    def draw(self):
        self.viz.draw_background()
        self.viz.draw_cells(self.build_cell_states())
        self.viz.draw_walls(self.grid, cfg.COLS, cfg.ROWS)
        self.viz.draw_start_goal_labels(self.start, self.goal)
        if self.phase != 'DFS_EXPLORANDO':
            self.viz.draw_character(self.character_pos)

        self.viz.draw_sidebar(self.build_sidebar_state())


if __name__ == '__main__':
    App().run()
