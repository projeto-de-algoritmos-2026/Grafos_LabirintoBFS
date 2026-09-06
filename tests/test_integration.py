import sys
import types
import unittest
from unittest.mock import patch

from graph import Graph
from algorithms import bfs_explore


class _FakeFont:
    def render(self, text, antialias, color):
        return types.SimpleNamespace(get_width=lambda: len(text), get_height=lambda: 1)


def _fake_pygame():
    pygame = types.ModuleType('pygame')
    pygame.init = lambda: None
    pygame.display = types.SimpleNamespace(
        set_caption=lambda title: None,
        set_mode=lambda size: object(),
    )
    pygame.time = types.SimpleNamespace(Clock=lambda: object())
    pygame.font = types.SimpleNamespace(SysFont=lambda *args, **kwargs: _FakeFont())
    return pygame


class AppBfsIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pygame_patch = patch.dict(sys.modules, {'pygame': _fake_pygame()})
        cls.pygame_patch.start()
        from main import App
        cls.App = App

    @classmethod
    def tearDownClass(cls):
        cls.pygame_patch.stop()

    def test_dfs_starts_bfs_once_and_exposes_return_path(self):
        app = self.App()

        while app.phase == 'DFS_EXPLORANDO':
            app.step_dfs()

        self.assertEqual(app.phase, 'BFS_CALCULANDO')
        bfs_generator = app.bfs_gen

        # Uma segunda chamada não deve reiniciar a busca nem substituir seu
        # gerador atual.
        app.dfs_finished()
        self.assertIs(app.bfs_gen, bfs_generator)

        while app.phase == 'BFS_CALCULANDO':
            app.step_bfs()

        self.assertEqual(app.phase, 'VOLTANDO_AO_INICIO')
        self.assertEqual(app.path[0], app.goal)
        self.assertEqual(app.path[-1], app.start)

    def test_unreachable_explored_graph_finishes_safely(self):
        app = self.App()
        app.graph_explorado = Graph()
        app.graph_explorado.add_node(app.goal)
        app.bfs_gen = bfs_explore(app.graph_explorado, app.goal, app.start)
        app.phase = 'BFS_CALCULANDO'

        while app.phase == 'BFS_CALCULANDO':
            app.step_bfs()

        self.assertEqual(app.phase, 'CONCLUIDO')
        self.assertEqual(app.path, [])
        self.assertIn('não encontrou', app.done_message)

    def test_return_animation_follows_path_cell_by_cell(self):
        app = self.App()

        while app.phase == 'DFS_EXPLORANDO':
            app.step_dfs()
        while app.phase == 'BFS_CALCULANDO':
            app.step_bfs()

        return_path = list(app.path)
        states = app.build_cell_states()
        self.assertEqual(states[app.start], 'start')
        self.assertEqual(states[app.goal], 'goal')
        for node in return_path[1:-1]:
            self.assertEqual(states[node], 'path')

        visited_on_return = []
        while app.phase == 'VOLTANDO_AO_INICIO':
            app.step_path()
            visited_on_return.append(app.character_pos)

        self.assertEqual(visited_on_return, return_path[1:])
        self.assertEqual(app.character_pos, app.start)
        self.assertEqual(app.phase, 'INDO_PARA_SAIDA')

        outgoing_path = list(app.path)
        visited_on_outgoing = []
        while app.phase == 'INDO_PARA_SAIDA':
            app.step_path()
            visited_on_outgoing.append(app.character_pos)

        self.assertEqual(visited_on_outgoing, outgoing_path[1:])
        self.assertEqual(app.character_pos, app.goal)
        self.assertEqual(app.phase, 'CONCLUIDO')

    def test_empty_path_finishes_without_moving(self):
        app = self.App()
        original_position = app.character_pos
        app.path = []
        app.path_index = 0
        app.phase = 'VOLTANDO_AO_INICIO'

        app.step_path()

        self.assertEqual(app.phase, 'CONCLUIDO')
        self.assertEqual(app.character_pos, original_position)
        self.assertIn('Nenhum caminho', app.done_message)

    def test_new_maze_resets_path_animation(self):
        app = self.App()
        app.path = [app.goal, app.start]
        app.path_index = 1
        app.phase = 'INDO_PARA_SAIDA'

        app.new_maze(seed=123)

        self.assertEqual(app.phase, 'DFS_EXPLORANDO')
        self.assertEqual(app.path, [])
        self.assertEqual(app.path_index, 0)
        self.assertEqual(app.character_pos, app.start)
        self.assertEqual(app.frontier_cells, set())

    def test_sidebar_snapshot_tracks_algorithm_structures(self):
        app = self.App()

        initial = app.build_sidebar_state()
        self.assertEqual(initial['phase'], 'DFS_EXPLORANDO')
        self.assertEqual(initial['stack'], [app.start])
        self.assertEqual(initial['queue'], [])
        self.assertEqual(initial['visited'], [app.start])
        self.assertEqual(initial['dfs_steps'], 0)
        self.assertEqual(initial['path_length'], 0)

        app.step_dfs()
        during_dfs = app.build_sidebar_state()
        self.assertEqual(during_dfs['stack'], app._last_stack)
        self.assertEqual(during_dfs['visited'], sorted(app.visited_cells))

        while app.phase == 'DFS_EXPLORANDO':
            app.step_dfs()
        app.step_bfs()
        during_bfs = app.build_sidebar_state()
        self.assertEqual(during_bfs['phase'], 'BFS_CALCULANDO')
        self.assertEqual(during_bfs['queue'], app.frontier_queue)
        self.assertEqual(during_bfs['visited'], sorted(app.visited_cells))


if __name__ == '__main__':
    unittest.main()
