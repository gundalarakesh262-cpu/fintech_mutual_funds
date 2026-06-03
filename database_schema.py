"""
Day 2: Database Schema & Data Loading Script
Creates SQLite star schema and loads cleaned data
"""

import pandas as pd
import sqlite3
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import os

DB_PATH = "bluestock_mf.db"
DATA_PROCESSED = "data/processed"

def create_schema_sql():
    """Generate SQL CREATE TABLE statements"""
    schema_sql = """
-- Star Schema for Mutual Fund Analytics

-- DIMENSION TABLES

CREATE TABLE IF NOT EXISTS dim_fund (
    fund_id INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code VARCHAR(10) UNIQUE NOT NULL,
    fund_name VARCHAR(255) NOT NULL,
    fund_house VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    sub_category VARCHAR(50),
    risk_grade VARCHAR(10),
    launch_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dim_date (
    date_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE UNIQUE NOT NULL,
    year INTEGER,
    month INTEGER,
    day INTEGER,
    quarter INTEGER,
    day_of_week VARCHAR(10),
    is_weekend INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dim_investor (
    investor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    investor_key VARCHAR(50) UNIQUE,
    kyc_status VARCHAR(20),
    investor_state VARCHAR(50),
    investor_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- FACT TABLES

CREATE TABLE IF NOT EXISTS fact_nav (
    nav_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_id INTEGER NOT NULL,
    date_id INTEGER NOT NULL,
    nav_value FLOAT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (fund_id) REFERENCES dim_fund(fund_id),
    FOREIGN KEY (date_id) REFERENCES dim_date(date_id),
    UNIQUE(fund_id, date_id)
);

CREATE TABLE IF NOT EXISTS fact_transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    investor_id INTEGER NOT NULL,
    fund_id INTEGER NOT NULL,
    date_id INTEGER NOT NULL,
    transaction_type VARCHAR(20) NOT NULL,
    amount FLOAT NOT NULL,
    units FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (investor_id) REFERENCES dim_investor(investor_id),
    FOREIGN KEY (fund_id) REFERENCES dim_fund(fund_id),
    FOREIGN KEY (date_id) REFERENCES dim_date(date_id)
);

CREATE TABLE IF NOT EXISTS fact_performance (
    performance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_id INTEGER NOT NULL,
    date_id INTEGER NOT NULL,
    return_1m FLOAT,
    return_3m FLOAT,
    return_6m FLOAT,
    return_1y FLOAT,
    return_3y FLOAT,
    return_5y FLOAT,
    expense_ratio FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (fund_id) REFERENCES dim_fund(fund_id),
    FOREIGN KEY (date_id) REFERENCES dim_date(date_id),
    UNIQUE(fund_id, date_id)
);

CREATE TABLE IF NOT EXISTS fact_aum (
    aum_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_id INTEGER NOT NULL,
    date_id INTEGER NOT NULL,
    aum_value FLOAT NOT NULL,
    aum_units FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (fund_id) REFERENCES dim_fund(fund_id),
    FOREIGN KEY (date_id) REFERENCES dim_date(date_id),
    UNIQUE(fund_id, date_id)
);

-- CREATE INDEXES FOR PERFORMANCE

CREATE INDEX IF NOT EXISTS idx_nav_fund_date ON fact_nav(fund_id, date_id);
CREATE INDEX IF NOT EXISTS idx_txn_investor ON fact_transactions(investor_id);
CREATE INDEX IF NOT EXISTS idx_txn_fund ON fact_transactions(fund_id);
CREATE INDEX IF NOT EXISTS idx_perf_fund ON fact_performance(fund_id);
CREATE INDEX IF NOT EXISTS idx_aum_fund ON fact_aum(fund_id);
"""
    
    return schema_sql

def create_database():
    """Create SQLite database and schema"""
    print("="*80)
    print("CREATING SQLITE DATABASE & SCHEMA")
    print("="*80 + "\n")
    
    # Remove existing DB if you want fresh start
    # if os.path.exists(DB_PATH):
    #     os.remove(DB_PATH)
    #     print(f"✓ Removed existing database\n")
    
    # Connect to SQLite
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create schema
    schema = create_schema_sql()
    cursor.executescript(schema)
    
    conn.commit()
    conn.close()
    
    print(f"✓ Database created: {DB_PATH}")
    print("✓ Tables created:")
    print("  - dim_fund")
    print("  - dim_date")
    print("  - dim_investor")
    print("  - fact_nav")
    print("  - fact_transactions")
    print("  - fact_performance")
    print("  - fact_aum\n")

def load_data_into_db():
    """Load cleaned data into SQLite database"""
    print("="*80)
    print("LOADING DATA INTO DATABASE")
    print("="*80 + "\n")
    
    engine = create_engine(f'sqlite:///{DB_PATH}')
    
    tables_loaded = {}
    
    # 1. Load nav_history
    print("1️⃣  Loading nav_history...")
    try:
        nav_df = pd.read_csv(f"{DATA_PROCESSED}/nav_history_cleaned.csv")
        # Map to fact_nav table
        nav_df.to_sql('nav_history_staging', engine, if_exists='replace', index=False)
        print(f"   ✓ Loaded {len(nav_df)} rows")
        tables_loaded['nav_history'] = len(nav_df)
    except FileNotFoundError:
        print("   ❌ File not found")
    
    # 2. Load investor_transactions
    print("\n2️⃣  Loading investor_transactions...")
    try:
        txn_df = pd.read_csv(f"{DATA_PROCESSED}/investor_transactions_cleaned.csv")
        txn_df.to_sql('transactions_staging', engine, if_exists='replace', index=False)
        print(f"   ✓ Loaded {len(txn_df)} rows")
        tables_loaded['transactions'] = len(txn_df)
    except FileNotFoundError:
        print("   ❌ File not found")
    
    # 3. Load scheme_performance
    print("\n3️⃣  Loading scheme_performance...")
    try:
        perf_df = pd.read_csv(f"{DATA_PROCESSED}/scheme_performance_cleaned.csv")
        perf_df.to_sql('performance_staging', engine, if_exists='replace', index=False)
        print(f"   ✓ Loaded {len(perf_df)} rows")
        tables_loaded['performance'] = len(perf_df)
    except FileNotFoundError:
        print("   ❌ File not found")
    
    print(f"\n✓ Data loaded into staging tables\n")
    
    return tables_loaded

def verify_database():
    """Verify database integrity"""
    print("="*80)
    print("DATABASE VERIFICATION")
    print("="*80 + "\n")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = cursor.fetchall()
    
    print(f"✓ Tables in database ({len(tables)}):")
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        count = cursor.fetchone()[0]
        print(f"  - {table_name}: {count} rows")
    
    conn.close()
    print()

def main():
    """Main execution"""
    print("\n" + "="*80)
    print("DAY 2: DATABASE SCHEMA & DATA LOADING")
    print("="*80 + "\n")
    
    # 1. Create database and schema
    create_database()
    
    # 2. Load data
    tables_loaded = load_data_into_db()
    
    # 3. Verify
    verify_database()
    
    print("="*80)
    print("✓ Database setup complete!")
    print("Next: Run queries.py for analytical queries")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
