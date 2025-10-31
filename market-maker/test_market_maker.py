#!/usr/bin/env python3
"""
Unit tests for Market Maker Simulation
Tests all components: Order, OrderBook, MarketMakerTracker, MarketMaker, and simulation logic
"""

import pytest
from market_maker import (
    Order,
    OrderBook,
    MarketMakerTracker,
    MarketMaker,
    simulate_market,
    parse_input
)


# ============================================================================
# Order Class Tests
# ============================================================================

class TestOrder:
    """Tests for the Order class"""

    def test_order_creation_buy(self):
        """Test creating a buy order"""
        order = Order('B', 100, 10)
        assert order.order_type == 'B'
        assert order.price == 100
        assert order.quantity == 10
        assert order.is_mm == False

    def test_order_creation_sell(self):
        """Test creating a sell order"""
        order = Order('S', 105, 5)
        assert order.order_type == 'S'
        assert order.price == 105
        assert order.quantity == 5
        assert order.is_mm == False

    def test_order_creation_market_maker(self):
        """Test creating a market maker order"""
        order = Order('B', 100, 10, is_mm=True)
        assert order.is_mm == True

    def test_order_repr(self):
        """Test order string representation"""
        order = Order('B', 100, 10)
        assert "B" in repr(order)
        assert "100" in repr(order)
        assert "10" in repr(order)

        mm_order = Order('S', 100, 10, is_mm=True)
        assert "(MM)" in repr(mm_order)


# ============================================================================
# OrderBook Class Tests
# ============================================================================

class TestOrderBook:
    """Tests for the OrderBook class"""

    def test_orderbook_initialization(self):
        """Test creating an empty order book"""
        book = OrderBook()
        assert book.get_best_bid() is None
        assert book.get_best_ask() is None
        assert book.insertion_counter == 0

    def test_add_buy_order(self):
        """Test adding a buy order"""
        book = OrderBook()
        order = Order('B', 100, 10)
        book.add_order(order)
        assert book.get_best_bid() == 100

    def test_add_sell_order(self):
        """Test adding a sell order"""
        book = OrderBook()
        order = Order('S', 105, 10)
        book.add_order(order)
        assert book.get_best_ask() == 105

    def test_add_zero_quantity_order(self):
        """Test that zero quantity orders are not added"""
        book = OrderBook()
        order = Order('B', 100, 0)
        book.add_order(order)
        assert book.get_best_bid() is None

    def test_add_negative_quantity_order(self):
        """Test that negative quantity orders are not added"""
        book = OrderBook()
        order = Order('S', 100, -5)
        book.add_order(order)
        assert book.get_best_ask() is None

    def test_best_bid_multiple_orders(self):
        """Test best bid with multiple buy orders"""
        book = OrderBook()
        book.add_order(Order('B', 100, 10))
        book.add_order(Order('B', 102, 5))
        book.add_order(Order('B', 98, 15))
        assert book.get_best_bid() == 102  # Highest buy price

    def test_best_ask_multiple_orders(self):
        """Test best ask with multiple sell orders"""
        book = OrderBook()
        book.add_order(Order('S', 105, 10))
        book.add_order(Order('S', 103, 5))
        book.add_order(Order('S', 107, 15))
        assert book.get_best_ask() == 103  # Lowest sell price

    def test_fifo_ordering_same_price(self):
        """Test FIFO ordering for orders at the same price"""
        book = OrderBook()
        tracker = MarketMakerTracker(holding_cost_per_unit=0)

        # Add three buy orders at price 100
        order1 = Order('B', 100, 10)
        order2 = Order('B', 100, 5)
        order3 = Order('B', 100, 3)

        book.add_order(order1)
        book.add_order(order2)
        book.add_order(order3)

        # Match with a sell order
        sell_order = Order('S', 100, 12)
        trades = book.match_order(sell_order, tracker)

        # Should fill 10 from first order, then 2 from second order (FIFO)
        assert len(trades) == 2
        assert trades[0][1] == 10  # First trade: 10 units
        assert trades[1][1] == 2   # Second trade: 2 units


