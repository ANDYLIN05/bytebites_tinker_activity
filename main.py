from models import (
    Customer, CustomerStatus,
    FoodItem, Category,
    OrderItem, Order,
    Menu
)

print("=" * 50)
print(" ByteBites — Manual Test Script")
print("=" * 50)


# ─────────────────────────────────────────
# 1. Set up the menu with some food items
# ─────────────────────────────────────────
print("\n── Building the menu ──")

menu = Menu()
menu.add_item(FoodItem("Spicy Burger",    8.99,  Category.BURGERS,  popularity_rating=4.8))
menu.add_item(FoodItem("Classic Burger",  7.49,  Category.BURGERS,  popularity_rating=4.2))
menu.add_item(FoodItem("Large Soda",      2.49,  Category.DRINKS,   popularity_rating=3.9))
menu.add_item(FoodItem("Milkshake",       4.99,  Category.DRINKS,   popularity_rating=4.6))
menu.add_item(FoodItem("Chocolate Cake",  5.49,  Category.DESSERTS, popularity_rating=4.7))
menu.add_item(FoodItem("Fries",           3.29,  Category.SIDES,    popularity_rating=4.1))
menu.add_item(FoodItem("Onion Rings",     3.79,  Category.SIDES,    popularity_rating=3.5))

print(menu)


# ─────────────────────────────────────────
# 2. Filter by category
# ─────────────────────────────────────────
print("\n── Filter: BURGERS ──")
burgers = menu.filter_by_category(Category.BURGERS)
for item in burgers:
    print(" ", item.get_details())

print("\n── Filter: DRINKS ──")
drinks = menu.filter_by_category(Category.DRINKS)
for item in drinks:
    print(" ", item.get_details())


# ─────────────────────────────────────────
# 3. Keyword search
# ─────────────────────────────────────────
print("\n── Search: 'burger' ──")
results = menu.search("burger")
for item in results:
    print(" ", item.get_details())


# ─────────────────────────────────────────
# 4. Sort the menu
# ─────────────────────────────────────────
print("\n── Sort: by price (low → high) ──")
for item in menu.sort_by_price():
    print(f"  ${item.price:.2f}  {item.name}")

print("\n── Sort: by popularity (high → low) ──")
for item in menu.sort_by_popularity():
    print(f"  {item.popularity_rating}/5.0  {item.name}")


# ─────────────────────────────────────────
# 5. Create a customer and verify them
# ─────────────────────────────────────────
print("\n── Customer setup ──")
andy = Customer("Andy", "andy@bytebites.com")
print(f"  Before verify: {andy}")
andy.verify()
print(f"  After verify:  {andy}")


# ─────────────────────────────────────────
# 6. Place an order
# ─────────────────────────────────────────
print("\n── Placing an order ──")
order = Order(andy)

spicy_burger   = menu.search("spicy")[0]
large_soda     = menu.search("soda")[0]
choc_cake      = menu.search("chocolate")[0]

order.add_item(OrderItem(spicy_burger, quantity=3))  # 3 x Spicy Burger
order.add_item(OrderItem(large_soda,   quantity=2))  # 2 x Large Soda
order.add_item(OrderItem(choc_cake,    quantity=1))  # 1 x Chocolate Cake

print(f"  {order}")
print("\n── Receipt ──")
for line in order.items:
    print(" ", line.get_snapshot())
print(f"  {'TOTAL':<40} ${order.compute_total():.2f}")


# ─────────────────────────────────────────
# 7. Test price lock — change burger price AFTER ordering
# ─────────────────────────────────────────
print("\n── Price lock test ──")
print(f"  Order total before price change: ${order.compute_total():.2f}")
spicy_burger.price = 99.99  # simulate a price hike
print(f"  Spicy Burger new price:          ${spicy_burger.price:.2f}")
print(f"  Order total after price change:  ${order.compute_total():.2f}  (unchanged — price is locked)")


# ─────────────────────────────────────────
# 8. Add order to customer history & cancel
# ─────────────────────────────────────────
print("\n── Order lifecycle ──")
andy.purchase_history.append(order)
print(f"  Orders in history: {len(andy.get_history())}")

cancelled = order.cancel()
print(f"  Cancel attempt: {'success' if cancelled else 'failed'}")
print(f"  Order status: {order.status.value}")

cancelled_again = order.cancel()
print(f"  Cancel again:  {'success' if cancelled_again else 'failed (already cancelled)'}")

print("\n" + "=" * 50)
print(" All tests complete.")
print("=" * 50)
