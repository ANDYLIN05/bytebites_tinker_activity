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

