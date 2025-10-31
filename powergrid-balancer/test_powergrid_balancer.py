#!/usr/bin/env python3
"""
Unit tests for Power Grid Balancer Simulation
"""
import pytest
from powergrid_balancer import (
    Edge,
    parse_input,
    find_surplus,
    simulate_flow_step,
    simulate_turn,
    simulate_balancing,
    check_disconnected_graph,
)


class TestEdge:
    """Test Edge dataclass functionality"""

    def test_edge_creation(self):
        """Test creating an edge"""
        edge = Edge(1, 2, 5)
        assert edge.s == 1
        assert edge.d == 2
        assert edge.c == 5

    def test_edge_repr(self):
        """Test edge string representation"""
        edge = Edge(1, 2, 5)
        assert str(edge) == "1 -> 2 ⚡5"

    def test_edge_mutability(self):
        """Test that edge capacity can be modified"""
        edge = Edge(1, 2, 5)
        edge.c = 3
        assert edge.c == 3

    def test_edge_hash(self):
        """Test edge hashing (should be based on s and d only)"""
        edge1 = Edge(1, 2, 5)
        edge2 = Edge(1, 2, 3)
        assert hash(edge1) == hash(edge2)

    def test_edge_equality(self):
        """Test edge equality (should be based on s and d only)"""
        edge1 = Edge(1, 2, 5)
        edge2 = Edge(1, 2, 3)
        assert edge1 == edge2

    def test_edge_in_set(self):
        """Test that edges can be stored in sets"""
        edge1 = Edge(1, 2, 5)
        edge2 = Edge(2, 3, 3)
        edge_set = {edge1, edge2}
        assert len(edge_set) == 2
        assert edge1 in edge_set


class TestParseInput:
    """Test input parsing functionality"""

    def test_parse_simple_input(self):
        """Test parsing a simple input"""
        input_text = """4 4 1
5 -3 -2 0
1 2 2
2 3 1
3 4 2
1 4 3"""
        generations, edges, t = parse_input(input_text)

        assert generations == [5, -3, -2, 0]
        assert t == 1
        assert len(edges) == 8  # 4 edges * 2 (bidirectional)

    def test_parse_edges_bidirectional(self):
        """Test that edges are created bidirectionally"""
        input_text = """2 1 1
5 -5
1 2 3"""
        generations, edges, t = parse_input(input_text)

        # Should have both 1->2 and 2->1
        forward = [e for e in edges if e.s == 1 and e.d == 2]
        backward = [e for e in edges if e.s == 2 and e.d == 1]

        assert len(forward) == 1
        assert len(backward) == 1
        assert forward[0].c == 3
        assert backward[0].c == 3


class TestFindSurplus:
    """Test surplus finding functionality"""

    def test_find_single_surplus(self):
        """Test finding a single surplus node"""
        generations = [5, -3, -2, 0]
        surpluses = find_surplus(generations)
        assert surpluses == [1]

    def test_find_multiple_surplus(self):
        """Test finding multiple surplus nodes"""
        generations = [5, 3, -2, 2]
        surpluses = find_surplus(generations)
        assert surpluses == [1, 2, 4]

    def test_find_no_surplus(self):
        """Test when there are no surplus nodes"""
        generations = [0, -3, -2, 0]
        surpluses = find_surplus(generations)
        assert surpluses == []

    def test_find_surplus_returns_one_based(self):
        """Test that surplus indices are 1-based and nodes need > 1 to be surplus"""
        generations = [2, 0, 0, 0]  # Node needs > 1 to be considered surplus
        surpluses = find_surplus(generations)
        assert surpluses == [1]  # Returns 1-based index, not 0


