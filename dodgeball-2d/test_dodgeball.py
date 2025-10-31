#!/usr/bin/env python3
"""
Comprehensive test suite for Dodgeball 2D Simulation
Tests cover basic functionality, edge cases, and complex scenarios.
"""

import pytest
from dodgeball import (
    parse_input,
    get_direction_vector,
    find_players,
    simulate_throw,
    simulate_turn,
    remove_players,
    count_active_players,
    simulate_game,
    print_grid
)
from io import StringIO
import sys


class TestParseInput:
    """Test input parsing functionality."""

    def test_basic_parse(self):
        """Test parsing of basic input."""
        input_text = """4 5 2
A....
..B..
.....
....C
A:E B:W C:NW
A:E B:W C:NW"""

        n, m, t, grid, turn_directions = parse_input(input_text)

        assert n == 4
        assert m == 5
        assert t == 2
        assert len(grid) == 4
        assert len(grid[0]) == 5
        assert grid[0][0] == 'A'
        assert grid[1][2] == 'B'
        assert grid[3][4] == 'C'
        assert len(turn_directions) == 2
        assert turn_directions[0]['A'] == 'E'
        assert turn_directions[0]['B'] == 'W'
        assert turn_directions[0]['C'] == 'NW'

    def test_single_player_parse(self):
        """Test parsing with single player."""
        input_text = """2 2 1
A.
..
A:S"""

        n, m, t, grid, turn_directions = parse_input(input_text)

        assert n == 2
        assert m == 2
        assert t == 1
        assert grid[0][0] == 'A'


class TestDirectionVector:
    """Test direction vector conversion."""

    def test_all_directions(self):
        """Test all eight compass directions."""
        assert get_direction_vector('N') == (-1, 0)
        assert get_direction_vector('NE') == (-1, 1)
        assert get_direction_vector('E') == (0, 1)
        assert get_direction_vector('SE') == (1, 1)
        assert get_direction_vector('S') == (1, 0)
        assert get_direction_vector('SW') == (1, -1)
        assert get_direction_vector('W') == (0, -1)
        assert get_direction_vector('NW') == (-1, -1)


class TestFindPlayers:
    """Test player finding functionality."""

    def test_find_multiple_players(self):
        """Test finding multiple players on grid."""
        grid = [
            ['A', '.', '.', '.', '.'],
            ['.', '.', 'B', '.', '.'],
            ['.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', 'C']
        ]

        players = find_players(grid)

        assert len(players) == 3
        assert players['A'] == (0, 0)
        assert players['B'] == (1, 2)
        assert players['C'] == (3, 4)

    def test_find_single_player(self):
        """Test finding single player."""
        grid = [
            ['.', '.'],
            ['.', 'X']
        ]

        players = find_players(grid)

        assert len(players) == 1
        assert players['X'] == (1, 1)

    def test_find_no_players(self):
        """Test grid with no players."""
        grid = [
            ['.', '.'],
            ['.', '.']
        ]

        players = find_players(grid)

        assert len(players) == 0


class TestSimulateThrow:
    """Test ball throwing simulation."""

    def test_throw_hits_player(self):
        """Test throw that hits another player."""
        grid = [
            ['A', '.', 'B', '.'],
            ['.', '.', '.', '.']
        ]

        hit = simulate_throw(grid, (0, 0), 'E', 'A')

        assert hit == 'B'

    def test_throw_misses(self):
        """Test throw that misses all players."""
        grid = [
            ['A', '.', '.', '.'],
            ['.', '.', '.', 'B']
        ]

        hit = simulate_throw(grid, (0, 0), 'N', 'A')

        assert hit is None

    def test_throw_diagonal_hit(self):
        """Test diagonal throw hitting a player."""
        grid = [
            ['A', '.', '.', '.'],
            ['.', '.', '.', '.'],
            ['.', '.', 'B', '.'],
            ['.', '.', '.', '.']
        ]

        hit = simulate_throw(grid, (0, 0), 'SE', 'A')

        assert hit == 'B'

    def test_throw_stops_at_first_player(self):
        """Test that throw stops at first player hit."""
        grid = [
            ['A', 'B', 'C', 'D']
        ]

        hit = simulate_throw(grid, (0, 0), 'E', 'A')

        assert hit == 'B'  # Should hit B, not C or D


