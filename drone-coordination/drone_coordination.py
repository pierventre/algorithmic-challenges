#!/usr/bin/env python3
"""
Drone Swarm Coordination Simulation
Autonomous drones move in a shared airspace grid, avoiding collisions and completing deliveries.
"""

def check_drone_not_allowed(drone_id):
    """Check if a drone is not allowed."""
    if drone_id in ['X', 'O', '.']:
        raise ValueError("Drone ID cannot be X, O, or .")

def parse_input(input_text):

    """Parse the input and return grid dimensions, turns, grid, and directions."""
    lines = input_text.strip().split('\n')

    # Parse first line: N T
    n, t = map(int, lines[0].split())

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
                drone, direction = pair.split(':')
                check_drone_not_allowed(drone)
                directions[drone] = direction
        turn_directions.append(directions)

    return n, t, grid, turn_directions


def get_direction_vector(direction):
    """Convert direction string to (row_delta, col_delta)."""
    direction_map = {
        'N': (-1, 0),
        'E': (0, 1),
        'S': (1, 0),
        'W': (0, -1),
    }
    return direction_map[direction]


def find_drones(grid):
    """Find all active drones on the grid and return their positions."""
    drones = {}
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] != '.' and grid[r][c] != 'X' and grid[r][c] != 'O':
                drones[grid[r][c]] = (r, c)
    return drones


def simulate_move(grid, start_pos, direction, drone):
    """
    Simulate a drone move from start_pos in the given direction.
    Returns new drones position (if any), or None.
    """
    n, m = len(grid), len(grid[0])
    dr, dc = get_direction_vector(direction)
    r, c = start_pos

    # Move in the direction
    r += dr
    c += dc

    if 0 <= r < n and 0 <= c < m:
        if grid[r][c] == '.':
            return (r, c)
        elif grid[r][c] == 'O':
            return (r, c)
        # Obstacle means no move
        elif grid[r][c] == 'X':
            return None
        # Hit another drone
        else:
            return (r, c)

    # Reached edge without hitting anyone
    return None


def simulate_turn(grid, directions, verbose=False):
    """
    Simulate one turn of the game.
    Returns the set of players eliminated this turn and action details.
    """
    delivered_packages = 0
    drones = find_drones(grid)
    crashed = set()
    actions = []

    # Get active drones in alphabetical order
    active_drones = sorted(drones.keys())

    # Process all throws simultaneously
    for drone in active_drones:
        if drone in directions:
            direction = directions[drone]
            pos = drones[drone]
            new_pos = simulate_move(grid, pos, direction, drone)
            if new_pos is not None:
                old_r, old_c = pos
                r, c = new_pos
                # Update delivery and make effective the new position
                if grid[r][c] == 'O':
                    delivered_packages = delivered_packages + 1
                    grid[r][c] = drone
                    actions.append({
                        'drone': drone,
                        'position': pos,
                        'direction': direction,
                        'action': f"{drone} delivered at {new_pos}"
                    })
                # Make effective the new position
                elif grid[r][c] == '.':
                    grid[r][c] = drone
                    actions.append({
                        'drone': drone,
                        'position': pos,
                        'direction': direction,
                        'action': f"{drone} moved at {new_pos}"
                    })
                # Update the crashed drones and cleanup the grid
                else:
                    crashed_drone = grid[r][c]
                    crashed.add(drone)
                    crashed.add(crashed_drone)
                    grid[r][c] = '.'
                    actions.append({
                        'drone': drone,
                        'position': pos,
                        'direction': direction,
                        'action': f"{drone} and {crashed_drone} crashed at {new_pos}"
                    })
                grid[old_r][old_c] = '.'
            else:
                actions.append({
                    'drone': drone,
                    'position': pos,
                    'direction': direction,
                    'action': f"{drone} stuck at {pos}"
                })

    return crashed, delivered_packages, actions

def count_active_drones(grid):
    """Count the number of active players on the grid."""
    count = 0
    for row in grid:
        for cell in row:
            if cell != '.' and cell != 'X' and cell != 'O':
                count += 1
    return count

def simulate_coordination(n, t, grid, turn_directions, verbose=True):
    """Run the complete drone swarm coordination simulation."""
    if verbose:
        print("=" * 60)
        print("INITIAL GRID")
        print("=" * 60)
        print_grid(grid)
        drones = find_drones(grid)
        print(f"\nActive Drones: {', '.join(sorted(drones.keys()))}")
        print()

    delivered_packages = 0
    crashed_drones = set()
    for turn_idx in range(t):
        # Check if simulation should end (0 drones or all packages delivered)
        active_drones = count_active_drones(grid)
        if active_drones <= 0 or delivered_packages == active_drones:
            if verbose:
                print(f"Game ended early: only {active_drones} drone(s) remaining or all packages delivered.")
                print()
            break

        if verbose:
            print("=" * 60)
            print(f"TURN {turn_idx + 1}")
            print("=" * 60)

        # Simulate this turn
        crashed, delivered, actions = simulate_turn(grid, turn_directions[turn_idx])

        # Print actions
        if verbose:
            for action in actions:
                print(f"  {action['action']}")

            if crashed:
                print(f"\n  Crashed: {', '.join(sorted(crashed))}")
            else:
                print(f"\n  No crash this turn")
            
            if delivered > 0:
                print(f"\n Delivered {delivered} packages")
            else:
                print(f"\n  No packages delivered this turn")
        
        delivered_packages = delivered_packages + delivered
        crashed_drones.update(crashed)

        if verbose:
            print("\nGrid after turn:")
            print_grid(grid)
            drones = find_drones(grid)
            print(f"Active drones: {', '.join(sorted(drones.keys())) if drones else 'None'}")
            print()

    if verbose:
        print("=" * 60)
        print("FINAL GRID")
        print("=" * 60)
        print_grid(grid)
        if delivered_packages > 0:
            print(f"\nDelivered: {delivered_packages} packages")
        drones = find_drones(grid)
        if len(drones) == 0:
            print("\nNo survivors!")
        else:
            print(f"\nRemaining drones: {', '.join(sorted(drones.keys()))}")
        print(f"\nCrashed drones: {', '.join(crashed_drones)}")
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

    # Check for verbose flag
    verbose = '--verbose' in sys.argv or '-v' in sys.argv

    # Read all input
    input_text = sys.stdin.read()

    # Parse input
    n, t, grid, turn_directions = parse_input(input_text)

    # Simulate scenario
    simulate_coordination(n, t, grid, turn_directions, verbose=verbose)


if __name__ == '__main__':
    main()
