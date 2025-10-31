# 🧮 Market Maker Simulation

### Problem Overview
You are implementing a **simplified market-making engine** that operates on a sequence of time steps.  
At each step, new **buy and sell orders** arrive, and your market maker places **quotes** to provide liquidity.  
Your goal is to **simulate the market**, track your **inventory** and **cash**, and report your **final profit**.

---

## 📋 Rules and Mechanics

### 1. Orders
Each order has:
- **type**: `'B'` (buy) or `'S'` (sell)
- **price**: integer (1 ≤ price ≤ 1000)
- **quantity**: integer (1 ≤ qty ≤ 100)

Orders are processed **in order of arrival**.

### 2. Order Matching
The market maintains an **order book**:
- **Buy book**: sorted descending by price (highest first)
- **Sell book**: sorted ascending by price (lowest first)

When a new order arrives:
- If it’s a **buy order**, it matches against the **best (lowest-price) sell orders** until either side is exhausted.
- If it’s a **sell order**, it matches against the **best (highest-price) buy orders** similarly.

Any remaining unfilled portion stays in the book for future steps.

---

### 3. Market Maker Quotes
Your market maker acts as a participant with its own **quote strategy**.  
At the **start of each time step**, before processing new orders:
- The market maker may **place one buy quote** and **one sell quote** (each with price and quantity).
- These quotes participate in matching **alongside** the incoming orders.

All trades that execute against the market maker update:
- **Cash balance**
- **Inventory**

Example:
- Market maker quote: buy 10 units @ 99  
- Incoming sell order: 5 units @ 98 → executed immediately  
→ Inventory +5, Cash -490.

---

### 4. Profit and Inventory Cost
At the end of all time steps:
- **Unrealized value** is not marked to market — inventory is valued at 0.
- Each time step, the market maker pays a **holding cost `C` per unit of inventory** (absolute value).

Final profit is:
```
Profit = Cash - (C × total_inventory_units_held_over_time)
```

---

### 5. Input Format

```
T C
n₁
type₁ price₁ qty₁
...
typeₙ₁ priceₙ₁ qtyₙ₁
n₂
type₁ price₁ qty₁
...
typeₙ₂ priceₙ₂ qtyₙ₂
...
```

- `T` = number of time steps
- `C` = inventory holding cost per unit per time step
- For each time step `i`, first an integer `nᵢ` (number of orders), followed by `nᵢ` lines of orders.

---

### 6. Output Format

Print:
```
Final Cash: X
Final Inventory: Y
Profit: Z
```

Optionally, print logs of trades for debugging:
```
Step 1: BUY 10 @ 99, SELL 10 @ 101
Executed 5 @ 100 → +500 cash, -5 inventory
```

---

## 💡 Example

**Input**
```
3 2
2
B 99 5
S 101 5
1
S 100 3
1
B 102 4
```

**Output**
```
Final Cash: 388
Final Inventory: 1
Profit: 386
```

*(Exact numbers may vary depending on quote logic.)*

---

## ⚙️ Requirements

Implement a function or main program to:
- Parse input from stdin
- Maintain buy/sell books efficiently (heaps or sorted structures)
- Simulate trades per time step
- Apply your market maker’s quote strategy (you may hard-code a simple one, e.g. bid=best_bid−1, ask=best_ask+1)
- Track cash, inventory, and profit
- Print final results

---

## 🧠 Bonus Extensions
- Support multiple market makers
- Include mark-to-market valuation (unrealized P&L)
- Introduce random order cancellations
- Optimize for time complexity: aim for `O(N log N)` total with appropriate data structures.

---

## 🎯 Evaluation Focus
- Correctness of trade simulation and book updates  
- Clean, modular code structure  
- Efficiency for up to 10⁵ orders  
- Readable output and adherence to format

---

**Good luck, trader. Make the market — and don’t get caught short!**
