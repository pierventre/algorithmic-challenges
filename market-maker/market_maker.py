#!/usr/bin/env python3
"""
Market Maker Simulation
Simulates a market maker operating on an order book with buy/sell orders.
"""

import heapq
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Order:
    """Represents a buy or sell order"""
    order_type: str  # 'B' for buy, 'S' for sell
    price: int
    quantity: int
    is_mm: bool = False  # True if this is a market maker quote

    def __repr__(self):
        mm_flag = " (MM)" if self.is_mm else ""
        return f"{self.order_type} {self.quantity}@{self.price}{mm_flag}"


class OrderBook:
    """Maintains buy and sell order books using heaps for efficient matching"""

    def __init__(self):
        # Buy book: max heap (negate prices for Python's min heap)
        # Store as (-price, insertion_order, order)
        self.buy_book: List[Tuple[int, int, Order]] = []

        # Sell book: min heap
        # Store as (price, insertion_order, order)
        self.sell_book: List[Tuple[int, int, Order]] = []

        self.insertion_counter = 0

    def add_order(self, order: Order):
        """Add an order to the appropriate book"""
        if order.quantity <= 0:
            return

        if order.order_type == 'B':
            # For buy orders, use negative price for max heap behavior
            heapq.heappush(self.buy_book, (-order.price, self.insertion_counter, order))
        else:  # 'S'
            heapq.heappush(self.sell_book, (order.price, self.insertion_counter, order))

        self.insertion_counter += 1

    def get_best_bid(self) -> Optional[int]:
        """Get the highest buy price (best bid)"""
        if self.buy_book:
            return -self.buy_book[0][0]
        return None

    def get_best_ask(self) -> Optional[int]:
        """Get the lowest sell price (best ask)"""
        if self.sell_book:
            return self.sell_book[0][0]
        return None

    def match_order(self, order: Order, mm_tracker: 'MarketMakerTracker') -> List[Tuple[int, int, bool]]:
        """
        Match an incoming order against the book.
        Returns list of (price, quantity, is_mm_counterparty) tuples for executed trades.
        """
        trades = []
        remaining_qty = order.quantity

        if order.order_type == 'B':
            # Buy order matches against sell book (lowest prices first)
            while remaining_qty > 0 and self.sell_book:
                best_ask_price, _, best_sell = self.sell_book[0]

                # Check if trade can happen
                if best_ask_price > order.price:
                    break

                # Execute trade
                trade_qty = min(remaining_qty, best_sell.quantity)
                trade_price = best_ask_price

                trades.append((trade_price, trade_qty, best_sell.is_mm))

                # Update the market maker if they're the counterparty
                if best_sell.is_mm:
                    # MM sold, so they receive cash and lose inventory
                    mm_tracker.execute_trade('S', trade_price, trade_qty)

                remaining_qty -= trade_qty
                best_sell.quantity -= trade_qty

                # Remove if fully filled
                if best_sell.quantity <= 0:
                    heapq.heappop(self.sell_book)

        else:  # order.order_type == 'S'
            # Sell order matches against buy book (highest prices first)
            while remaining_qty > 0 and self.buy_book:
                neg_best_bid_price, _, best_buy = self.buy_book[0]
                best_bid_price = -neg_best_bid_price

                # Check if trade can happen
                if best_bid_price < order.price:
                    break

                # Execute trade
                trade_qty = min(remaining_qty, best_buy.quantity)
                trade_price = best_bid_price

                trades.append((trade_price, trade_qty, best_buy.is_mm))

                # Update the market maker if they're the counterparty
                if best_buy.is_mm:
                    # MM bought, so they pay cash and gain inventory
                    mm_tracker.execute_trade('B', trade_price, trade_qty)

                remaining_qty -= trade_qty
                best_buy.quantity -= trade_qty

                # Remove if fully filled
                if best_buy.quantity <= 0:
                    heapq.heappop(self.buy_book)

        # Add remaining quantity to the book
        if remaining_qty > 0:
            remaining_order = Order(order.order_type, order.price, remaining_qty, order.is_mm)
            self.add_order(remaining_order)

        return trades


class MarketMakerTracker:
    """Tracks market maker's cash, inventory, and profit"""

    def __init__(self, holding_cost_per_unit: int):
        self.cash = 0
        self.inventory = 0
        self.holding_cost = holding_cost_per_unit
        self.total_holding_cost_incurred = 0

    def execute_trade(self, side: str, price: int, quantity: int):
        """Execute a trade for the market maker"""
        if side == 'B':
            # Market maker bought: pay cash, gain inventory
            self.cash -= price * quantity
            self.inventory += quantity
        else:  # 'S'
            # Market maker sold: receive cash, lose inventory
            self.cash += price * quantity
            self.inventory -= quantity

    def apply_holding_cost(self):
        """Apply holding cost for one time step"""
        cost = self.holding_cost * abs(self.inventory)
        self.total_holding_cost_incurred += cost

    def get_profit(self) -> int:
        """Calculate final profit"""
        return self.cash - self.total_holding_cost_incurred

    def __repr__(self):
        return f"Cash: {self.cash}, Inventory: {self.inventory}, Profit: {self.get_profit()}"


