# 🧩 Coding Challenge — Dodgeball

## 🧠 Problem Description
You are asked to simulate a **turn-based dodgeball game** on a 2D grid.  

Each cell of the grid may contain:
- a **player**, represented by a unique uppercase letter (`A`, `B`, `C`, …), or  
- be **empty**, represented by a dot (`.`).  

At each turn, **every remaining player** throws a ball in one of the **eight compass directions**:

```
N, NE, E, SE, S, SW, W, NW
```

A thrown ball travels in a straight line, one cell at a time, until:
- it **hits another player**, in which case that player is immediately **eliminated**, or  
- it reaches the **edge of the grid** (and disappears).  

All throws occur **simultaneously**.  
Eliminated players are removed from the grid at the **end of the turn** and no longer act in subsequent turns.  

The game ends when:
- only **one player remains**, or  
- the game reaches the **maximum number of turns**, whichever comes first.  

At the end of the simulation, output the **final state of the grid**.

---

## ⚙️ Game Rules Summary
- Players throw simultaneously each turn.  
- Balls stop at the first player hit or the grid boundary.  
- Eliminations take effect after all throws in the current turn are resolved.  
- No ball-to-ball collisions are considered.  
- Players do not move between turns.  

---

## 🧾 Input Format
```
N M T
<row_1>
<row_2>
...
<row_N>
<turn_1_directions>
<turn_2_directions>
...
<turn_T_directions>
```

Where:
- `N`, `M` are integers — number of rows and columns.  
- `T` is the number of turns to simulate.  
- Each `<row_i>` is a string of length `M` representing the initial grid.  
- Each `<turn_k_directions>` line lists the throw direction of each **active player**, in **alphabetical order**, as key–value pairs separated by spaces.  
  Example:  
  ```
  A:E B:W C:NW
  ```

---

## 📤 Output Format
After simulating the game, print the final grid as `N` lines of text.  
Eliminated players are replaced by `.`.  

---

## 💡 Example

### Input
```
4 5 2
A....
..B..
.....
....C
A:E B:W C:NW
A:E B:W C:NW
```

### Step-by-step Explanation
**Turn 1**  
- A throws east → travels right until edge.  
- B throws west → travels left until edge.  
- C throws northwest → path (3,3) → (2,2) → (1,1) → (0,0).  
- C’s ball hits A at (0,0).  
→ A is eliminated at end of turn.  

**Turn 2**  
- Remaining players: B, C  
- B throws west → misses.  
- C throws northwest → travels until edge, no hit.  

Game ends after 2 turns.  

### Output
```
.....
..B..
.....
....C
```

---

## ⏱️ Constraints
- `2 ≤ N, M ≤ 50`
- `1 ≤ T ≤ 100`
- Players ≤ 26 (A–Z)
- Simulation should complete within 2 seconds  

---

## 🧩 Task
Implement a program that performs the simulation as described and outputs the final grid state.
