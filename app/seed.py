from app.database import SessionLocal, engine
from app.models import Allocation, Base, Order, OrderItem, Product


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if db.query(Product).count() > 0:
        print("Database already seeded, skipping.")
        db.close()
        return

    products = [
        Product(name="Widget A", sku="WGT-001", available_quantity=100),
        Product(name="Widget B", sku="WGT-002", available_quantity=50),
        Product(name="Gadget Pro", sku="GDG-001", available_quantity=30),
        Product(name="Gadget Lite", sku="GDG-002", available_quantity=75),
        Product(name="Bolt M6x20", sku="BLT-006", available_quantity=500),
        Product(name="Bolt M8x30", sku="BLT-008", available_quantity=300),
        Product(name="Nut M6", sku="NUT-006", available_quantity=600),
        Product(name="Nut M8", sku="NUT-008", available_quantity=400),
        Product(name="Steel Plate 10mm", sku="PLT-010", available_quantity=20),
        Product(name="Steel Plate 5mm", sku="PLT-005", available_quantity=45),
        Product(name="Copper Wire 1m", sku="COP-001", available_quantity=200),
        Product(name="Copper Wire 5m", sku="COP-005", available_quantity=80),
        Product(name="LED Module Red", sku="LED-RED", available_quantity=150),
        Product(name="LED Module Blue", sku="LED-BLU", available_quantity=150),
        Product(name="Sensor Unit", sku="SNS-001", available_quantity=25),
        Product(name="Motor DC 12V", sku="MOT-012", available_quantity=15),
        Product(name="Motor DC 24V", sku="MOT-024", available_quantity=10),
        Product(name="Battery Pack", sku="BAT-001", available_quantity=40),
        Product(name="Circuit Board v2", sku="PCB-002", available_quantity=60),
        Product(name="Enclosure Small", sku="ENC-S01", available_quantity=35),
    ]
    db.add_all(products)
    db.flush()

    orders = [
        Order(customer="Acme Corp", priority=1, status="pending"),
        Order(customer="Acme Corp", priority=2, status="pending"),
        Order(customer="Globex Inc", priority=1, status="confirmed"),
        Order(customer="Globex Inc", priority=3, status="pending"),
        Order(customer="Initech", priority=2, status="confirmed"),
        Order(customer="Umbrella Ltd", priority=1, status="pending"),
        Order(customer="Umbrella Ltd", priority=3, status="shipped"),
        Order(customer="Stark Industries", priority=1, status="pending"),
        Order(customer="Wayne Enterprises", priority=2, status="confirmed"),
        Order(customer="Cyberdyne", priority=3, status="pending"),
    ]
    db.add_all(orders)
    db.flush()

    # Several orders compete for the same products (motors, sensors, batteries)
    order_items = [
        # Order 1 - Acme wants motors and sensors
        OrderItem(order_id=1, product_id=16, requested_quantity=8),   # Motor 12V (only 15 avail)
        OrderItem(order_id=1, product_id=15, requested_quantity=10),  # Sensor (only 25 avail)
        OrderItem(order_id=1, product_id=18, requested_quantity=20),  # Battery (only 40 avail)
        # Order 2 - Acme also wants batteries and boards
        OrderItem(order_id=2, product_id=18, requested_quantity=15),  # Battery - competes w/ order 1
        OrderItem(order_id=2, product_id=19, requested_quantity=30),  # Circuit Board
        # Order 3 - Globex wants motors too
        OrderItem(order_id=3, product_id=16, requested_quantity=10),  # Motor 12V - competes w/ order 1
        OrderItem(order_id=3, product_id=17, requested_quantity=5),   # Motor 24V (only 10 avail)
        # Order 4 - Globex wants plates and bolts
        OrderItem(order_id=4, product_id=9, requested_quantity=10),   # Steel Plate 10mm (only 20)
        OrderItem(order_id=4, product_id=5, requested_quantity=100),  # Bolt M6
        # Order 5 - Initech wants sensors and LEDs
        OrderItem(order_id=5, product_id=15, requested_quantity=12),  # Sensor - competes w/ order 1
        OrderItem(order_id=5, product_id=13, requested_quantity=50),  # LED Red
        OrderItem(order_id=5, product_id=14, requested_quantity=50),  # LED Blue
        # Order 6 - Umbrella wants everything scarce
        OrderItem(order_id=6, product_id=16, requested_quantity=5),   # Motor 12V - 3-way competition
        OrderItem(order_id=6, product_id=15, requested_quantity=8),   # Sensor - 3-way competition
        OrderItem(order_id=6, product_id=17, requested_quantity=7),   # Motor 24V - competes w/ order 3
        # Order 7 - Umbrella shipped order (simple)
        OrderItem(order_id=7, product_id=1, requested_quantity=20),   # Widget A
        OrderItem(order_id=7, product_id=2, requested_quantity=10),   # Widget B
        # Order 8 - Stark wants batteries and enclosures
        OrderItem(order_id=8, product_id=18, requested_quantity=10),  # Battery - 3-way competition
        OrderItem(order_id=8, product_id=20, requested_quantity=15),  # Enclosure (only 35)
        OrderItem(order_id=8, product_id=19, requested_quantity=25),  # Circuit Board - competes w/ order 2
        # Order 9 - Wayne wants copper and plates
        OrderItem(order_id=9, product_id=11, requested_quantity=100), # Copper 1m
        OrderItem(order_id=9, product_id=9, requested_quantity=12),   # Steel Plate 10mm - competes w/ order 4
        # Order 10 - Cyberdyne wants gadgets
        OrderItem(order_id=10, product_id=3, requested_quantity=15),  # Gadget Pro (only 30)
        OrderItem(order_id=10, product_id=4, requested_quantity=25),  # Gadget Lite
    ]
    db.add_all(order_items)

    # A few existing allocations for the confirmed/shipped orders
    allocations = [
        Allocation(order_id=3, product_id=16, allocated_quantity=10),  # Globex got their motors
        Allocation(order_id=3, product_id=17, allocated_quantity=5),
        Allocation(order_id=5, product_id=13, allocated_quantity=50),  # Initech got LEDs
        Allocation(order_id=5, product_id=14, allocated_quantity=50),
        Allocation(order_id=7, product_id=1, allocated_quantity=20),   # Umbrella shipped
        Allocation(order_id=7, product_id=2, allocated_quantity=10),
    ]
    db.add_all(allocations)

    db.commit()
    db.close()
    print("Seeded 20 products, 10 orders, order items, and allocations.")


if __name__ == "__main__":
    seed()
