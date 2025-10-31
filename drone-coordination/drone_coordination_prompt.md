# 🛰️ Drone Swarm Coordination Challenge

## Overview

You are simulating a **swarm of autonomous drones** navigating a 2D grid.  
Each drone moves according to directional commands, delivers packages to target cells, and must **avoid collisions** and **stay within the grid boundaries**.

The simulation runs for a fixed number of turns.  
Your task is to process each time step, update drone positions, handle deliveries and crashes, and output the final statistics.

---

## 🧩 Input Format

1. The first line contains two integers:

N T

- `N` — number of rows in the grid  
- `T` — number of turns in the simulation

2. The next `N` lines each contain a string of length `N`, describing the initial grid:
   - `.` = empty cell  
   - `X` = obstacle  
   - `A`, `B`, `C`, ... = drones (each represented by a unique uppercase letter)
   - `O` = delivery target for a drone

3. The next `T` lines describe movement commands per turn, formatted as:

A:N B:E C:S

Each `<Drone>:<Direction>` pair specifies a direction:
- `N`, `S`, `E`, `W` — move one cell north, south, east, or west.
- Directions may be missing for some drones (they remain stationary).

---

## ⚙️ Rules

- **Simultaneous movement**: All drones move at the same time each turn.
- **Boundaries**: Drones cannot move outside the grid.
- **Obstacles**: Drones cannot enter a cell containing `X`.
- **Collisions**:
  - If multiple drones move into the same cell → **all crash** (removed from grid).
  - If a drone moves into a cell occupied by another drone that hasn’t moved yet → both crash.
- **Delivery**:
  - A drone that moves onto its target cell (e.g., `A` onto `O`) **completes its delivery**.
- The simulation ends either after `T` turns or when all drones are gone or all deliveries done.

---

## 🧮 Output Format

At the end of the simulation, print:

<completed_deliveries> <crashed_drones> <remaining_drones>


- `<completed_deliveries>` — number of drones that successfully reached their target  
- `<crashed_drones>` — number of drones destroyed in collisions  
- `<remaining_drones>` — number of drones still active on the grid

Then, print the final grid state.

---

## 🧠 Example

### Input

4 3
AX.O
..B.
.OX.
O.XC
A:E B:W C:N
A:E B:W C:N
A:S B:W C:N