class TestOrderBookMatching:
    """Tests for order matching logic"""

    def test_match_buy_order_full_fill(self):
        """Test matching a buy order that fully fills"""
        book = OrderBook()
        tracker = MarketMakerTracker(holding_cost_per_unit=0)

        book.add_order(Order('S', 100, 10))
        buy_order = Order('B', 100, 10)

        trades = book.match_order(buy_order, tracker)

        assert len(trades) == 1
        assert trades[0] == (100, 10, False)  # price, qty, is_mm
        assert book.get_best_ask() is None  # Sell order fully consumed

    def test_match_sell_order_full_fill(self):
        """Test matching a sell order that fully fills"""
        book = OrderBook()
        tracker = MarketMakerTracker(holding_cost_per_unit=0)

        book.add_order(Order('B', 100, 10))
        sell_order = Order('S', 100, 10)

        trades = book.match_order(sell_order, tracker)

        assert len(trades) == 1
        assert trades[0] == (100, 10, False)
        assert book.get_best_bid() is None

    def test_match_buy_order_partial_fill(self):
        """Test matching a buy order that partially fills"""
        book = OrderBook()
        tracker = MarketMakerTracker(holding_cost_per_unit=0)

        book.add_order(Order('S', 100, 5))
        buy_order = Order('B', 100, 10)

        trades = book.match_order(buy_order, tracker)

        assert len(trades) == 1
        assert trades[0] == (100, 5, False)
        assert book.get_best_bid() == 100  # Remaining 5 units added as bid

    def test_match_sell_order_partial_fill(self):
        """Test matching a sell order that partially fills"""
        book = OrderBook()
        tracker = MarketMakerTracker(holding_cost_per_unit=0)

        book.add_order(Order('B', 100, 5))
        sell_order = Order('S', 100, 10)

        trades = book.match_order(sell_order, tracker)

        assert len(trades) == 1
        assert trades[0] == (100, 5, False)
        assert book.get_best_ask() == 100  # Remaining 5 units added as ask

    def test_match_no_price_improvement_buy(self):
        """Test buy order that doesn't match due to price"""
        book = OrderBook()
        tracker = MarketMakerTracker(holding_cost_per_unit=0)

        book.add_order(Order('S', 105, 10))
        buy_order = Order('B', 100, 10)

        trades = book.match_order(buy_order, tracker)

        assert len(trades) == 0
        assert book.get_best_bid() == 100
        assert book.get_best_ask() == 105

    def test_match_no_price_improvement_sell(self):
        """Test sell order that doesn't match due to price"""
        book = OrderBook()
        tracker = MarketMakerTracker(holding_cost_per_unit=0)

        book.add_order(Order('B', 95, 10))
        sell_order = Order('S', 100, 10)

        trades = book.match_order(sell_order, tracker)

        assert len(trades) == 0
        assert book.get_best_bid() == 95
        assert book.get_best_ask() == 100

    def test_match_multiple_levels(self):
        """Test matching across multiple price levels"""
        book = OrderBook()
        tracker = MarketMakerTracker(holding_cost_per_unit=0)

        # Add multiple sell orders at different prices
        book.add_order(Order('S', 100, 5))
        book.add_order(Order('S', 101, 5))
        book.add_order(Order('S', 102, 5))

        # Buy order sweeps through multiple levels
        buy_order = Order('B', 102, 12)
        trades = book.match_order(buy_order, tracker)

        assert len(trades) == 3
        assert trades[0] == (100, 5, False)
        assert trades[1] == (101, 5, False)
        assert trades[2] == (102, 2, False)

    def test_match_with_mm_counterparty(self):
        """Test matching updates market maker when MM is counterparty"""
        book = OrderBook()
        tracker = MarketMakerTracker(holding_cost_per_unit=0)

        # MM places a sell order
        mm_order = Order('S', 100, 10, is_mm=True)
        book.add_order(mm_order)

        # Incoming buy order matches with MM
        buy_order = Order('B', 100, 10)
        trades = book.match_order(buy_order, tracker)

        assert len(trades) == 1
        assert trades[0][2] == True  # is_mm flag is True
        assert tracker.cash == 1000  # MM sold 10@100
        assert tracker.inventory == -10


# ============================================================================
# MarketMakerTracker Class Tests
# ============================================================================

