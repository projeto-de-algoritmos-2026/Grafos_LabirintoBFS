# -*- coding: utf-8 -*-
"""
Configurações globais do projeto: dimensões, cores e parâmetros de animação.
"""

# --- Dimensões do labirinto (em células) ---
# Mantendo pequeno por enquanto, só para validar visualmente se DFS e BFS
# estão corretos antes de mexer na UI/UX.
COLS = 10
ROWS = 7

# --- Dimensões visuais ---
CELL_SIZE = 56
SIDEBAR_WIDTH = 360
MARGIN = 20
WALL_THICKNESS = 3

WINDOW_WIDTH = COLS * CELL_SIZE + SIDEBAR_WIDTH + MARGIN * 2
# A lateral do painel precisa de espaço para a legenda, controles e métricas
# das fases DFS/BFS, mesmo quando o labirinto é baixo.
WINDOW_HEIGHT = max(ROWS * CELL_SIZE + MARGIN * 2, 520)

FPS = 60

# --- Velocidade da animação (passos do algoritmo por segundo) ---
DEFAULT_STEPS_PER_SEC = 4.0
MIN_STEPS_PER_SEC = 1.0
MAX_STEPS_PER_SEC = 60.0

# Fase de BFS costuma ter muito mais "eventos de visita" que células no grid
# então deixamos ela mais rápida por padrão para não ficar arrastado.
BFS_SPEED_MULTIPLIER = 2.5

# --- Cores (R, G, B) ---
COLOR_BG = (24, 26, 34)
COLOR_SIDEBAR_BG = (18, 20, 27)
COLOR_WALL = (230, 230, 235)
COLOR_CELL_UNVISITED = (40, 43, 56)
COLOR_CELL_DFS_VISITED = (61, 90, 128)      # trilha do DFS (grafo explorado)
COLOR_CELL_DFS_CURRENT = (247, 199, 68)      # célula atual durante o DFS
COLOR_CELL_BFS_FRONTIER = (156, 107, 219)    # fronteira sendo visitada pelo BFS
COLOR_CELL_PATH = (76, 201, 138)             # caminho ótimo encontrado pelo BFS
COLOR_CELL_START = (46, 139, 87)
COLOR_CELL_GOAL = (196, 62, 62)
COLOR_CHARACTER = (255, 255, 255)

COLOR_TEXT = (230, 230, 235)
COLOR_TEXT_DIM = (140, 145, 160)
COLOR_TEXT_ACCENT = (247, 199, 68)
COLOR_PANEL_DIVIDER = (55, 58, 72)

FONT_NAME = None  # usa fonte default do pygame
FONT_SIZE_TITLE = 22
FONT_SIZE_NORMAL = 17
FONT_SIZE_SMALL = 14
