"""
Day 1: Data Ingestion Script
Loads 10 CSV datasets, explores structure, identifies anomalies
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path

# Define data paths
DATA_RAW = "data/raw"
DATA_PROCESSED = "data/processed"

def ensure_directories():
    """Create necessary directories"""
    Path(DATA_RAW).mkdir(parents=True, exist_ok=True)
    Path(DATA_PROCESSED).mkdir(parents=True, exist_ok=True)
    print("✓ Directories created/verified\n")

def load_and_explore_dataset(file_path, dataset_name):
    """Load CSV and print shape, dtypes, head, and anomalies"""
    print(f"\n{'='*80}")
    print(f"Dataset: {dataset_name}")
    print(f"{'='*80}")
    
    try:
        df = pd.read_csv(file_path)
        
        # 1. Shape
        print(f"\n📊 Shape: {df.shape}")
        print(f"   Rows: {df.shape[0]}, Columns: {df.shape[1]}")
        
        # 2. Data Types
        print(f"\n📋 Data Types:")
        print(df.dtypes)
        
        # 3. First 5 rows
        print(f"\n👀 First 5 Rows:")
        print(df.head())
        
        # 4. Anomalies Detection
        print(f"\n⚠️  Anomalies:")
        anomalies = []
        
        # Missing values
        missing = df.isnull().sum()
        if missing.sum() > 0:
            anomalies.append(f"   Missing Values: {missing[missing > 0].to_dict()}")
        else:
            anomalies.append("   ✓ No missing values")
        
        # Duplicate rows
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            anomalies.append(f"   Duplicate Rows: {duplicates}")
        else:
            anomalies.append("   ✓ No duplicate rows")
        
        # Numeric columns - check for negative values where unexpected
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if (df[col] < 0).any():
                neg_count = (df[col] < 0).sum()
                anomalies.append(f"   Negative Values in '{col}': {neg_count}")
        
        # Empty strings in object columns
        obj_cols = df.select_dtypes(include=['object']).columns
        for col in obj_cols:
            empty_count = (df[col] == '').sum()
            if empty_count > 0:
                anomalies.append(f"   Empty Strings in '{col}': {empty_count}")
        
        for anomaly in anomalies:
            print(anomaly)
        
        return df, len(anomalies) > 1
    
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return None, True
    except Exception as e:
        print(f"❌ Error loading file: {str(e)}")
        return None, True

def main():
    """Main execution"""
    print("\n" + "="*80)
    print("DAY 1: DATA INGESTION & EXPLORATION")
    print("="*80)
    
    # Create directories
    ensure_directories()
    
    # List of 10 datasets to load (adjust file names as per your data)
    datasets = {
        "fund_master": f"{DATA_RAW}/fund_master.csv",
        "nav_history": f"{DATA_RAW}/nav_history.csv",
        "portfolio_holdings": f"{DATA_RAW}/portfolio_holdings.csv",
        "fund_performance": f"{DATA_RAW}/fund_performance.csv",
        "market_indices": f"{DATA_RAW}/market_indices.csv",
        "risk_metrics": f"{DATA_RAW}/risk_metrics.csv",
        "scheme_details": f"{DATA_RAW}/scheme_details.csv",
        "aum_history": f"{DATA_RAW}/aum_history.csv",
        "expense_ratios": f"{DATA_RAW}/expense_ratios.csv",
        "returns_history": f"{DATA_RAW}/returns_history.csv",
    }
    
    loaded_datasets = {}
    anomaly_summary = {}
    
    # Load and explore each dataset
    for name, path in datasets.items():
        df, has_anomalies = load_and_explore_dataset(path, name)
        if df is not None:
            loaded_datasets[name] = df
            anomaly_summary[name] = has_anomalies
    
    # Summary Report
    print(f"\n\n{'='*80}")
    print("SUMMARY REPORT")
    print(f"{'='*80}")
    
    print(f"\n✓ Successfully loaded: {len(loaded_datasets)}/{len(datasets)} datasets")
    
    print(f"\nDatasets with anomalies: {sum(anomaly_summary.values())}")
    for name, has_anomalies in anomaly_summary.items():
        status = "⚠️ " if has_anomalies else "✓"
        print(f"   {status} {name}")
    
    print(f"\n{'='*80}")
    print("✓ Data ingestion complete!")
    print("Next: Run live_nav_fetch.py to get live NAV data")
    print(f"{'='*80}\n")
    
    return loaded_datasets

if __name__ == "__main__":
    loaded_data = main()
