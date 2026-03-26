"""
Customer - represents a registered user. Stores their identity (uniqueID, email) and purchase history. The status field (via CustomerStatus) tells the system whether they're verified, a guest, or flagged.

FoodItem - a single item on the menu like a "Spicy Burger" or "Large Soda". Holds the name, price, category, and popularity rating. The category is enforced by the Category enum to prevent typos.

OrderItem - the link class between Order and FoodItem. Handles quantity (e.g. "3 Spicy Burgers") and locks in the price at the time of purchase so historical totals stay accurate.

Order - a single transaction tied to a Customer. Holds a list of OrderItems, tracks when it was placed (orderDate), and computes the total. Its lifecycle is managed through the OrderStatus enum.

Menu - the full catalogue of available FoodItems. Acts as the system's central list, supporting filtering by category and keyword search for browsing.

CustomerStatus - enum controlling user state: VERIFIED, GUEST, FLAGGED, or SUSPENDED.

OrderStatus - enum tracking a transaction's lifecycle: PENDING → CONFIRMED → DELIVERED, or CANCELLED/REFUNDED.

Category - enum locking in valid food categories like BURGERS, DRINKS, and DESSERTS to keep filtering reliable.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional


# ─────────────────────────────────────────
# Enums
# ─────────────────────────────────────────

class CustomerStatus(Enum):
    """
    Represents the verification state of a Customer account.

    - VERIFIED:  Confirmed legitimate account.
    - GUEST:     Browsing without a full account.
    - FLAGGED:   Marked for review due to suspicious activity.
    - SUSPENDED: Blocked from the system.
    """
    VERIFIED  = "verified"
    GUEST     = "guest"
    FLAGGED   = "flagged"
    SUSPENDED = "suspended"


class OrderStatus(Enum):
    """
    Tracks the lifecycle of an Order from creation to completion.

    - PENDING:   Created but not yet confirmed.
    - CONFIRMED: Accepted and being prepared.
    - CANCELLED: Cancelled before completion.
    - DELIVERED: Successfully delivered.
    - REFUNDED:  Returned and payment refunded.
    """
    PENDING   = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    DELIVERED = "delivered"
    REFUNDED  = "refunded"


class Category(Enum):
    """
    Valid food categories for a FoodItem.
    Using an Enum instead of a raw String prevents typos
    (e.g. 'Drink' vs 'Drinks') from breaking Menu filters.
    """
    BURGERS  = "burgers"
    DRINKS   = "drinks"
    DESSERTS = "desserts"
    SIDES    = "sides"
    SPECIALS = "specials"


# ─────────────────────────────────────────
# Customer
# ─────────────────────────────────────────

class Customer:
    """
    Represents a registered user of the ByteBites system.

    Attributes:
        unique_id:        Auto-generated UUID — ensures two users named
                          'Andy' never collide in the database.
        name:             Display name of the customer.
        email:            Used for communication and as a secondary unique key.
        status:           Current verification state (CustomerStatus enum).
        purchase_history: List of past Order objects linked to this customer.
    """

    def __init__(self, name: str, email: str,
                 status: CustomerStatus = CustomerStatus.GUEST):
        self.unique_id: str = str(uuid.uuid4())
        self.name: str = name
        self.email: str = email
        self.status: CustomerStatus = status
        self.purchase_history: List["Order"] = []

    def verify(self) -> bool:
        """
        Promotes the customer to VERIFIED status.
        Returns True if successful, False if account is SUSPENDED.
        """
        if self.status == CustomerStatus.SUSPENDED:
            return False
        self.status = CustomerStatus.VERIFIED
        return True

    def get_history(self) -> List["Order"]:
        """Returns the full list of past orders for this customer."""
        return self.purchase_history

    def __repr__(self) -> str:
        return f"Customer(name={self.name!r}, email={self.email!r}, status={self.status.value})"


# ─────────────────────────────────────────
# FoodItem
# ─────────────────────────────────────────

class FoodItem:
    """
    Represents a single item available on the ByteBites menu.

    Attributes:
        item_id:          Auto-generated UUID for database referencing.
        name:             Display name (e.g. 'Spicy Burger').
        price:            Current price in dollars.
        category:         Category enum value (e.g. Category.BURGERS).
        popularity_rating: Score between 0.0 and 5.0 reflecting customer ratings.
    """

    def __init__(self, name: str, price: float, category: Category,
                 popularity_rating: float = 0.0):
        self.item_id: str = str(uuid.uuid4())
        self.name: str = name
        self.price: float = price
        self.category: Category = category
        self.popularity_rating: float = popularity_rating

    def get_details(self) -> str:
        """Returns a formatted summary string of this food item."""
        return (f"[{self.category.value.upper()}] {self.name} "
                f"— ${self.price:.2f} (Rating: {self.popularity_rating}/5.0)")

    def update_popularity(self, rating: float) -> None:
        """
        Updates the popularity rating.
        Clamps the value between 0.0 and 5.0.
        """
        if not 0.0 <= rating <= 5.0:
            raise ValueError("Rating must be between 0.0 and 5.0.")
        self.popularity_rating = rating

    def __repr__(self) -> str:
        return f"FoodItem(name={self.name!r}, price={self.price}, category={self.category.value})"


# ─────────────────────────────────────────
# OrderItem  (link class)
# ─────────────────────────────────────────

class OrderItem:
    """
    Links a FoodItem to an Order with a quantity and a locked-in price.

    This is the key class that solves two problems:
      1. Quantity: store '3 x Spicy Burger' instead of three duplicate objects.
      2. Price history: locking priceAtPurchase means that if the burger price
         rises next month, old receipts still show the correct total.

    Attributes:
        food_item:          Reference to the FoodItem being ordered.
        quantity:           Number of units ordered.
        price_at_purchase:  Price per unit at the time of ordering.
    """

    def __init__(self, food_item: FoodItem, quantity: int = 1):
        if quantity < 1:
            raise ValueError("Quantity must be at least 1.")
        self.food_item: FoodItem = food_item
        self.quantity: int = quantity
        self.price_at_purchase: float = food_item.price  # locked in at creation

    def get_subtotal(self) -> float:
        """Returns price_at_purchase × quantity for this line item."""
        return round(self.price_at_purchase * self.quantity, 2)

    def get_snapshot(self) -> str:
        """Returns a receipt-style string for this line item."""
        return (f"{self.food_item.name} x{self.quantity} "
                f"@ ${self.price_at_purchase:.2f} = ${self.get_subtotal():.2f}")

    def set_quantity(self, n: int) -> None:
        """Updates the quantity. Must be at least 1."""
        if n < 1:
            raise ValueError("Quantity must be at least 1.")
        self.quantity = n

    def __repr__(self) -> str:
        return f"OrderItem(item={self.food_item.name!r}, qty={self.quantity}, subtotal={self.get_subtotal()})"


# ─────────────────────────────────────────
# Order
# ─────────────────────────────────────────

class Order:
    """
    Represents a single transaction in the ByteBites system.

    Attributes:
        order_id:   Auto-generated UUID.
        customer:   The Customer who placed this order.
        items:      List of OrderItem objects in this transaction.
        order_date: Timestamp of when the order was created.
        status:     Current lifecycle state (OrderStatus enum).
    """

    def __init__(self, customer: Customer):
        self.order_id: str = str(uuid.uuid4())
        self.customer: Customer = customer
        self.items: List[OrderItem] = []
        self.order_date: datetime = datetime.now()
        self.status: OrderStatus = OrderStatus.PENDING

    def add_item(self, item: OrderItem) -> None:
        """
        Adds an OrderItem to this order.
        If the same FoodItem already exists, increments its quantity instead.
        """
        for existing in self.items:
            if existing.food_item.item_id == item.food_item.item_id:
                existing.set_quantity(existing.quantity + item.quantity)
                return
        self.items.append(item)

    def compute_total(self) -> float:
        """
        Calculates the total cost by summing each OrderItem's subtotal
        (price_at_purchase × quantity). Uses locked-in prices, not current ones.
        """
        return round(sum(i.get_subtotal() for i in self.items), 2)

    def cancel(self) -> bool:
        """
        Cancels the order if it hasn't already been delivered or refunded.
        Returns True if cancelled successfully, False otherwise.
        """
        if self.status in (OrderStatus.DELIVERED, OrderStatus.REFUNDED):
            return False
        self.status = OrderStatus.CANCELLED
        return True

    def __repr__(self) -> str:
        return (f"Order(id={self.order_id[:8]}..., customer={self.customer.name!r}, "
                f"total=${self.compute_total()}, status={self.status.value})")


# ─────────────────────────────────────────
# Menu
# ─────────────────────────────────────────

class Menu:
    """
    The central catalogue of all available FoodItems in the ByteBites system.

    Acts as the single source of truth for what can be ordered.
    Supports filtering by category and keyword search for browsing.

    Attributes:
        items: Master list of all FoodItem objects.
    """

    def __init__(self):
        self.items: List[FoodItem] = []

    def add_item(self, item: FoodItem) -> None:
        """Adds a FoodItem to the menu."""
        self.items.append(item)

    def remove_item(self, item_id: str) -> bool:
        """
        Removes a FoodItem by its UUID.
        Returns True if found and removed, False if not found.
        """
        for item in self.items:
            if item.item_id == item_id:
                self.items.remove(item)
                return True
        return False

    def filter_by_category(self, category: Category) -> List[FoodItem]:
        """Returns all FoodItems matching the given Category enum value."""
        return [i for i in self.items if i.category == category]

    def get_all_items(self) -> List[FoodItem]:
        """Returns the full list of menu items."""
        return self.items

    def search(self, keyword: str) -> List[FoodItem]:
        """
        Case-insensitive keyword search across item names.
        e.g. search('burger') returns all items with 'burger' in the name.
        """
        kw = keyword.lower()
        return [i for i in self.items if kw in i.name.lower()]
    
    def sort_by_price(self, descending: bool = False) -> List[FoodItem]:
        """
        Returns menu items sorted by price.
        Default is ascending (cheapest first).
        Pass descending=True for most expensive first.
        """
        return sorted(self.items, key=lambda i: i.price, reverse=descending)

    def sort_by_popularity(self, descending: bool = True) -> List[FoodItem]:
        """
        Returns menu items sorted by popularity rating.
        Default is descending (highest rated first).
        """
        return sorted(self.items, key=lambda i: i.popularity_rating, reverse=descending)
    
    def __repr__(self) -> str:
        return f"Menu(items={len(self.items)} items)"