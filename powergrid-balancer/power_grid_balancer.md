# ⚡ Power Grid Balancer

### Description
You are simulating a simplified **power grid balancing system**.  
Cities are connected by power lines that transmit discrete units of energy per turn.  
Some cities generate electricity (positive values), others consume it (negative values).

Each time step, energy flows **from surplus nodes to deficit nodes** along the network edges, up to the capacity limits of each transmission line.  
If any line exceeds its instantaneous capacity, it **fails** and is removed from the network.

The simulation continues until:
1. The system stabilizes (no power movements),
2. The grid becomes disconnected, or
3. A maximum number of turns `T` is reached.

Your task is to compute the **total unmet demand** (sum of remaining deficits) once the system stops.

---

## Input Format
```
N M T
g1 g2 ... gN
u1 v1 c1
u2 v2 c2
...
uM vM cM
```

- `N`: number of cities (nodes)  
- `M`: number of transmission lines (edges)  
- `T`: maximum number of simulation steps  
- `gi`: net generation of city `i` (positive = producer, negative = consumer)  
- Each of the next `M` lines defines an **undirected** line between cities `ui` and `vi` with capacity `ci`.

All indices `ui` and `vi` are 1-based (1..N).

---

## Simulation Rules
At each time step:

1. For each **surplus city** (`gi > 0`):
   - It attempts to send up to **1 unit of power** along each connected edge toward any neighbor that has a deficit.
   - Each edge can carry **multiple units** in total during a step (summing flows from both directions and from both endpoints), but if the **total instantaneous flow** on an edge exceeds its `capacity`, that edge **fails** and is removed **after** the step.
2. For each **deficit city** (`gi < 0`):
   - It receives incoming power units until its deficit is reduced to zero.
3. After all flows for the step are computed:
   - Update each city’s generation `gi` by subtracting units sent and adding units received.
   - Remove failed edges from the graph.
4. Stop the simulation if:
   - No power moved in the last step (stabilized), or
   - The graph becomes disconnected (i.e., some nodes cannot reach others), or
   - The number of turns reaches `T`.

Notes:
- Flows are **integer units**.
- Edges are **bidirectional**; flows may occur in both directions in the same step but both contribute to the instantaneous flow used to check capacity.
- Use a deterministic rule to decide which surplus sends to which deficit when multiple candidates exist (e.g., iterate nodes in increasing index order and for each neighbor in increasing index order). The scoring will accept any deterministic tie-breaker; state it in comments if needed.
- `T` acts as a safety cap to prevent infinite loops.

---

## Output Format
Print a single line:
```
Unmet demand: X
```
Where `X` is the sum of remaining negative values across all cities after the simulation stops.

If `--verbose` is provided as a command-line flag, additionally print per-turn diagnostics:
- Turn header (e.g., `=== TURN 1 ===`)
- Flow on each edge for that turn (e.g., `Flow 1->2: 1, Flow 2->1: 0`)
- Edges removed due to overload
- Remaining generation list after the step

---

## Example

**Input:**
```
4 4 10
5 -3 -2 0
1 2 2
2 3 1
3 4 2
1 4 3
```

**Verbose (abridged):**
```
=== TURN 1 ===
Flow 1->2: 1
Flow 1->4: 1
Flow 4->3: 1
No overloads this turn.
Remaining generations: [3, -2, -1, 0]

=== TURN 2 ===
Flow 1->2: 1
Flow 1->4: 1
Flow 4->3: 1
No overloads this turn.
Remaining generations: [1, -1, 0, 0]

=== TURN 3 ===
Flow 1->2: 1
No overloads this turn.
Remaining generations: [0, 0, 0, 0]
System stabilized.
```

**Output:**
```
Unmet demand: 0
```

---

## Implementation guidance & evaluation focus
- Implement as a command-line program reading stdin and printing stdout. Accept an optional `--verbose` flag.
- Use deterministic, reproducible tie-breaking rules for selecting edges/nodes (e.g., iterate node indices ascending, neighbors ascending).
- Efficient implementation expected: with `N` up to several thousands and `M` up to ~10⁵, aim for reasonable per-step complexity—however, correctness and determinism are prioritized for this challenge.
- Provide clear comments explaining tie-breaking and any assumptions.
- The simulation must adhere to integer flows and the discrete 1-unit-per-edge rule as described.

---

## Bonus extensions (optional)
- Add edge deterioration over multiple overloaded steps rather than instant failure.
- Allow nodes to have limited storage/buffers.
- Weighted routing where surplus prefers shortest-path deficits.
- Visualize the grid/graph per step in verbose mode.

---

**End of prompt**