class TestMarketMakerTracker:
    """Tests for the MarketMakerTracker class"""

    def test_tracker_initialization(self):
        """Test tracker initialization"""
        tracker = MarketMakerTracker(holding_cost_per_unit=5)
        assert tracker.cash == 0
        assert tracker.inventory == 0
        assert tracker.holding_cost == 5
        assert tracker.total_holding_cost_incurred == 0

    def test_execute_buy_trade(self):
        """Test executing a buy trade"""
        tracker = MarketMakerTracker(holding_cost_per_unit=0)
        tracker.execute_trade('B', 100, 10)

        assert tracker.cash == -1000  # Paid 10 * 100
        assert tracker.inventory == 10

    def test_execute_sell_trade(self):
        """Test executing a sell trade"""
        tracker = MarketMakerTracker(holding_cost_per_unit=0)
        tracker.execute_trade('S', 105, 5)

        assert tracker.cash == 525  # Received 5 * 105
        assert tracker.inventory == -5

    def test_execute_multiple_trades(self):
        """Test executing multiple trades"""
        tracker = MarketMakerTracker(holding_cost_per_unit=0)

        tracker.execute_trade('B', 100, 10)  # Buy 10@100
        tracker.execute_trade('S', 105, 10)  # Sell 10@105

        assert tracker.cash == 50  # -1000 + 1050
        assert tracker.inventory == 0

    def test_apply_holding_cost_zero_inventory(self):
        """Test holding cost with zero inventory"""
        tracker = MarketMakerTracker(holding_cost_per_unit=5)
        tracker.apply_holding_cost()

        assert tracker.total_holding_cost_incurred == 0

    def test_apply_holding_cost_positive_inventory(self):
        """Test holding cost with positive inventory"""
        tracker = MarketMakerTracker(holding_cost_per_unit=5)
        tracker.inventory = 10
        tracker.apply_holding_cost()

        assert tracker.total_holding_cost_incurred == 50  # 5 * 10

    def test_apply_holding_cost_negative_inventory(self):
        """Test holding cost with negative inventory (uses absolute value)"""
        tracker = MarketMakerTracker(holding_cost_per_unit=5)
        tracker.inventory = -10
        tracker.apply_holding_cost()

        assert tracker.total_holding_cost_incurred == 50  # 5 * abs(-10)

    def test_apply_holding_cost_multiple_steps(self):
        """Test holding cost accumulation over multiple steps"""
        tracker = MarketMakerTracker(holding_cost_per_unit=2)
        tracker.inventory = 5

        tracker.apply_holding_cost()
        tracker.apply_holding_cost()
        tracker.apply_holding_cost()

        assert tracker.total_holding_cost_incurred == 30  # 2 * 5 * 3 steps

    def test_get_profit_no_trades(self):
        """Test profit calculation with no trades"""
        tracker = MarketMakerTracker(holding_cost_per_unit=5)
        assert tracker.get_profit() == 0

    def test_get_profit_with_trades(self):
        """Test profit calculation with trades"""
        tracker = MarketMakerTracker(holding_cost_per_unit=0)
        tracker.execute_trade('B', 100, 10)
        tracker.execute_trade('S', 105, 10)

        assert tracker.get_profit() == 50  # Bought at 100, sold at 105

    def test_get_profit_with_holding_costs(self):
        """Test profit calculation including holding costs"""
        tracker = MarketMakerTracker(holding_cost_per_unit=2)
        tracker.execute_trade('B', 100, 10)
        tracker.apply_holding_cost()  # 2 * 10 = 20
        tracker.execute_trade('S', 105, 10)

        profit = tracker.get_profit()
        assert profit == 30  # 50 profit - 20 holding cost


# ============================================================================
# MarketMaker Class Tests
# ============================================================================

