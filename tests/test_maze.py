import unittest

from algorithms import dfs_explore
from maze import generate_maze


def grid_fingerprint(grid):
    return tuple(
        tuple(
            tuple(cell.walls[direction] for direction in ('N', 'S', 'E', 'W'))
            for cell in row
        )
        for row in grid
    )


class ReproducibleMazeTests(unittest.TestCase):
    def test_same_seed_reproduces_maze_and_dfs_order(self):
        first_grid, first_graph, start, goal = generate_maze(10, 7, seed=12345)
        second_grid, second_graph, _, _ = generate_maze(10, 7, seed=12345)

        self.assertEqual(grid_fingerprint(first_grid), grid_fingerprint(second_grid))
        self.assertEqual(first_graph.edges(), second_graph.edges())
        self.assertEqual(
            list(dfs_explore(first_graph, start, goal, seed=12345)),
            list(dfs_explore(second_graph, start, goal, seed=12345)),
        )

    def test_different_seed_can_produce_a_different_maze(self):
        first_grid, _, _, _ = generate_maze(10, 7, seed=1)
        second_grid, _, _, _ = generate_maze(10, 7, seed=2)

        self.assertNotEqual(grid_fingerprint(first_grid), grid_fingerprint(second_grid))


if __name__ == '__main__':
    unittest.main()