class MarketMaker:
    """Market maker with quoting strategy"""

    def __init__(self, quote_qty: int = 10):
        self.quote_qty = quote_qty

    def generate_quotes(self, book: OrderBook) -> Tuple[Optional[Order], Optional[Order]]:
        """
        Generate buy and sell quotes based on current book state.
        Strategy: Quote at the touch (best bid/ask) to provide competitive liquidity
        """
        best_bid = book.get_best_bid()
        best_ask = book.get_best_ask()

        buy_quote = None
        sell_quote = None

        # Generate buy quote - join the best bid
        if best_bid is not None:
            buy_quote = Order('B', best_bid, self.quote_qty, is_mm=True)
        elif best_ask is not None:
            # No bids, quote below the best ask
            buy_price = best_ask - 1
            if buy_price > 0:
                buy_quote = Order('B', buy_price, self.quote_qty, is_mm=True)

        # Generate sell quote - join the best ask
        if best_ask is not None:
            sell_quote = Order('S', best_ask, self.quote_qty, is_mm=True)
        elif best_bid is not None:
            # No asks, quote above the best bid
            sell_price = best_bid + 1
            if sell_price <= 1000:
                sell_quote = Order('S', sell_price, self.quote_qty, is_mm=True)

        return buy_quote, sell_quote


def simulate_market(time_steps: int, holding_cost: int, orders_by_step: List[List[Order]],
                    verbose: bool = False) -> MarketMakerTracker:
    """
    Simulate the market maker over multiple time steps.

    Args:
        time_steps: Number of time steps
        holding_cost: Cost per unit of inventory per time step
        orders_by_step: List of order lists, one per time step
        verbose: Whether to print detailed logs

    Returns:
        MarketMakerTracker with final state
    """
    book = OrderBook()
    mm = MarketMaker(quote_qty=10)
    tracker = MarketMakerTracker(holding_cost)

    for step in range(time_steps):
        if verbose:
            print(f"\n{'='*60}")
            print(f"STEP {step + 1}/{time_steps}")
            print(f"{'='*60}")
            print(f"Book state at start: Best Bid={book.get_best_bid()}, Best Ask={book.get_best_ask()}")
            print(f"MM state at start: Cash={tracker.cash}, Inventory={tracker.inventory}")

        # 1. Market maker places quotes at the start of the step
        buy_quote, sell_quote = mm.generate_quotes(book)

        if verbose:
            print(f"\n--- MM Placing Quotes ---")

        if buy_quote:
            if verbose:
                print(f"  BUY quote: {buy_quote}")
            book.add_order(buy_quote)
        elif verbose:
            print(f"  No BUY quote generated")

        if sell_quote:
            if verbose:
                print(f"  SELL quote: {sell_quote}")
            book.add_order(sell_quote)
        elif verbose:
            print(f"  No SELL quote generated")

        if verbose:
            print(f"Book after MM quotes: Best Bid={book.get_best_bid()}, Best Ask={book.get_best_ask()}")

        # 2. Process incoming orders for this step
        if verbose:
            print(f"\n--- Processing Incoming Orders ---")

        if step < len(orders_by_step):
            if verbose and len(orders_by_step[step]) == 0:
                print(f"  No incoming orders this step")

            for order in orders_by_step[step]:
                if verbose:
                    print(f"\n  Incoming: {order}")
                    cash_before = tracker.cash
                    inv_before = tracker.inventory

                trades = book.match_order(order, tracker)

                if verbose:
                    if trades:
                        for price, qty, is_mm in trades:
                            mm_flag = " [MM was counterparty]" if is_mm else ""
                            print(f"    ✓ Executed: {qty} @ ${price}{mm_flag}")

                        cash_change = tracker.cash - cash_before
                        inv_change = tracker.inventory - inv_before
                        print(f"    MM impact: Cash {cash_before} → {tracker.cash} ({cash_change:+d}), "
                              f"Inventory {inv_before} → {tracker.inventory} ({inv_change:+d})")
                    else:
                        print(f"    No immediate match - added to book")

        # 3. Apply holding cost at the end of the step
        holding_cost_this_step = holding_cost * abs(tracker.inventory)
        tracker.apply_holding_cost()

        if verbose:
            print(f"\n--- End of Step {step + 1} ---")
            print(f"Holding cost applied: {holding_cost} × |{tracker.inventory}| = {holding_cost_this_step}")
            print(f"MM Final state: Cash={tracker.cash}, Inventory={tracker.inventory}, "
                  f"Total Holding Cost={tracker.total_holding_cost_incurred}, Profit={tracker.get_profit()}")

    return tracker


def parse_input(input_text: str) -> Tuple[int, int, List[List[Order]]]:
    """Parse input format and return time_steps, holding_cost, and orders_by_step"""
    lines = input_text.strip().split('\n')
    idx = 0

    # Parse T and C
    time_steps, holding_cost = map(int, lines[idx].split())
    idx += 1

    orders_by_step = []

    for _ in range(time_steps):
        # Parse number of orders for this step
        n_orders = int(lines[idx])
        idx += 1

        step_orders = []
        for _ in range(n_orders):
            parts = lines[idx].split()
            order_type = parts[0]
            price = int(parts[1])
            quantity = int(parts[2])
            step_orders.append(Order(order_type, price, quantity))
            idx += 1

        orders_by_step.append(step_orders)

    return time_steps, holding_cost, orders_by_step


def main():
    """Main entry point"""
    import sys

    # Check for verbose flag
    verbose = '--verbose' in sys.argv or '-v' in sys.argv

    # Read all input
    input_text = sys.stdin.read()

    # Parse input
    time_steps, holding_cost, orders_by_step = parse_input(input_text)

    # Run simulation
    tracker = simulate_market(time_steps, holding_cost, orders_by_step, verbose=verbose)

    # Output results
    if verbose:
        print(f"\n{'='*60}")
        print(f"FINAL RESULTS")
        print(f"{'='*60}")
    print(f"Final Cash: {tracker.cash}")
    print(f"Final Inventory: {tracker.inventory}")
    print(f"Profit: {tracker.get_profit()}")


if __name__ == "__main__":
    main()
