import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

print("\n" + "="*80)
print("CREATING DATABASE WITH SAMPLE DATA")
print("="*80 + "\n")


conn = sqlite3.connect('bluestock_mf.db')
cursor = conn.cursor()


print(" Creating tables...\n")

cursor.execute('''CREATE TABLE dim_fund (
    fund_id INTEGER PRIMARY KEY,
    fund_name TEXT,
    fund_house TEXT,
    category TEXT
)''')

cursor.execute('''CREATE TABLE dim_date (
    date_id INTEGER PRIMARY KEY,
    date TEXT
)''')

cursor.execute('''CREATE TABLE fact_nav (
    nav_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_id INTEGER,
    date_id INTEGER,
    nav_value REAL
)''')

cursor.execute('''CREATE TABLE dim_investor (
    investor_id INTEGER PRIMARY KEY,
    investor_state TEXT
)''')

cursor.execute('''CREATE TABLE fact_transactions (
    txn_id INTEGER PRIMARY KEY AUTOINCREMENT,
    investor_id INTEGER,
    fund_id INTEGER,
    date_id INTEGER,
    transaction_type TEXT,
    amount REAL
)''')

cursor.execute('''CREATE TABLE fact_performance (
    perf_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_id INTEGER,
    date_id INTEGER,
    returns_1y REAL,
    returns_3y REAL,
    returns_5y REAL
)''')

cursor.execute('''CREATE TABLE fact_aum (
    aum_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_id INTEGER,
    date_id INTEGER,
    aum_value REAL
)''')


print("  - Inserting fund data...")
fund_houses = ['SBI', 'ICICI', 'HDFC', 'Axis', 'Kotak', 'Nippon']
for i in range(1, 41):
    fund_house = fund_houses[i % len(fund_houses)]
    cursor.execute("INSERT INTO dim_fund VALUES (?, ?, ?, ?)", 
                   (i, f'Fund {i}', fund_house, 'Large Cap'))
conn.commit()


print("  - Inserting date data...")
start_date = datetime(2022, 1, 1)
for i in range(1, 1001):
    date = start_date + timedelta(days=i)
    cursor.execute("INSERT INTO dim_date VALUES (?, ?)", (i, str(date.date())))
conn.commit()


print("  - Inserting investor data...")
states = ['Telangana', 'Karnataka', 'Tamil Nadu', 'Delhi', 'Maharashtra', 'Gujarat']
for i in range(1, 101):
    state = states[i % len(states)]
    cursor.execute("INSERT INTO dim_investor VALUES (?, ?)", (i, state))
conn.commit()

print("  - Inserting NAV data...")
np.random.seed(42)
for fund_id in range(1, 41):
    nav_value = 100
    for date_id in range(1, 101):
        nav_value = nav_value * (1 + np.random.normal(0.0004, 0.015))
        cursor.execute("INSERT INTO fact_nav (fund_id, date_id, nav_value) VALUES (?, ?, ?)",
                      (fund_id, date_id, nav_value))
conn.commit()


print("  - Inserting transaction data...")
for i in range(1, 501):
    investor_id = (i % 100) + 1
    fund_id = (i % 40) + 1
    date_id = (i % 1000) + 1
    amount = np.random.uniform(10000, 100000)
    cursor.execute("""INSERT INTO fact_transactions 
                     (investor_id, fund_id, date_id, transaction_type, amount) 
                     VALUES (?, ?, ?, ?, ?)""",
                  (investor_id, fund_id, date_id, 'SIP', amount))
conn.commit()


print("  - Inserting performance data...")
for fund_id in range(1, 41):
    for date_id in range(1, 101, 10):
        cursor.execute("""INSERT INTO fact_performance 
                         (fund_id, date_id, returns_1y, returns_3y, returns_5y) 
                         VALUES (?, ?, ?, ?, ?)""",
                      (fund_id, date_id, 0.15, 0.12, 0.10))
conn.commit()


print("  - Inserting AUM data...\n")
for fund_id in range(1, 41):
    for date_id in range(1, 501, 50):
        aum = 1000000 + (fund_id * 100000)
        cursor.execute("INSERT INTO fact_aum (fund_id, date_id, aum_value) VALUES (?, ?, ?)",
                      (fund_id, date_id, aum))
conn.commit()

print("✓ Tables created successfully!")
print("✓ Data inserted:")
print(f"  - Funds: 40")
print(f"  - Dates: 1000")
print(f"  - Investors: 100")
print(f"  - NAV records: 400")
print(f"  - Transactions: 500\n")

cursor.execute("SELECT COUNT(*) FROM fact_nav")
print(f"✓ fact_nav table has {cursor.fetchone()[0]} records")
print(f"✓ Database ready!\n")

conn.close()

print("="*80 + "\n")