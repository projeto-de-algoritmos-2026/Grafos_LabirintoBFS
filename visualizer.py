# -*- coding: utf-8 -*-
"""
Tudo relacionado a desenhar a cena na tela com Pygame: o labirinto (paredes),
as células coloridas de acordo com o estado do algoritmo, o personagem, e o
painel lateral (HUD) com status, contadores e a pilha/fila do algoritmo atual.
"""

import sys

import pygame
import config as cfg


# Pygame 2.6.1 possui uma importação circular em pygame.font no Python 3.14.
# Nesse ambiente, evita-se até tentar carregar o módulo problemático.
_USE_FREETYPE_FALLBACK = sys.version_info >= (3, 14)


class _FreetypeFontAdapter:
    """Adapta pygame._freetype.Font à API usada pelo desenhador."""

    def __init__(self, font):
        self.font = font

    def render(self, text, antialias, color):
        surface, _ = self.font.render(text, fgcolor=color)
        return surface


def _make_font(size, bold=False):
    """Cria uma fonte mesmo quando pygame.font falha no Python 3.14.

    Pygame 2.6.1 pode deixar pygame.font/sysfont em importação circular em
    algumas versões recentes do Python. O backend _freetype não passa por
    esse caminho e expõe renderização equivalente para o painel.
    """
    global _USE_FREETYPE_FALLBACK

    if not _USE_FREETYPE_FALLBACK:
        try:
            return pygame.font.SysFont(cfg.FONT_NAME, size, bold=bold)
        except (ImportError, NotImplementedError):
            _USE_FREETYPE_FALLBACK = True

    try:
        import pygame._freetype as freetype
    except (ImportError, ModuleNotFoundError):
        # Permite usar doubles de teste e builds antigas sem _freetype.
        return pygame.font.SysFont(cfg.FONT_NAME, size, bold=bold)

    freetype.init()
    font = freetype.Font(None, size)
    font.strong = bold
    return _FreetypeFontAdapter(font)