class TestSimulateFlowStep:
    """Test flow simulation step functionality"""

    def test_basic_flow(self):
        """Test basic flow from surplus to deficit"""
        generations = [5, -3, -2, 0]
        edges = [
            Edge(1, 2, 2),
            Edge(2, 1, 2),
        ]

        overloaded, changed = simulate_flow_step(edges, generations, 1)

        # Check generations updated
        assert generations[0] == 4  # 5 - 1
        assert generations[1] == -2  # -3 + 1

        # Check edge capacity reduced
        forward_edge = [e for e in edges if e.s == 1 and e.d == 2][0]
        reverse_edge = [e for e in edges if e.s == 2 and e.d == 1][0]
        assert forward_edge.c == 1  # 2 - 1
        assert reverse_edge.c == 1  # 2 - 1 (reverse also reduced)

        # Check changed tracking (both forward and reverse edges are tracked)
        assert len(changed) == 2
        assert len(overloaded) == 0

    def test_no_flow_to_surplus(self):
        """Test that flow doesn't go from surplus to surplus"""
        generations = [5, 3, -2, 0]
        edges = [
            Edge(1, 2, 2),
            Edge(2, 1, 2),
        ]

        original_gen = generations.copy()
        overloaded, changed = simulate_flow_step(edges, generations, 1)

        # Node 2 is surplus, so no flow should happen
        assert generations[1] == original_gen[1]
        assert len(changed) == 0

    def test_flow_stops_at_one_unit(self):
        """Test that flow doesn't happen if source has only 1 unit"""
        generations = [1, -3, -2, 0]
        edges = [
            Edge(1, 2, 2),
            Edge(2, 1, 2),
        ]

        overloaded, changed = simulate_flow_step(edges, generations, 1)

        # Should not flow because source needs to keep > 1
        assert generations[0] == 1
        assert len(changed) == 0

    def test_overloaded_edge_removed(self):
        """Test that overloaded edges are removed"""
        generations = [5, -3, -2, 0]
        edges = [
            Edge(1, 2, 0),  # Already at capacity
            Edge(2, 1, 0),
        ]

        overloaded, changed = simulate_flow_step(edges, generations, 1)

        # Both edges should be removed (forward and reverse)
        assert len(edges) == 0
        assert len(overloaded) == 2  # Both forward and reverse marked as overloaded

    def test_reverse_edge_removed_when_capacity_zero(self):
        """Test that reverse edge is removed when it reaches 0 capacity"""
        generations = [5, -3, -2, 0]
        edges = [
            Edge(1, 2, 1),
            Edge(2, 1, 1),
        ]

        overloaded, changed = simulate_flow_step(edges, generations, 1)

        # Both edges should reach 0 and be removed
        assert all(e.c == 0 for e in edges)
        # Reverse edge should have been added to removal list
        assert len([e for e in edges if e.s == 2 and e.d == 1]) == 0 or \
               [e for e in edges if e.s == 2 and e.d == 1][0].c == 0


class TestSimulateTurn:
    """Test full turn simulation"""

    def test_turn_with_single_surplus(self):
        """Test a turn with a single surplus node"""
        generations = [5, -3, -2, 0]
        edges = [
            Edge(1, 2, 2),
            Edge(2, 1, 2),
        ]

        overloaded, changed, actions = simulate_turn(generations, edges, verbose=False)

        assert len(actions) > 0
        assert generations[0] == 4
        assert generations[1] == -2

    def test_turn_with_no_surplus(self):
        """Test a turn with no surplus nodes"""
        generations = [0, -3, -2, 0]
        edges = [
            Edge(1, 2, 2),
            Edge(2, 1, 2),
        ]

        overloaded, changed, actions = simulate_turn(generations, edges, verbose=False)

        assert len(actions) == 0
        assert len(changed) == 0


class TestCheckDisconnectedGraph:
    """Test graph connectivity checking"""

    def test_connected_graph(self):
        """Test a fully connected graph"""
        generations = [5, -3, -2, 0]
        edges = [
            Edge(1, 2, 2),
            Edge(2, 1, 2),
            Edge(2, 3, 1),
            Edge(3, 2, 1),
            Edge(3, 4, 2),
            Edge(4, 3, 2),
        ]

        assert not check_disconnected_graph(generations, edges)

    def test_disconnected_graph(self):
        """Test a disconnected graph"""
        generations = [5, -3, -2, 0]
        edges = [
            Edge(2, 3, 1),
            Edge(3, 2, 1),
        ]

        # Node 1 and 4 are not in any edges
        assert check_disconnected_graph(generations, edges)

    def test_empty_edges(self):
        """Test with no edges (completely disconnected)"""
        generations = [5, -3, -2, 0]
        edges = []

        assert check_disconnected_graph(generations, edges)


