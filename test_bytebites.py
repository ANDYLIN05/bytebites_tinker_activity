import pytest
from models import OrderStatus
from models import (
    Customer, CustomerStatus,
    FoodItem, Category,
    OrderItem, Order,
    Menu
)


# ─────────────────────────────────────────
# Fixtures — reusable test data
# ─────────────────────────────────────────

@pytest.fixture
def menu():
    """A Menu pre-loaded with a small set of items across categories."""
    m = Menu()
    m.add_item(FoodItem("Spicy Burger",   8.99, Category.BURGERS,  popularity_rating=4.8))
    m.add_item(FoodItem("Classic Burger", 7.49, Category.BURGERS,  popularity_rating=4.2))
    m.add_item(FoodItem("Large Soda",     2.49, Category.DRINKS,   popularity_rating=3.9))
    m.add_item(FoodItem("Milkshake",      4.99, Category.DRINKS,   popularity_rating=4.6))
    m.add_item(FoodItem("Chocolate Cake", 5.49, Category.DESSERTS, popularity_rating=4.7))
    m.add_item(FoodItem("Fries",          3.29, Category.SIDES,    popularity_rating=4.1))
    return m

@pytest.fixture
def customer():
    """A basic guest customer."""
    return Customer("Andy", "andy@bytebites.com")

@pytest.fixture
def verified_customer(customer):
    """A customer who has been verified."""
    customer.verify()
    return customer

@pytest.fixture
def order(verified_customer):
    """An empty order tied to a verified customer."""
    return Order(verified_customer)


# ─────────────────────────────────────────
# Order total tests
# ─────────────────────────────────────────

def test_order_total_is_zero_when_empty(order):
    """An order with no items should compute a total of $0.00."""
    assert order.compute_total() == 0.0

def test_order_total_with_single_item(order, menu):
    """An order with one item should return that item's price as the total."""
    burger = menu.search("spicy")[0]
    order.add_item(OrderItem(burger, quantity=1))
    assert order.compute_total() == 8.99

def test_order_total_with_multiple_items(order, menu):
    """Adding a burger ($8.99) and a soda ($2.49) should total $11.48."""
    burger = menu.search("spicy")[0]
    soda   = menu.search("soda")[0]
    order.add_item(OrderItem(burger, quantity=1))
    order.add_item(OrderItem(soda,   quantity=1))
    assert order.compute_total() == 11.48

def test_order_total_respects_quantity(order, menu):
    """3 Spicy Burgers at $8.99 each should total $26.97."""
    burger = menu.search("spicy")[0]
    order.add_item(OrderItem(burger, quantity=3))
    assert order.compute_total() == 26.97

def test_order_total_is_price_locked(order, menu):
    """Changing a FoodItem's price after ordering should not affect the order total."""
    burger = menu.search("spicy")[0]
    order.add_item(OrderItem(burger, quantity=1))
    total_before = order.compute_total()
    burger.price = 99.99  # simulate a price hike
    assert order.compute_total() == total_before


# ─────────────────────────────────────────
# Menu filtering tests
# ─────────────────────────────────────────

def test_filter_by_category_returns_only_matching_items(menu):
    """Filtering by BURGERS should return only burger items."""
    results = menu.filter_by_category(Category.BURGERS)
    assert all(item.category == Category.BURGERS for item in results)

def test_filter_by_category_returns_correct_count(menu):
    """There are 2 burgers in the fixture menu."""
    results = menu.filter_by_category(Category.BURGERS)
    assert len(results) == 2

def test_filter_by_category_empty_result(menu):
    """Filtering by SPECIALS should return an empty list when none exist."""
    results = menu.filter_by_category(Category.SPECIALS)
    assert results == []


# ─────────────────────────────────────────
# Menu sorting tests
# ─────────────────────────────────────────

def test_sort_by_price_ascending(menu):
    """sort_by_price() should return items cheapest first."""
    sorted_items = menu.sort_by_price()
    prices = [item.price for item in sorted_items]
    assert prices == sorted(prices)

def test_sort_by_price_descending(menu):
    """sort_by_price(descending=True) should return items most expensive first."""
    sorted_items = menu.sort_by_price(descending=True)
    prices = [item.price for item in sorted_items]
    assert prices == sorted(prices, reverse=True)

def test_sort_by_popularity(menu):
    """sort_by_popularity() should return highest rated items first."""
    sorted_items = menu.sort_by_popularity()
    ratings = [item.popularity_rating for item in sorted_items]
    assert ratings == sorted(ratings, reverse=True)


# ─────────────────────────────────────────
# Menu search tests
# ─────────────────────────────────────────

def test_search_returns_matching_items(menu):
    """Searching 'burger' should return all items with burger in the name."""
    results = menu.search("burger")
    assert len(results) == 2

def test_search_is_case_insensitive(menu):
    """Search should work regardless of casing — 'BURGER' matches 'burger'."""
    results = menu.search("BURGER")
    assert len(results) == 2

def test_search_no_match_returns_empty(menu):
    """Searching a term that matches nothing should return an empty list."""
    results = menu.search("pizza")
    assert results == []


# ─────────────────────────────────────────
# Customer tests
# ─────────────────────────────────────────

def test_customer_default_status_is_guest(customer):
    """A newly created customer should have GUEST status by default."""
    assert customer.status == CustomerStatus.GUEST

def test_customer_verify_sets_verified_status(customer):
    """Calling verify() should promote the customer to VERIFIED."""
    customer.verify()
    assert customer.status == CustomerStatus.VERIFIED

def test_suspended_customer_cannot_be_verified(customer):
    """A SUSPENDED customer should not be upgradeable to VERIFIED."""
    customer.status = CustomerStatus.SUSPENDED
    result = customer.verify()
    assert result is False
    assert customer.status == CustomerStatus.SUSPENDED

def test_customer_unique_ids_are_different():
    """Two customers with the same name should have different unique IDs."""
    a = Customer("Andy", "a@bytebites.com")
    b = Customer("Andy", "b@bytebites.com")
    assert a.unique_id != b.unique_id


# ─────────────────────────────────────────
# Order lifecycle tests
# ─────────────────────────────────────────

def test_order_cancel_sets_cancelled_status(order):
    """Cancelling a PENDING order should set its status to CANCELLED."""
    order.cancel()
    assert order.status == OrderStatus.CANCELLED

def test_order_cannot_cancel_twice(order):
    """Cancelling an already cancelled order should return False."""
    order.cancel()
    result = order.cancel()
    assert result is False

def test_order_duplicate_item_increments_quantity(order, menu):
    """Adding the same FoodItem twice should merge into one OrderItem with combined quantity."""
    burger = menu.search("spicy")[0]
    order.add_item(OrderItem(burger, quantity=1))
    order.add_item(OrderItem(burger, quantity=2))
    assert len(order.items) == 1
    assert order.items[0].quantity == 3


