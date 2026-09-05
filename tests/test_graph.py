import unittest

from graph import Graph


class GraphTests(unittest.TestCase):
    def test_add_node_is_idempotent(self):
        graph = Graph()

        graph.add_node('A')
        graph.add_node('A')

        self.assertEqual(len(graph), 1)
        self.assertEqual(list(graph.neighbors('A')), [])
        self.assertIn('A', graph)
        self.assertNotIn('B', graph)

    def test_bidirectional_edge_and_duplicate_prevention(self):
        graph = Graph()

        graph.add_edge('A', 'B')
        graph.add_edge('A', 'B')
        graph.add_edge('B', 'A')

        self.assertEqual(list(graph.neighbors('A')), ['B'])
        self.assertEqual(list(graph.neighbors('B')), ['A'])
        self.assertEqual(graph.edges(), [('A', 'B')])
        self.assertEqual(graph.num_edges(), 1)
        self.assertEqual(len(graph), 2)

    def test_directed_edge_does_not_add_reverse_neighbor(self):
        graph = Graph()

        graph.add_edge('A', 'B', bidirectional=False)

        self.assertEqual(list(graph.neighbors('A')), ['B'])
        self.assertEqual(list(graph.neighbors('B')), [])
        self.assertEqual(graph.num_edges(), 1)

    def test_edges_and_counts_for_multiple_connections(self):
        graph = Graph()

        graph.add_edge('A', 'B')
        graph.add_edge('B', 'C')
        graph.add_edge('C', 'A')

        self.assertEqual(set(graph.nodes()), {'A', 'B', 'C'})
        self.assertEqual(graph.num_edges(), 3)
        self.assertEqual(
            {frozenset(edge) for edge in graph.edges()},
            {frozenset(('A', 'B')), frozenset(('B', 'C')), frozenset(('C', 'A'))},
        )


if __name__ == '__main__':
    unittest.main()