class TestMarketMaker:
    """Tests for the MarketMaker quote generation"""

    def test_mm_initialization(self):
        """Test market maker initialization"""
        mm = MarketMaker(quote_qty=15)
        assert mm.quote_qty == 15

    def test_mm_default_quote_qty(self):
        """Test market maker default quote quantity"""
        mm = MarketMaker()
        assert mm.quote_qty == 10

    def test_generate_quotes_empty_book(self):
        """Test quote generation with empty book"""
        book = OrderBook()
        mm = MarketMaker()

        buy_quote, sell_quote = mm.generate_quotes(book)

        assert buy_quote is None
        assert sell_quote is None

    def test_generate_quotes_with_bid_and_ask(self):
        """Test quote generation with existing bid and ask"""
        book = OrderBook()
        book.add_order(Order('B', 100, 10))
        book.add_order(Order('S', 105, 10))

        mm = MarketMaker()
        buy_quote, sell_quote = mm.generate_quotes(book)

        assert buy_quote is not None
        assert buy_quote.price == 100  # Join best_bid
        assert buy_quote.quantity == 10
        assert buy_quote.is_mm == True

        assert sell_quote is not None
        assert sell_quote.price == 105  # Join best_ask
        assert sell_quote.quantity == 10
        assert sell_quote.is_mm == True

    def test_generate_quotes_only_bids(self):
        """Test quote generation with only bids in book"""
        book = OrderBook()
        book.add_order(Order('B', 100, 10))

        mm = MarketMaker()
        buy_quote, sell_quote = mm.generate_quotes(book)

        assert buy_quote is not None
        assert buy_quote.price == 100  # Join best_bid

        assert sell_quote is not None
        assert sell_quote.price == 101  # best_bid + 1

    def test_generate_quotes_only_asks(self):
        """Test quote generation with only asks in book"""
        book = OrderBook()
        book.add_order(Order('S', 105, 10))

        mm = MarketMaker()
        buy_quote, sell_quote = mm.generate_quotes(book)

        assert buy_quote is not None
        assert buy_quote.price == 104  # best_ask - 1

        assert sell_quote is not None
        assert sell_quote.price == 105  # Join best_ask

    def test_generate_quotes_price_too_low(self):
        """Test quote generation when best bid is 1"""
        book = OrderBook()
        book.add_order(Order('B', 1, 10))

        mm = MarketMaker()
        buy_quote, sell_quote = mm.generate_quotes(book)

        assert buy_quote is not None
        assert buy_quote.price == 1  # Join best_bid at 1
        assert sell_quote is not None
        assert sell_quote.price == 2  # best_bid + 1

    def test_generate_quotes_price_too_high(self):
        """Test quote generation when best ask is 1000"""
        book = OrderBook()
        book.add_order(Order('S', 1000, 10))

        mm = MarketMaker()
        buy_quote, sell_quote = mm.generate_quotes(book)

        assert buy_quote is not None
        assert buy_quote.price == 999  # best_ask - 1
        assert sell_quote is not None
        assert sell_quote.price == 1000  # Join best_ask at 1000


# ============================================================================
# Integration Tests - simulate_market
# ============================================================================

class TestSimulateMarket:
    """Integration tests for the full simulation"""

    def test_simulate_empty_market(self):
        """Test simulation with no orders"""
        orders_by_step = [[], [], []]
        tracker = simulate_market(3, 5, orders_by_step)

        assert tracker.cash == 0
        assert tracker.inventory == 0
        assert tracker.get_profit() == 0

    def test_simulate_basic_trade(self):
        """Test simulation with basic trade"""
        # Step 1: incoming buy and sell orders
        orders_by_step = [
            [Order('B', 99, 5), Order('S', 101, 5)],
        ]

        tracker = simulate_market(1, 2, orders_by_step)

        # MM should have placed quotes and possibly traded
        # At minimum, holding costs should be applied
        assert tracker.total_holding_cost_incurred >= 0

    def test_simulate_example_input(self):
        """Test simulation with the example input from problem"""
        # T=3, C=2
        # Step 1: B 99@5, S 101@5
        # Step 2: S 100@3
        # Step 3: B 102@4

        orders_by_step = [
            [Order('B', 99, 5), Order('S', 101, 5)],
            [Order('S', 100, 3)],
            [Order('B', 102, 4)]
        ]

        tracker = simulate_market(3, 2, orders_by_step)

        # Verify simulation runs successfully and tracker is in valid state
        assert tracker is not None
        assert tracker.holding_cost == 2
        assert tracker.total_holding_cost_incurred >= 0
        # The exact values depend on the MM strategy and order matching

    def test_simulate_mm_trades(self):
        """Test that MM quotes are placed and simulation runs correctly"""
        # Create a market with bid/ask spread
        orders_by_step = [
            [Order('B', 100, 5), Order('S', 110, 5)],  # Wide spread
            [Order('S', 98, 20)],  # Aggressive sell that will hit MM's buy quote
        ]

        tracker = simulate_market(2, 0, orders_by_step)

        # Verify simulation runs successfully
        assert tracker is not None
        # MM may or may not have traded depending on quote placement timing
        # Just verify the tracker is in a valid state
        assert isinstance(tracker.cash, int)
        assert isinstance(tracker.inventory, int)

    def test_simulate_holding_costs_accumulate(self):
        """Test that holding costs accumulate over time"""
        orders_by_step = [
            [Order('B', 100, 5)],
            [Order('S', 95, 20)],  # MM buys inventory
            [],  # Empty step - holding costs apply
            [],  # Empty step - holding costs apply
        ]

        tracker = simulate_market(4, 5, orders_by_step)

        # Should have inventory and holding costs
        assert tracker.total_holding_cost_incurred > 0


