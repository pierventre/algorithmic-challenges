#!/usr/bin/env python3
from dataclasses import dataclass
"""
Power Grid Balancer Simulation
Cities consume and produce electricity, and a control node balances flows to prevent blackouts.
"""

@dataclass
class Edge:
    """Represents an edge from s to d and with c capacity"""
    s: int  # source
    d: int  # destination
    c: int  # capacity

    def __repr__(self):
        return f"{self.s} -> {self.d} ⚡{self.c}"

    def __hash__(self):
        # Only hash based on source and destination (immutable attributes)
        return hash((self.s, self.d))

    def __eq__(self, other):
        # Two edges are equal if they have the same source and destination
        if not isinstance(other, Edge):
            return False
        return self.s == other.s and self.d == other.d

def parse_input(input_text):

    """Parse the input and return grid dimensions, turns, nodes, flows, edges and capcity."""
    lines = input_text.strip().split('\n')

    # Parse first line: N M T
    n, m, t = map(int, lines[0].split())

    # Parse second line: nodes generation
    generations = list(map(int, lines[1].split()))

    # Parse edges (next M lines)
    edges = []
    for i in range(2, m + 2):
        src, dst, cap = map(int, lines[i].split())
        edges.append(Edge(src, dst, cap))
        edges.append(Edge(dst, src, cap))

    return generations, edges, t

def find_surplus(generations):
    """Find all surplus cities and return their indices (1-based to match edge node numbers)."""
    surplus = []
    for idx, generation in enumerate(generations):
        if generation > 1:
            surplus.append(idx + 1)  # Convert to 1-based indexing
    return surplus

def simulate_flow_step(edges, generations, source):
    """
    Simulate a flow step where a unit of capacity is moved from a src to dst.
    Returned overloaded links and wheter or not there were changes
    """
    overloaded = set()
    changed = set()
    edges_to_remove = []
    for edge in edges:
        # Found a candidate link
        if edge.s == source:
            destination = edge.d
            # Move only if it makes sense: neutral or negative flow at dst
            # Convert 1-based node numbers to 0-based array indices
            if generations[source - 1] > 1 and generations[destination - 1] <= 0:
                if edge.c > 0:
                    # Update remaining capacity and energy values
                    edge.c = edge.c - 1
                    generations[source - 1] = generations[source - 1] - 1
                    generations[destination - 1] = generations[destination - 1] + 1
                    changed.add(edge)

                    # Find and update the reverse edge
                    for reverse_edge in edges:
                        if reverse_edge.s == destination and reverse_edge.d == source:
                            reverse_edge.c = reverse_edge.c - 1
                            changed.add(reverse_edge)
                else:
                    # Mark overloaded link for removal
                    overloaded.add(edge)
                    edges_to_remove.append(edge)
                    reverse_edge = Edge(edge.d, edge.s, edge.c)
                    edges_to_remove.append(reverse_edge)
                    overloaded.add(reverse_edge)
    for edge in edges_to_remove:
        edges.remove(edge)
    return overloaded, changed

def simulate_turn(generations, edges, verbose=False):
    """
    Simulate one turn of the simulation.
    Returns the set of the links overloaded and links changed in this turn and action details.
    """
    surpluses = sorted(find_surplus(generations))
    overloaded = set()
    changed = set()
    actions = []

    if len(surpluses) == 0:
        return overloaded, changed, actions

    for surplus in surpluses:
        action = None
        overloaded_links, changed_links = simulate_flow_step(edges, generations, surplus)

        if len(overloaded_links) > 0:
            overloaded.update(overloaded_links)
            action = "Overloaded links: " + ', '.join(map(str, overloaded_links))

        if len(changed_links) > 0:
            changed.update(changed_links)
            changed_link = ', '.join(map(str, changed_links))
            if action:
                action = f"{action} and moved 1u {changed_link}"
            else:
                action = f"Moved 1u {changed_link}"

        if action:
            actions.append(action)

    return overloaded, changed, actions

def check_disconnected_graph(generations, edges):
    """Verify if the graph got disconnected because of the overloading"""
    visited = set()
    for edge in edges:
        visited.add(edge.s)
        visited.add(edge.d)

    return len(visited) != len(generations)

def simulate_balancing(generations, edges, t, verbose=True):
    """Run the complete dalanrone swarm coordination simulation."""
    if verbose:
        print("=" * 60)
        print("INITIAL Network State")
        print("=" * 60)
        print_graph(generations, edges)
        surpluses = find_surplus(generations)
        print(f"\nSurpluses: {', '.join(sorted(map(str, surpluses)))}")
        print()

    overloaded = set()
    changed = set()
    for turn_idx in range(t):
        if check_disconnected_graph(generations, edges):
            if verbose:
                print(f"Graph disconnected due to overloaded links. Ending simulation.")
                print()
            break
        if verbose:
            print("=" * 60)
            print(f"TURN {turn_idx + 1}")
            print("=" * 60)

        # Simulate this turn
        overloaded_links, changed_links, actions = simulate_turn(generations, edges, verbose)

        if len(changed_links) == 0:
            if verbose:
                print("No more possible changes. Ending simulation.")
                print()
            break

        # Print actions
        if verbose:
            for action in actions:
                print(f"  {action}")

        overloaded.update(overloaded_links)
        changed.update(changed_links)


        if verbose:
            print("\nNetwork State after turn:")
            print_graph(generations, edges)
            surpluses = find_surplus(generations)
            print(f"\nSurpluses: {', '.join(sorted(map(str, surpluses)))}")
            print()

    if verbose:
        print("=" * 60)
        print("FINAL Network STATE")
        print("=" * 60)
        print_graph(generations, edges)
        surpluses = find_surplus(generations)
        if len(surpluses) == 0:
            print("\nNo surpluses!")
        else:
            print(f"\nRemaining surpluses: {', '.join(sorted(map(str, surpluses)))}")
        print(f"\nOverloaded links: {', '.join(map(str, overloaded))}")
        print(f"\nChanged links: {', '.join(map(str, changed))}")
        print("=" * 60)
    else:
        print_graph(generations, edges)
    
    return edges


def print_graph(generations, edges):
    """Print the graph state: node generations and edges with capacities."""
    print("Nodes (index: generation):")
    for idx, gen in enumerate(generations, start=1):
        # show sign for clarity (+ producer, - consumer, 0 neutral)
        print(f"  {idx}: {gen:+d}")

    print("\nEdges (u -> v ⚡capacity):")
    if not edges:
        print("  (none)")
        return

    for edge in edges:
        print(f"  {edge}")


def main():
    """Main entry point."""
    import sys

    # Check for verbose flag
    verbose = '--verbose' in sys.argv or '-v' in sys.argv

    # Read all input
    input_text = sys.stdin.read()

    # Parse input
    generations, edges, t = parse_input(input_text)

    # Simulate scenario
    simulate_balancing(generations, edges, t, verbose=verbose)

if __name__ == '__main__':
    main()
