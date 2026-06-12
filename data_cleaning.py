
Cleans nav_history, investor_transactions, scheme_performance datasets


import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

DATA_RAW = "data/raw"
DATA_PROCESSED = "data/processed"

def ensure_directories():
    """Create processed data directory"""
    Path(DATA_PROCESSED).mkdir(parents=True, exist_ok=True)
    print("✓ Directories ready\n")

def clean_nav_history():
    """Clean nav_history.csv"""
    print("="*80)
    print("CLEANING: nav_history.csv")
    print("="*80 + "\n")
    
    try:
        df = pd.read_csv(f"{DATA_RAW}/nav_history.csv")
        print(f" Loaded: {df.shape[0]} rows, {df.shape[1]} columns")
        
       
        print("\n  Parsing dates...")
        date_cols = [col for col in df.columns if 'date' in col.lower()]
        for col in date_cols:
            try:
                df[col] = pd.to_datetime(df[col])
                print(f"    Converted '{col}' to datetime")
            except:
                print(f"     Could not convert '{col}'")
        
       
        print("\n  Sorting by amfi_code + date...")
        amfi_col = [col for col in df.columns if 'amfi' in col.lower() or 'code' in col.lower()]
        if amfi_col and date_cols:
            df = df.sort_values(by=[amfi_col[0], date_cols[0]])
            print(f"    Sorted")
       
        print("\n  Forward-filling missing NAV values...")
        nav_cols = [col for col in df.columns if 'nav' in col.lower()]
        for col in nav_cols:
            missing_before = df[col].isnull().sum()
            df[col] = df[col].fillna(method='ffill')
            missing_after = df[col].isnull().sum()
            print(f"    '{col}': {missing_before} → {missing_after} missing")
        
        print("\n  Removing duplicates...")
        dup_before = len(df)
        df = df.drop_duplicates()
        dup_after = len(df)
        print(f"    Removed {dup_before - dup_after} duplicate rows")
        
        print("\n  Validating NAV > 0...")
        for col in nav_cols:
            invalid = (df[col] <= 0).sum()
            if invalid > 0:
                print(f"     '{col}': {invalid} values ≤ 0 (removing)")
                df = df[df[col] > 0]
            else:
                print(f"    '{col}': All values > 0")
        
    
        output_file = f"{DATA_PROCESSED}/nav_history_cleaned.csv"
        df.to_csv(output_file, index=False)
        print(f"\n✓ Saved: {output_file}")
        print(f"  Final shape: {df.shape[0]} rows, {df.shape[1]} columns\n")
        
        return df
    
    except FileNotFoundError:
        print(" nav_history.csv not found\n")
        return None

def clean_investor_transactions():
    """Clean investor_transactions.csv"""
    print("="*80)
    print("CLEANING: investor_transactions.csv")
    print("="*80 + "\n")
    
    try:
        df = pd.read_csv(f"{DATA_RAW}/investor_transactions.csv")
        print(f"📥 Loaded: {df.shape[0]} rows, {df.shape[1]} columns")
        
        
        print("\n1️⃣  Standardising transaction_type...")
        txn_col = [col for col in df.columns if 'type' in col.lower() or 'transaction' in col.lower()]
        if txn_col:
            col_name = txn_col[0]
            print(f"   Original values: {df[col_name].unique()}")
            df[col_name] = df[col_name].str.upper().str.strip()
            valid_types = ['SIP', 'LUMPSUM', 'REDEMPTION', 'SWITCH']
            df[col_name] = df[col_name].replace({
                'LUMPSUMP': 'LUMPSUM',
                'LUMP SUM': 'LUMPSUM',
                'REDEEM': 'REDEMPTION',
                'SWITCHIN': 'SWITCH',
                'SWITCHOUT': 'SWITCH'
            })
            print(f"   Cleaned values: {df[col_name].unique()}")
            invalid = ~df[col_name].isin(valid_types)
            if invalid.sum() > 0:
                print(f"     {invalid.sum()} invalid values (removing)")
                df = df[~invalid]
            print(f"   ✓ Standardised")
        
        print("\n  Validating amount > 0...")
        amt_cols = [col for col in df.columns if 'amount' in col.lower() or 'value' in col.lower()]
        for col in amt_cols:
            invalid = (df[col] <= 0).sum()
            if invalid > 0:
                print(f"     '{col}': {invalid} values ≤ 0 (removing)")
                df = df[df[col] > 0]
            else:
                print(f"    '{col}': All values > 0")
        
        print("\n  Fixing date formats...")
        date_cols = [col for col in df.columns if 'date' in col.lower()]
        for col in date_cols:
            try:
                df[col] = pd.to_datetime(df[col])
                print(f"    Converted '{col}' to datetime")
            except:
                print(f"     Could not convert '{col}'")
        
      
        print("\n  Validating KYC status...")
        kyc_cols = [col for col in df.columns if 'kyc' in col.lower()]
        for col in kyc_cols:
            print(f"   Values in '{col}': {df[col].unique()}")
            valid_kyc = ['APPROVED', 'PENDING', 'REJECTED', 'VERIFIED']
            invalid_kyc = ~df[col].isin(valid_kyc)
            if invalid_kyc.sum() > 0:
                print(f"     {invalid_kyc.sum()} invalid KYC values")

        output_file = f"{DATA_PROCESSED}/investor_transactions_cleaned.csv"
        df.to_csv(output_file, index=False)
        print(f"\n✓ Saved: {output_file}")
        print(f"  Final shape: {df.shape[0]} rows, {df.shape[1]} columns\n")
        
        return df
    
    except FileNotFoundError:
        print(" investor_transactions.csv not found\n")
        return None