class TestSimulateTurn:
    """Test turn simulation."""

    def test_single_elimination(self):
        """Test single player being eliminated."""
        grid = [
            ['A', '.', 'B']
        ]
        directions = {'A': 'E'}

        eliminated, actions = simulate_turn(grid, directions)

        assert 'B' in eliminated
        assert len(eliminated) == 1

    def test_mutual_elimination(self):
        """Test two players eliminating each other."""
        grid = [
            ['A', '.', 'B']
        ]
        directions = {'A': 'E', 'B': 'W'}

        eliminated, actions = simulate_turn(grid, directions)

        assert 'A' in eliminated
        assert 'B' in eliminated
        assert len(eliminated) == 2

    def test_multiple_hits_same_target(self):
        """Test multiple players hitting the same target."""
        grid = [
            ['A', '.', 'X'],
            ['.', '.', '.'],
            ['B', '.', '.']
        ]
        directions = {'A': 'E', 'B': 'N'}

        eliminated, actions = simulate_turn(grid, directions)

        # X should be in eliminated (can be hit by A)
        # Both A and B throw, but only one can hit X
        assert 'X' in eliminated

    def test_no_eliminations(self):
        """Test turn with no eliminations."""
        grid = [
            ['A', '.', '.'],
            ['.', '.', '.'],
            ['.', '.', 'B']
        ]
        directions = {'A': 'N', 'B': 'S'}

        eliminated, actions = simulate_turn(grid, directions)

        assert len(eliminated) == 0


class TestRemovePlayers:
    """Test player removal from grid."""

    def test_remove_single_player(self):
        """Test removing a single player."""
        grid = [
            ['A', '.', 'B']
        ]

        remove_players(grid, {'B'})

        assert grid[0][0] == 'A'
        assert grid[0][2] == '.'

    def test_remove_multiple_players(self):
        """Test removing multiple players."""
        grid = [
            ['A', 'B', 'C']
        ]

        remove_players(grid, {'A', 'C'})

        assert grid[0][0] == '.'
        assert grid[0][1] == 'B'
        assert grid[0][2] == '.'


class TestCountActivePlayers:
    """Test active player counting."""

    def test_count_multiple_players(self):
        """Test counting multiple players."""
        grid = [
            ['A', '.', 'B'],
            ['.', 'C', '.']
        ]

        assert count_active_players(grid) == 3

    def test_count_no_players(self):
        """Test counting with no players."""
        grid = [
            ['.', '.'],
            ['.', '.']
        ]

        assert count_active_players(grid) == 0

    def test_count_single_player(self):
        """Test counting single player."""
        grid = [
            ['.', 'X', '.']
        ]

        assert count_active_players(grid) == 1