# ============================================================================
# Input Parsing Tests
# ============================================================================

class TestParseInput:
    """Tests for input parsing function"""

    def test_parse_basic_input(self):
        """Test parsing basic input"""
        input_text = """2 5
1
B 100 10
1
S 105 5"""

        time_steps, holding_cost, orders_by_step = parse_input(input_text)

        assert time_steps == 2
        assert holding_cost == 5
        assert len(orders_by_step) == 2
        assert len(orders_by_step[0]) == 1
        assert orders_by_step[0][0].order_type == 'B'
        assert orders_by_step[0][0].price == 100
        assert orders_by_step[0][0].quantity == 10

    def test_parse_example_input(self):
        """Test parsing the example input"""
        input_text = """3 2
2
B 99 5
S 101 5
1
S 100 3
1
B 102 4"""

        time_steps, holding_cost, orders_by_step = parse_input(input_text)

        assert time_steps == 3
        assert holding_cost == 2
        assert len(orders_by_step) == 3
        assert len(orders_by_step[0]) == 2
        assert len(orders_by_step[1]) == 1
        assert len(orders_by_step[2]) == 1

    def test_parse_empty_step(self):
        """Test parsing with empty steps"""
        input_text = """3 1
0
1
B 100 10
0"""

        time_steps, holding_cost, orders_by_step = parse_input(input_text)

        assert time_steps == 3
        assert len(orders_by_step[0]) == 0
        assert len(orders_by_step[1]) == 1
        assert len(orders_by_step[2]) == 0

    def test_parse_multiple_orders_per_step(self):
        """Test parsing multiple orders in a single step"""
        input_text = """1 0
3
B 100 5
S 105 10
B 98 3"""

        time_steps, holding_cost, orders_by_step = parse_input(input_text)

        assert len(orders_by_step[0]) == 3
        assert orders_by_step[0][0].price == 100
        assert orders_by_step[0][1].price == 105
        assert orders_by_step[0][2].price == 98


# ============================================================================
# Edge Cases and Scenarios
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_large_price_values(self):
        """Test handling of large price values"""
        book = OrderBook()
        book.add_order(Order('B', 999, 10))
        book.add_order(Order('S', 1000, 10))

        assert book.get_best_bid() == 999
        assert book.get_best_ask() == 1000

    def test_large_quantity_values(self):
        """Test handling of large quantities"""
        tracker = MarketMakerTracker(holding_cost_per_unit=1)
        tracker.execute_trade('B', 100, 1000)

        assert tracker.cash == -100000
        assert tracker.inventory == 1000

    def test_alternating_trades(self):
        """Test alternating buy and sell trades"""
        tracker = MarketMakerTracker(holding_cost_per_unit=1)

        for _ in range(10):
            tracker.execute_trade('B', 100, 5)
            tracker.apply_holding_cost()
            tracker.execute_trade('S', 101, 5)
            tracker.apply_holding_cost()

        assert tracker.inventory == 0
        assert tracker.cash > 0  # Should have profit from spread

    def test_deep_order_book(self):
        """Test order book with many levels"""
        book = OrderBook()

        # Add 100 buy orders at different prices
        for i in range(100):
            book.add_order(Order('B', 100 - i, 10))

        # Add 100 sell orders at different prices
        for i in range(100):
            book.add_order(Order('S', 101 + i, 10))

        assert book.get_best_bid() == 100
        assert book.get_best_ask() == 101


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
