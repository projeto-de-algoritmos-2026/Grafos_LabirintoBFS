import unittest

from algorithms import bfs_shortest_path
from graph import Graph


class BfsShortestPathTests(unittest.TestCase):
    def setUp(self):
        self.graph = Graph()
        self.graph.add_edge('A', 'B')
        self.graph.add_edge('A', 'C')
        self.graph.add_edge('B', 'D')
        self.graph.add_edge('C', 'E')
        self.graph.add_edge('E', 'F')
        self.graph.add_edge('F', 'D')

    def test_returns_minimum_path_in_origin_to_destination_order(self):
        self.assertEqual(
            bfs_shortest_path(self.graph, 'A', 'D'),
            ['A', 'B', 'D'],
        )

    def test_origin_equal_destination(self):
        self.assertEqual(
            bfs_shortest_path(self.graph, 'A', 'A'),
            ['A'],
        )

    def test_unreachable_destination_returns_none(self):
        self.assertIsNone(bfs_shortest_path(self.graph, 'A', 'Z'))


if __name__ == '__main__':
    unittest.main()
