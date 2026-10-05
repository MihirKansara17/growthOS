import datetime
import random
from sqlalchemy.orm import Session
from app.db.models import (
    Base, engine, Tenant, Store, Product, Customer, 
    Transaction, TransactionItem, InventorySnapshot, Alert
)

def seed_database():
    Base.metadata.create_all(bind=engine)
    db = Session(bind=engine)
    
    # Check if already seeded
    if db.query(Tenant).count() > 0:
        print("Database already seeded.")
        db.close()
        return

    print("Seeding 3 Multi-Tenant Retail Datasets...")

    # TENANT 1: High-Tech Multi-Store Chain ("Apex Retail Chains")
    t1 = Tenant(
        id="tenant_apex",
        name="Apex Retail Chains (Multi-Store)",
        maturity_level="HIGH_MULTI_STORE",
        description="High tech maturity chain with 3 stores in Mumbai, Bengaluru & Delhi, full barcodes, SKU inventory tracking & RFM phone tracking."
    )
    db.add(t1)
    
    stores_t1 = [
        Store(id="store_mumbai", tenant_id="tenant_apex", name="Mumbai Flagship", city="Mumbai"),
        Store(id="store_blr", tenant_id="tenant_apex", name="Bengaluru Store", city="Bengaluru"),
        Store(id="store_delhi", tenant_id="tenant_apex", name="Delhi Store", city="Delhi")
    ]
    db.add_all(stores_t1)
    db.commit()
    
    categories = ["Packaged Foods", "Apparel & Fashion", "Electronics & Acc", "Personal Care", "Beverages"]
    products_t1 = []
    for i in range(1, 51):
        cat = random.choice(categories)
        p = Product(
            id=f"prod_apex_{i}",
            tenant_id="tenant_apex",
            sku=f"SKU-APX-{1000+i}",
            barcode=f"8901000{1000+i}",
            name=f"{cat} Item #{i}",
            category=cat,
            cost_price=round(random.uniform(50, 800), 2),
            selling_price=round(random.uniform(100, 1500), 2)
        )
        products_t1.append(p)
    db.add_all(products_t1)
    
    customers_t1 = []
    for i in range(1, 101):
        c = Customer(
            id=f"cust_apex_{i}",
            tenant_id="tenant_apex",
            name=f"Customer {i}",
            phone=f"+9198765{i:05d}",
            segment="VIP" if i <= 15 else ("Loyal" if i <= 50 else "At-Risk")
        )
        customers_t1.append(c)
    db.add_all(customers_t1)
    db.commit()

    # Generate 12 months of realistic transactions for Tenant 1
    start_date = datetime.datetime.utcnow() - datetime.timedelta(days=365)
    transactions = []
    items = []
    snapshots = []
    
    # Stock inventory snapshots for Tenant 1
    for store in stores_t1:
        for prod in products_t1:
            stock = random.randint(5, 120)
            snapshots.append(InventorySnapshot(
                id=f"inv_{store.id}_{prod.id}",
                tenant_id="tenant_apex",
                store_id=store.id,
                product_id=prod.id,
                stock_on_hand=stock,
                reorder_level=15
            ))
    db.add_all(snapshots)

    # Historical transactions with simulated Diwali/Holi seasonal spikes
    curr = start_date
    tx_counter = 1
    while curr <= datetime.datetime.utcnow():
        # High sales spike during festival months (Oct/Nov & March)
        num_daily_tx = random.randint(15, 30)
        if curr.month in [10, 11, 3]: 
            num_daily_tx = random.randint(35, 60)
            
        for _ in range(num_daily_tx):
            store = random.choice(stores_t1)
            cust = random.choice(customers_t1)
            payment = random.choice(["UPI", "UPI", "CARD", "COD"])
            
            # Select 1-4 random products
            bought_prods = random.sample(products_t1, k=random.randint(1, 4))
            tx_total = 0
            
            tx_id = f"tx_apx_{tx_counter}"
            tx_counter += 1
            
            for prod in bought_prods:
                qty = random.randint(1, 3)
                total_p = round(qty * prod.selling_price, 2)
                tx_total += total_p
                items.append(TransactionItem(
                    id=f"txi_{tx_id}_{prod.id}",
                    transaction_id=tx_id,
                    product_id=prod.id,
                    category_name=prod.category,
                    quantity=qty,
                    unit_price=prod.selling_price,
                    total_price=total_p
                ))
                
            transactions.append(Transaction(
                id=tx_id,
                tenant_id="tenant_apex",
                store_id=store.id,
                customer_id=cust.id,
                timestamp=curr + datetime.timedelta(hours=random.randint(9, 21), minutes=random.randint(0, 59)),
                total_amount=round(tx_total, 2),
                payment_method=payment
            ))
            
        curr += datetime.timedelta(days=1)
        
    db.add_all(transactions)
    db.add_all(items)

    # TENANT 2: Medium-Tech Single Store Kirana ("Shree Ganesh Kirana")
    t2 = Tenant(
        id="tenant_ganesh",
        name="Shree Ganesh Kirana (Digital Store)",
        maturity_level="MEDIUM_EXCEL",
        description="Single store Kirana using Excel & basic POS exports. Has itemized product records but no customer phone RFM tracking."
    )
    db.add(t2)
    s2 = Store(id="store_ganesh_main", tenant_id="tenant_ganesh", name="Shree Ganesh Kirana", city="Pune")
    db.add(s2)
    
    # TENANT 3: Basic Traditional Store ("Verma General Store")
    t3 = Tenant(
        id="tenant_verma",
        name="Verma General Store (Traditional)",
        maturity_level="BASIC_TRADITIONAL",
        description="Traditional store maintaining basic category daily sales logs. Demonstrates graceful degradation and data quality upgrade path."
    )
    db.add(t3)
    s3 = Store(id="store_verma_main", tenant_id="tenant_verma", name="Verma Store", city="Jaipur")
    db.add(s3)

    # Alerts for Tenant 1
    db.add_all([
        Alert(id="alt_1", tenant_id="tenant_apex", type="STOCKOUT_RISK", severity="HIGH", title="Critical Stockout Warning: Electronics & Acc", description="Electronics items in Bengaluru Store have Days of Cover < 4 days."),
        Alert(id="alt_2", tenant_id="tenant_apex", type="REVENUE_DROP", severity="MEDIUM", title="Revenue Variance Detected", description="Delhi Store revenue dropped 14% WoW due to volume decline in Apparel & Fashion."),
        Alert(id="alt_3", tenant_id="tenant_apex", type="CHURN_WARNING", severity="HIGH", title="VIP Churn Alert", description="18 VIP customers haven't purchased in > 45 days. Recommended campaign: 10% Win-back coupon.")
    ])

    db.commit()
    print("Seeding finished successfully.")
    db.close()

if __name__ == "__main__":
    seed_database()
