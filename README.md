# Algorithmic Challenges

A collection of complex algorithmic challenges focusing on simulation, optimization, and game theory. Each challenge involves multi-step logic, state management, and efficient data structure usage.

## Challenges

### 1. Dodgeball 2D
**Directory:** `dodgeball-2d/`

Turn-based dodgeball simulation on a 2D grid where players throw balls simultaneously in eight compass directions.

**Key Concepts:**
- Grid-based simulation
- Simultaneous action resolution
- Collision detection along rays
- State management across turns

**Files:**
- `dodgeball.py` - Main simulation implementation
- `test_dodgeball.py` - Test suite
- `dodgeball_prompt.md` - Full problem specification

**Run:**
```bash
cd dodgeball-2d
python dodgeball.py < input.txt
python -m pytest test_dodgeball.py
```

---

### 2. Market Maker Simulation
**Directory:** `market-maker/`

Simplified market-making engine that processes buy/sell orders and manages inventory, cash flow, and profit.

**Key Concepts:**
- Order book management (bid/ask)
- Trade matching algorithms
- Inventory and P&L tracking
- Holding cost optimization

**Files:**
- `market_maker.py` - Market simulation engine
- `test_market_maker.py` - Test suite
- `market_maker_prompt.md` - Full problem specification
- `README.md` - Additional documentation

**Run:**
```bash
cd market-maker
python market_maker.py < input.txt
python -m pytest test_market_maker.py
```

---

### 3. Drone Coordination
**Directory:** `drone-coordination/`

Autonomous drone swarm navigation with collision avoidance, obstacle handling, and package delivery.

**Key Concepts:**
- Multi-agent pathfinding
- Collision detection
- Simultaneous movement resolution
- Grid-based navigation

**Files:**
- `drone_coordination.py` - Drone simulation logic
- `main.py` - Entry point
- `test_drone_coordination.py` - Test suite
- `drone_coordination_prompt.md` - Full problem specification
- `README.md` - Additional documentation

**Run:**
```bash
cd drone-coordination
python main.py < input.txt
python -m pytest test_drone_coordination.py
```

---

### 4. Power Grid Balancer
**Directory:** `powergrid-balancer/`

Power grid simulation managing energy flow between producer and consumer cities with transmission line capacity constraints.

**Key Concepts:**
- Network flow simulation
- Graph connectivity analysis
- Capacity-constrained routing
- System stabilization detection

**Files:**
- `powergrid_balancer.py` - Grid balancing implementation
- `main.py` - Entry point with CLI support
- `test_powergrid_balancer.py` - Test suite
- `power_grid_balancer.md` - Full problem specification
- `README.md` - Additional documentation

**Run:**
```bash
cd powergrid-balancer
python main.py < input.txt
python main.py --verbose < input.txt  # Detailed output
python -m pytest test_powergrid_balancer.py
```

---

## Setup

### Prerequisites
- Python 3.8+
- pip

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd algorithmic-challenges

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Running Tests

Each challenge includes a comprehensive test suite. The project is configured to run all tests from the root directory:

```bash
# Run all tests across all challenges
pytest

# Run tests for a specific challenge
pytest dodgeball-2d/
pytest market-maker/
pytest drone-coordination/
pytest powergrid-balancer/

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov
```

## Challenge Characteristics

| Challenge | Difficulty | Key Data Structures | Time Complexity |
|-----------|-----------|---------------------|-----------------|
| Dodgeball 2D | Medium | Grid, Set | O(P�T) per turn |
| Market Maker | Hard | Heap, OrderedDict | O(N log N) |
| Drone Coordination | Medium | Grid, HashMap | O(D�T) |
| Power Grid Balancer | Hard | Graph, BFS/DFS | O(N�M�T) |

**Legend:**
- P = number of players
- T = number of turns
- N = number of orders/nodes
- M = number of edges
- D = number of drones

## Project Structure

This is a standardized Python monorepo with each challenge as an independent project:

```
algorithmic-challenges/
├── README.md                      # Project overview
├── LICENSE                        # Project license
├── pyproject.toml                 # Workspace configuration
├── requirements.txt               # Shared dependencies
├── .gitignore                     # Git ignore rules
│
├── dodgeball-2d/
│   ├── pyproject.toml            # Project metadata
│   ├── dodgeball.py              # Implementation
│   ├── test_dodgeball.py         # Tests
│   └── dodgeball_prompt.md       # Problem specification
│
├── market-maker/
│   ├── pyproject.toml
│   ├── market_maker.py
│   ├── test_market_maker.py
│   ├── market_maker_prompt.md
│   └── README.md
│
├── drone-coordination/
│   ├── pyproject.toml
│   ├── drone_coordination.py
│   ├── main.py
│   ├── test_drone_coordination.py
│   ├── drone_coordination_prompt.md
│   └── README.md
│
└── powergrid-balancer/
    ├── pyproject.toml
    ├── powergrid_balancer.py
    ├── main.py
    ├── test_powergrid_balancer.py
    ├── power_grid_balancer.md
    └── README.md
```

## Learning Objectives

These challenges help develop skills in:

- **Algorithm Design:** Greedy algorithms, graph algorithms, simulation logic
- **Data Structures:** Heaps, graphs, grids, hash maps
- **Complexity Analysis:** Time/space optimization for large inputs
- **State Management:** Tracking complex state across simulation steps
- **Testing:** Writing comprehensive test suites with edge cases
- **Clean Code:** Modular design, clear documentation, type hints

## Contributing

Feel free to:
- Add new test cases
- Optimize existing solutions
- Add alternative implementations
- Improve documentation

## License

This project is for educational purposes.