class TestSimulateGame:
    """Test complete game simulation."""

    def test_example_from_prompt(self):
        """Test the exact example from the problem prompt."""
        grid = [
            ['A', '.', '.', '.', '.'],
            ['.', '.', 'B', '.', '.'],
            ['.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', 'C']
        ]
        turn_directions = [
            {'A': 'E', 'B': 'W', 'C': 'NW'},
            {'A': 'E', 'B': 'W', 'C': 'NW'}
        ]

        final_grid = simulate_game(4, 5, 2, grid, turn_directions, verbose=False)

        # Note: C throwing NW from (3,4) actually hits B at (1,2), not A at (0,0)
        # Path: (3,4) -> (2,3) -> (1,2) where B is located
        # So the actual result is: B eliminated, A and C remain
        assert final_grid[0][0] == 'A'
        assert final_grid[1][2] == '.'  # B is eliminated
        assert final_grid[3][4] == 'C'

    def test_game_ends_with_one_player(self):
        """Test game ending when only one player remains."""
        grid = [
            ['A', '.', 'B']
        ]
        turn_directions = [
            {'A': 'E', 'B': 'N'},
            {'A': 'E'}  # This turn should not execute
        ]

        final_grid = simulate_game(1, 3, 2, grid, turn_directions, verbose=False)

        # B should be eliminated, A remains, second turn shouldn't happen
        assert final_grid[0][0] == 'A'
        assert final_grid[0][2] == '.'

    def test_all_players_eliminated(self):
        """Test scenario where all players are eliminated."""
        grid = [
            ['A', '.', 'B']
        ]
        turn_directions = [
            {'A': 'E', 'B': 'W'}
        ]

        final_grid = simulate_game(1, 3, 1, grid, turn_directions, verbose=False)

        # Both players should be eliminated
        assert final_grid[0][0] == '.'
        assert final_grid[0][2] == '.'

    def test_no_eliminations_all_turns(self):
        """Test game where no one is eliminated."""
        grid = [
            ['A', '.', '.'],
            ['.', '.', '.'],
            ['.', '.', 'B']
        ]
        turn_directions = [
            {'A': 'N', 'B': 'S'},
            {'A': 'N', 'B': 'S'}
        ]

        final_grid = simulate_game(3, 3, 2, grid, turn_directions, verbose=False)

        # Both players should remain
        assert final_grid[0][0] == 'A'
        assert final_grid[2][2] == 'B'

    def test_complex_multi_turn_scenario(self):
        """Test complex scenario with multiple turns and eliminations."""
        grid = [
            ['A', 'B', 'C', 'D']
        ]
        turn_directions = [
            {'A': 'E', 'B': 'E', 'C': 'W', 'D': 'W'},
            {'A': 'E', 'D': 'W'}
        ]

        final_grid = simulate_game(1, 4, 2, grid, turn_directions, verbose=False)

        # Turn 1: A hits B, B hits C, C hits B, D hits C
        # B and C should be eliminated
        # Turn 2: A and D shoot at each other
        assert final_grid[0][1] == '.'  # B eliminated
        assert final_grid[0][2] == '.'  # C eliminated


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_minimum_grid(self):
        """Test minimum grid size (2x2)."""
        grid = [
            ['A', 'B'],
            ['.', '.']
        ]
        turn_directions = [
            {'A': 'E', 'B': 'W'}
        ]

        final_grid = simulate_game(2, 2, 1, grid, turn_directions, verbose=False)

        assert final_grid[0][0] == '.'
        assert final_grid[0][1] == '.'

    def test_single_player_game(self):
        """Test game with single player (should end immediately)."""
        grid = [
            ['A', '.', '.']
        ]
        turn_directions = [
            {'A': 'E'},
            {'A': 'W'}
        ]

        final_grid = simulate_game(1, 3, 2, grid, turn_directions, verbose=False)

        # Game should end immediately, no turns executed
        assert final_grid[0][0] == 'A'

    def test_throws_at_grid_edges(self):
        """Test throws at the edges of the grid."""
        grid = [
            ['A', '.', '.', '.', 'B']
        ]
        turn_directions = [
            {'A': 'W', 'B': 'E'}  # Both throw away from each other
        ]

        final_grid = simulate_game(1, 5, 1, grid, turn_directions, verbose=False)

        # No one should be eliminated
        assert final_grid[0][0] == 'A'
        assert final_grid[0][4] == 'B'

    def test_diagonal_chain_elimination(self):
        """Test diagonal throws across larger grid."""
        grid = [
            ['A', '.', '.', '.'],
            ['.', '.', '.', '.'],
            ['.', '.', '.', '.'],
            ['.', '.', '.', 'B']
        ]
        turn_directions = [
            {'A': 'SE', 'B': 'NW'}
        ]

        final_grid = simulate_game(4, 4, 1, grid, turn_directions, verbose=False)

        # Both should eliminate each other
        assert final_grid[0][0] == '.'
        assert final_grid[3][3] == '.'

    def test_many_players(self):
        """Test with many players (stress test)."""
        grid = [
            ['A', 'B', 'C', 'D', 'E'],
            ['F', 'G', 'H', 'I', 'J'],
            ['K', 'L', '.', 'M', 'N']
        ]
        turn_directions = [
            {
                'A': 'E', 'B': 'E', 'C': 'E', 'D': 'E', 'E': 'W',
                'F': 'N', 'G': 'N', 'H': 'N', 'I': 'N', 'J': 'N',
                'K': 'E', 'L': 'E', 'M': 'W', 'N': 'W'
            }
        ]

        final_grid = simulate_game(3, 5, 1, grid, turn_directions, verbose=False)

        # Multiple eliminations should occur
        eliminated_count = sum(1 for row in final_grid for cell in row if cell == '.')
        assert eliminated_count > 1

    def test_empty_directions_for_turn(self):
        """Test turn with no directions provided."""
        grid = [
            ['A', '.', 'B']
        ]
        turn_directions = [
            {},  # No one throws
            {'A': 'E'}
        ]

        final_grid = simulate_game(1, 3, 2, grid, turn_directions, verbose=False)

        # First turn: no eliminations
        # Second turn: A hits B
        assert final_grid[0][0] == 'A'
        assert final_grid[0][2] == '.'


class TestIntegration:
    """Integration tests using full input/output flow."""

    def test_full_example_integration(self):
        """Test full example with parse and simulate."""
        input_text = """4 5 2
A....
..B..
.....
....C
A:E B:W C:NW
A:E B:W C:NW"""

        n, m, t, grid, turn_directions = parse_input(input_text)
        final_grid = simulate_game(n, m, t, grid, turn_directions, verbose=False)

        # Convert to string for easy comparison
        result = '\n'.join(''.join(row) for row in final_grid)
        # Actual behavior: C hits B (not A) because path from (3,4) NW goes through (1,2)
        expected = "A....\n.....\n.....\n....C"

        assert result == expected

    def test_output_format(self, capsys):
        """Test that print_grid produces correct output format."""
        grid = [
            ['.', 'A', '.'],
            ['.', '.', 'B']
        ]

        print_grid(grid)
        captured = capsys.readouterr()

        assert captured.out == ".A.\n..B\n"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
