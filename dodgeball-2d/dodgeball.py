#!/usr/bin/env python3
"""
Dodgeball 2D Simulation
Simulates a turn-based dodgeball game on a 2D grid.
"""

def parse_input(input_text):
    """Parse the input and return grid dimensions, turns, grid, and directions."""
    lines = input_text.strip().split('\n')

    # Parse first line: N M T
    n, m, t = map(int, lines[0].split())

    # Parse grid (next N lines)
    grid = []
    for i in range(1, n + 1):
        grid.append(list(lines[i]))

    # Parse turn directions (next T lines)
    turn_directions = []
    for i in range(n + 1, n + 1 + t):
        directions = {}
        if i < len(lines):
            pairs = lines[i].split()
            for pair in pairs:
                player, direction = pair.split(':')
                directions[player] = direction
        turn_directions.append(directions)

    return n, m, t, grid, turn_directions


def get_direction_vector(direction):
    """Convert direction string to (row_delta, col_delta)."""
    direction_map = {
        'N': (-1, 0),
        'NE': (-1, 1),
        'E': (0, 1),
        'SE': (1, 1),
        'S': (1, 0),
        'SW': (1, -1),
        'W': (0, -1),
        'NW': (-1, -1)
    }
    return direction_map[direction]


def find_players(grid):
    """Find all active players on the grid and return their positions."""
    players = {}
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] != '.':
                players[grid[r][c]] = (r, c)
    return players


def simulate_throw(grid, start_pos, direction, thrower):
    """
    Simulate a ball thrown from start_pos in the given direction.
    Returns the player hit (if any), or None.
    """
    n, m = len(grid), len(grid[0])
    dr, dc = get_direction_vector(direction)
    r, c = start_pos

    # Move in the direction until hitting a player or edge
    r += dr
    c += dc

    while 0 <= r < n and 0 <= c < m:
        if grid[r][c] != '.' and grid[r][c] != thrower:
            # Hit a player
            return grid[r][c]
        r += dr
        c += dc

    # Reached edge without hitting anyone
    return None


def simulate_turn(grid, directions, verbose=False):
    """
    Simulate one turn of the game.
    Returns the set of players eliminated this turn and action details.
    """
    players = find_players(grid)
    eliminated = set()
    actions = []

    # Get active players in alphabetical order
    active_players = sorted(players.keys())

    # Process all throws simultaneously
    for player in active_players:
        if player in directions:
            direction = directions[player]
            pos = players[player]
            hit_player = simulate_throw(grid, pos, direction, player)
            actions.append({
                'player': player,
                'position': pos,
                'direction': direction,
                'hit': hit_player
            })
            if hit_player:
                eliminated.add(hit_player)

    return eliminated, actions


def remove_players(grid, eliminated):
    """Remove eliminated players from the grid."""
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] in eliminated:
                grid[r][c] = '.'


def count_active_players(grid):
    """Count the number of active players on the grid."""
    count = 0
    for row in grid:
        for cell in row:
            if cell != '.':
                count += 1
    return count


def simulate_game(n, m, t, grid, turn_directions, verbose=True):
    """Run the complete dodgeball simulation."""
    if verbose:
        print("=" * 60)
        print("INITIAL GRID")
        print("=" * 60)
        print_grid(grid)
        players = find_players(grid)
        print(f"\nActive players: {', '.join(sorted(players.keys()))}")
        print()

    for turn_idx in range(t):
        # Check if game should end (1 or fewer players remain)
        if count_active_players(grid) <= 1:
            if verbose:
                print(f"Game ended early: only {count_active_players(grid)} player(s) remaining")
                print()
            break

        if verbose:
            print("=" * 60)
            print(f"TURN {turn_idx + 1}")
            print("=" * 60)

        # Simulate this turn
        eliminated, actions = simulate_turn(grid, turn_directions[turn_idx])

        # Print actions
        if verbose:
            for action in actions:
                hit_msg = f"→ HIT {action['hit']}!" if action['hit'] else "→ miss"
                print(f"  {action['player']} at {action['position']} throws {action['direction']} {hit_msg}")

            if eliminated:
                print(f"\n  Eliminated: {', '.join(sorted(eliminated))}")
            else:
                print(f"\n  No eliminations this turn")

        # Remove eliminated players
        remove_players(grid, eliminated)

        if verbose:
            print("\nGrid after turn:")
            print_grid(grid)
            players = find_players(grid)
            print(f"Active players: {', '.join(sorted(players.keys())) if players else 'None'}")
            print()

    if verbose:
        print("=" * 60)
        print("FINAL GRID")
        print("=" * 60)
        print_grid(grid)
        players = find_players(grid)
        if len(players) == 1:
            winner = list(players.keys())[0]
            print(f"\nWinner: {winner}")
        elif len(players) == 0:
            print("\nNo survivors!")
        else:
            print(f"\nRemaining players: {', '.join(sorted(players.keys()))}")
        print("=" * 60)
    else:
        print_grid(grid)

    return grid


def print_grid(grid):
    """Print the grid state."""
    for row in grid:
        print(''.join(row))


def main():
    """Main entry point."""
    import sys

    # Check for flags
    verbose = True
    args = sys.argv[1:]

    if '--quiet' in args or '-q' in args:
        verbose = False
        args = [arg for arg in args if arg not in ['--quiet', '-q']]

    # Read input from file if provided, otherwise from stdin
    if len(args) > 0:
        input_file = args[0]
        with open(input_file, 'r') as f:
            input_text = f.read()
    else:
        input_text = sys.stdin.read()

    # Parse input
    n, m, t, grid, turn_directions = parse_input(input_text)

    # Simulate game
    simulate_game(n, m, t, grid, turn_directions, verbose=verbose)


if __name__ == '__main__':
    main()