def clean_scheme_performance():
    """Clean scheme_performance.csv"""
    print("="*80)
    print("CLEANING: scheme_performance.csv")
    print("="*80 + "\n")
    
    try:
        df = pd.read_csv(f"{DATA_RAW}/scheme_performance.csv")
        print(f"📥 Loaded: {df.shape[0]} rows, {df.shape[1]} columns")
        
      
        print("\n1️⃣  Validating return values are numeric...")
        return_cols = [col for col in df.columns if 'return' in col.lower()]
        for col in return_cols:
            try:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                invalid = df[col].isnull().sum()
                if invalid > 0:
                    print(f"    '{col}': {invalid} non-numeric values (removing)")
                    df = df.dropna(subset=[col])
                print(f"    '{col}': All numeric")
            except:
                print(f"    Error converting '{col}'")
        
   
        print("\n  Checking for anomalies...")
        for col in return_cols:
            mean_val = df[col].mean()
            std_val = df[col].std()
            anomalies = (df[col] > mean_val + 3*std_val) | (df[col] < mean_val - 3*std_val)
            if anomalies.sum() > 0:
                print(f"   ⚠️  '{col}': {anomalies.sum()} anomalies (beyond 3σ)")
            else:
                print(f"   ✓ '{col}': No anomalies detected")
        
     
        print("\n  Validating expense_ratio (0.1% - 2.5%)...")
        exp_cols = [col for col in df.columns if 'expense' in col.lower()]
        for col in exp_cols:
            try:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                invalid = (df[col] < 0.1) | (df[col] > 2.5)
                if invalid.sum() > 0:
                    print(f"    '{col}': {invalid.sum()} values outside range (removing)")
                    df = df[~invalid]
                else:
                    print(f"    '{col}': All values in valid range")
            except:
                print(f"    Error validating '{col}'")
        
      
        output_file = f"{DATA_PROCESSED}/scheme_performance_cleaned.csv"
        df.to_csv(output_file, index=False)
        print(f"\n✓ Saved: {output_file}")
        print(f"  Final shape: {df.shape[0]} rows, {df.shape[1]} columns\n")
        
        return df
    
    except FileNotFoundError:
        print(" scheme_performance.csv not found\n")
        return None

def main():
    """Main execution"""
    print("\n" + "="*80)
    print("DAY 2: DATA CLEANING")
    print("="*80 + "\n")
    
    ensure_directories()
    
    
    nav_df = clean_nav_history()
    txn_df = clean_investor_transactions()
    perf_df = clean_scheme_performance()
    
  
    print("\n" + "="*80)
    print("CLEANING SUMMARY")
    print("="*80 + "\n")
    
    if nav_df is not None:
        print(f" nav_history.csv: {nav_df.shape[0]} rows")
    if txn_df is not None:
        print(f" investor_transactions.csv: {txn_df.shape[0]} rows")
    if perf_df is not None:
        print(f"scheme_performance.csv: {perf_df.shape[0]} rows")
    
    print(f"\n✓ All cleaned files saved to: {DATA_PROCESSED}/")
    print("Next: Run database_schema.py to create SQLite database\n")

if __name__ == "__main__":
    main()
