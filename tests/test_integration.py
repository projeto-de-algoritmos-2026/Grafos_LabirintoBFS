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


if __name__ == '__main__':
    unittest.main()