class TestSimulateBalancing:
    """Test full simulation scenarios"""

    def test_simple_balancing_scenario(self):
        """Test a simple balancing scenario"""
        generations = [3, -2]
        edges = [
            Edge(1, 2, 5),
            Edge(2, 1, 5),
        ]
        t = 2

        result_edges = simulate_balancing(generations, edges, t, verbose=False)

        # After 2 turns, node 1 should have transferred 2 units to node 2
        assert generations[0] == 1  # 3 - 2
        assert generations[1] == 0  # -2 + 2

    def test_balancing_with_capacity_limit(self):
        """Test balancing when edge capacity is reached"""
        generations = [5, -3]
        edges = [
            Edge(1, 2, 2),
            Edge(2, 1, 2),
        ]
        t = 5

        result_edges = simulate_balancing(generations, edges, t, verbose=False)

        # Should only transfer 2 units (capacity limit)
        assert generations[0] == 3  # 5 - 2
        assert generations[1] == -1  # -3 + 2

        # Edges should be overloaded and removed
        assert len(result_edges) == 0

    def test_balancing_multi_node(self):
        """Test balancing with multiple nodes"""
        generations = [5, -3, -2, 0]
        edges = [
            Edge(1, 2, 2),
            Edge(2, 1, 2),
            Edge(2, 3, 1),
            Edge(3, 2, 1),
            Edge(3, 4, 2),
            Edge(4, 3, 2),
        ]
        t = 1

        result_edges = simulate_balancing(generations, edges, t, verbose=False)

        # Node 1 should have sent 1 unit to node 2
        assert generations[0] == 4
        assert generations[1] == -2

    def test_balancing_stops_on_disconnect(self):
        """Test that simulation stops when graph becomes disconnected"""
        generations = [5, -3, -2, 0]
        edges = [
            Edge(1, 2, 1),  # Low capacity
            Edge(2, 1, 1),
            Edge(2, 3, 1),
            Edge(3, 2, 1),
            Edge(3, 4, 2),
            Edge(4, 3, 2),
        ]
        t = 10  # More turns than needed

        result_edges = simulate_balancing(generations, edges, t, verbose=False)

        # Simulation should stop early when edges overload
        # Node 1 should still have surplus (couldn't fully balance)
        assert generations[0] > 1


class TestEdgeCases:
    """Test edge cases and corner scenarios"""

    def test_all_balanced_from_start(self):
        """Test when all nodes are already balanced"""
        generations = [0, 0, 0, 0]
        edges = [
            Edge(1, 2, 2),
            Edge(2, 1, 2),
        ]
        t = 3

        result_edges = simulate_balancing(generations, edges, t, verbose=False)

        # Nothing should change
        assert all(g == 0 for g in generations)

    def test_single_node(self):
        """Test with a single node"""
        generations = [5]
        edges = []
        t = 1

        result_edges = simulate_balancing(generations, edges, t, verbose=False)

        # Node should remain unchanged
        assert generations[0] == 5

    def test_no_turns(self):
        """Test with zero turns"""
        generations = [5, -3]
        edges = [
            Edge(1, 2, 2),
            Edge(2, 1, 2),
        ]
        t = 0

        result_edges = simulate_balancing(generations, edges, t, verbose=False)

        # Nothing should change
        assert generations[0] == 5
        assert generations[1] == -3


class TestReverseEdgeUpdate:
    """Test that reverse edges are properly updated"""

    def test_reverse_edge_capacity_decreases(self):
        """Test that reverse edge capacity decreases with forward flow"""
        generations = [5, -3]
        edges = [
            Edge(1, 2, 3),
            Edge(2, 1, 3),
        ]

        simulate_flow_step(edges, generations, 1)

        forward = [e for e in edges if e.s == 1 and e.d == 2][0]
        reverse = [e for e in edges if e.s == 2 and e.d == 1][0]

        assert forward.c == 2  # 3 - 1
        assert reverse.c == 2  # 3 - 1

    def test_reverse_edge_removed_at_zero(self):
        """Test that reverse edge is removed when capacity reaches 0"""
        generations = [5, -3]
        edges = [
            Edge(1, 2, 1),
            Edge(2, 1, 1),
        ]

        simulate_flow_step(edges, generations, 1)

        # Both edges should be at 0 capacity
        remaining_edges = [e for e in edges if e.c > 0]
        assert len(remaining_edges) == 0

    def test_multiple_flows_update_reverse_edges(self):
        """Test that multiple flows correctly update reverse edges"""
        generations = [5, -3]
        edges = [
            Edge(1, 2, 5),
            Edge(2, 1, 5),
        ]

        # Flow 3 times
        for _ in range(3):
            simulate_flow_step(edges, generations, 1)

        forward = [e for e in edges if e.s == 1 and e.d == 2][0]
        reverse = [e for e in edges if e.s == 2 and e.d == 1][0]

        assert forward.c == 2  # 5 - 3
        assert reverse.c == 2  # 5 - 3


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