class Visualizer:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = _make_font(cfg.FONT_SIZE_TITLE, bold=True)
        self.font_normal = _make_font(cfg.FONT_SIZE_NORMAL)
        self.font_small = _make_font(cfg.FONT_SIZE_SMALL)

    # ------------------------------------------------------------------ #
    # Coordenadas
    # ------------------------------------------------------------------ #
    def cell_rect(self, x, y):
        px = cfg.MARGIN + x * cfg.CELL_SIZE
        py = cfg.MARGIN + y * cfg.CELL_SIZE
        return pygame.Rect(px, py, cfg.CELL_SIZE, cfg.CELL_SIZE)

    def cell_center(self, x, y):
        r = self.cell_rect(x, y)
        return r.center

    # ------------------------------------------------------------------ #
    # Cena principal
    # ------------------------------------------------------------------ #
    def draw_background(self):
        self.screen.fill(cfg.COLOR_BG)
        sidebar_rect = pygame.Rect(
            cfg.COLS * cfg.CELL_SIZE + cfg.MARGIN * 2, 0,
            cfg.SIDEBAR_WIDTH, cfg.WINDOW_HEIGHT,
        )
        pygame.draw.rect(self.screen, cfg.COLOR_SIDEBAR_BG, sidebar_rect)

    def draw_cells(self, cell_states):
        """
        cell_states: dict (x, y) -> uma das strings:
            'unvisited', 'dfs_visited', 'dfs_current',
            'bfs_frontier', 'path', 'start', 'goal'
        """
        color_map = {
            'unvisited': cfg.COLOR_CELL_UNVISITED,
            'dfs_visited': cfg.COLOR_CELL_DFS_VISITED,
            'dfs_current': cfg.COLOR_CELL_DFS_CURRENT,
            'bfs_visited': cfg.COLOR_CELL_BFS_VISITED,
            'bfs_frontier': cfg.COLOR_CELL_BFS_FRONTIER,
            'bidir_a': cfg.COLOR_CELL_BIDIR_A,
            'bidir_b': cfg.COLOR_CELL_BIDIR_B,
            'bidir_frontier_a': cfg.COLOR_CELL_BIDIR_FRONTIER_A,
            'bidir_frontier_b': cfg.COLOR_CELL_BIDIR_FRONTIER_B,
            'bidir_meeting': cfg.COLOR_CELL_BIDIR_MEETING,
            'path': cfg.COLOR_CELL_PATH,
            'start': cfg.COLOR_CELL_START,
            'goal': cfg.COLOR_CELL_GOAL,
        }
        for (x, y), state in cell_states.items():
            color = color_map.get(state, cfg.COLOR_CELL_UNVISITED)
            pygame.draw.rect(self.screen, color, self.cell_rect(x, y))

    def draw_walls(self, grid, cols, rows):
        for y in range(rows):
            for x in range(cols):
                cell = grid[y][x]
                r = self.cell_rect(x, y)
                if cell.walls['N']:
                    pygame.draw.line(self.screen, cfg.COLOR_WALL, r.topleft, r.topright, cfg.WALL_THICKNESS)
                if cell.walls['S']:
                    pygame.draw.line(self.screen, cfg.COLOR_WALL, r.bottomleft, r.bottomright, cfg.WALL_THICKNESS)
                if cell.walls['W']:
                    pygame.draw.line(self.screen, cfg.COLOR_WALL, r.topleft, r.bottomleft, cfg.WALL_THICKNESS)
                if cell.walls['E']:
                    pygame.draw.line(self.screen, cfg.COLOR_WALL, r.topright, r.bottomright, cfg.WALL_THICKNESS)

    def draw_character(self, pos):
        cx, cy = self.cell_center(*pos)
        radius = cfg.CELL_SIZE // 2 - 5
        pygame.draw.circle(self.screen, cfg.COLOR_CHARACTER, (cx, cy), radius)
        pygame.draw.circle(self.screen, (10, 10, 12), (cx, cy), radius, 2)

    def draw_start_goal_labels(self, start, goal):
        sx, sy = self.cell_center(*start)
        gx, gy = self.cell_center(*goal)
        s_label = self.font_small.render("INÍCIO", True, cfg.COLOR_TEXT)
        g_label = self.font_small.render("SAÍDA", True, cfg.COLOR_TEXT)
        self.screen.blit(s_label, (sx - s_label.get_width() // 2, sy - cfg.CELL_SIZE))
        self.screen.blit(g_label, (gx - g_label.get_width() // 2, gy - cfg.CELL_SIZE))

    # ------------------------------------------------------------------ #
    # HUD / Painel lateral
    # ------------------------------------------------------------------ #
    def _draw_timer_block(self, write, divider, state):
        """Mostra, no topo do painel, o tempo (real, de parede) gasto até
        cada etapa terminar. Não tenta compensar a velocidade de animação —
        é só o cronômetro solto desde o início da rodada."""
        write("Tempos das etapas:", self.font_normal, cfg.COLOR_TEXT_DIM, 22)
        stage_times = state.get('stage_times', {})
        labels = [
            ('dfs', "DFS achou a saída"),
            ('bfs', "BFS achou o caminho"),
            ('volta', "Chegou ao início"),
            ('saida', "Chegou de novo na saída"),
        ]
        for key, label in labels:
            if key in stage_times:
                value = f"{stage_times[key]:.2f}s"
                color = cfg.COLOR_TEXT
            else:
                value = "—"
                color = cfg.COLOR_TEXT_DIM
            write(f"{label}: {value}", self.font_small, color, 20)

        if 'total' in stage_times and 'saida' not in stage_times:
            # Terminou sem sucesso (ex.: caminho não encontrado).
            write(f"Encerrado em: {stage_times['total']:.2f}s", self.font_small, cfg.COLOR_TEXT, 20)

        write(f"Tempo decorrido: {state['elapsed_now']:.1f}s", self.font_small, cfg.COLOR_TEXT_DIM, 20)
        divider()

    def draw_sidebar(self, state):
        """
        state: dict com as chaves usadas para montar o texto do painel.
        Veja main.py para a lista completa de campos.
        """
        x0 = cfg.COLS * cfg.CELL_SIZE + cfg.MARGIN * 2 + 20
        y = 24
        line_h_title = 30
        line_h = 24

        def write(text, font=None, color=None, dy=None):
            nonlocal y
            font = font or self.font_normal
            color = color or cfg.COLOR_TEXT
            surf = font.render(text, True, color)
            self.screen.blit(surf, (x0, y))
            y += dy if dy is not None else line_h

        def divider():
            nonlocal y
            y += 6
            pygame.draw.line(self.screen, cfg.COLOR_PANEL_DIVIDER, (x0, y), (x0 + cfg.SIDEBAR_WIDTH - 40, y), 1)
            y += 14

        write("Projeto PA - Grafos", self.font_title, cfg.COLOR_TEXT_ACCENT, line_h_title)
        divider()

        self._draw_timer_block(write, divider, state)

        write("Legenda:", self.font_normal, cfg.COLOR_TEXT_DIM, 22)
        legend = [
            (cfg.COLOR_CELL_START, "Início"),
            (cfg.COLOR_CELL_GOAL, "Saída"),
            (cfg.COLOR_CELL_DFS_CURRENT, "Célula atual do DFS"),
            (cfg.COLOR_CELL_DFS_VISITED, "Área explorada pelo DFS"),
            (cfg.COLOR_CELL_BFS_VISITED, "Visitado pelo BFS"),
            (cfg.COLOR_CELL_BFS_FRONTIER, "Fronteira da fila BFS"),
            (cfg.COLOR_CELL_PATH, "Caminho mínimo do BFS"),
        ]
        for color, label in legend:
            pygame.draw.rect(self.screen, color, pygame.Rect(x0, y + 3, 14, 14))
            surf = self.font_small.render(label, True, cfg.COLOR_TEXT)
            self.screen.blit(surf, (x0 + 22, y))
            y += 22

        divider()
        write("Controles:", self.font_normal, cfg.COLOR_TEXT_DIM, 22)
        for line in [
            "ESPAÇO — pausar / continuar",
            "R — novo labirinto",
            "S — repetir cenário atual",
            "+ / -  — velocidade",
            "ESC — sair",
            "X — repete com BFS bidirecional"
        ]:
            write(line, self.font_small, cfg.COLOR_TEXT, 20)

        y += 6
        write(f"Velocidade: {state['speed']:.1f} passos/s", self.font_small, cfg.COLOR_TEXT_DIM, 20)
        write(f"Seed: {state['seed']}", self.font_small, cfg.COLOR_TEXT_DIM, 20)

        y += 4
        phase_labels = {
            'DFS_EXPLORANDO': 'DFS explorando',
            'BFS_CALCULANDO': 'BFS calculando',
            'VOLTANDO_AO_INICIO': 'Voltando ao início',
            'INDO_PARA_SAIDA': 'Indo para a saída',
            'CONCLUIDO': 'Concluído',
        }
        write(f"Fase: {phase_labels.get(state['phase'], state['phase'])}", self.font_small)
        write(f"Passos DFS: {state['dfs_steps']}", self.font_small, cfg.COLOR_TEXT_DIM, 20)
        write(f"Células visitadas: {len(state['visited'])}", self.font_small, cfg.COLOR_TEXT_DIM, 20)
        write(f"Pilha DFS: {len(state['stack'])}", self.font_small, cfg.COLOR_TEXT_DIM, 20)
        write(f"Fila BFS: {len(state['queue'])}", self.font_small, cfg.COLOR_TEXT_DIM, 20)
        write(f"Menor caminho: {state['path_length']} arestas", self.font_small, cfg.COLOR_TEXT_DIM, 20)

        write(
            f"Pilha: {self._summarize_nodes(state['stack'])}",
            self.font_small, cfg.COLOR_TEXT_DIM, 20,
        )
        write(
            f"Fila: {self._summarize_nodes(state['queue'])}",
            self.font_small, cfg.COLOR_TEXT_DIM, 20,
        )
        write(
            f"Visitadas: {self._summarize_nodes(state['visited'])}",
            self.font_small, cfg.COLOR_TEXT_DIM, 20,
        )
        if state['done_message']:
            for line in self._wrap_text(state['done_message'], 42)[:2]:
                write(f"Status: {line}", self.font_small, cfg.COLOR_TEXT_DIM, 18)

    @staticmethod
    def _summarize_nodes(nodes, limit=4):
        """Formata uma coleção de células sem deixar o painel crescer."""
        if not nodes:
            return "—"

        formatted = [str(node) for node in nodes[:limit]]
        summary = ", ".join(formatted)
        remaining = len(nodes) - limit
        if remaining > 0:
            summary += f" ... (+{remaining})"
        return summary

    @staticmethod
    def _wrap_text(text, max_chars):
        words = text.split(" ")
        lines = []
        current = ""
        for w in words:
            if len(current) + len(w) + 1 <= max_chars:
                current = (current + " " + w).strip()
            else:
                lines.append(current)
                current = w
        if current:
            lines.append(current)
        return lines