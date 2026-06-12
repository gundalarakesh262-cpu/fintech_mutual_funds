
Day 1: Fund Master Exploration & AMFI Validation Script


import pandas as pd
import numpy as np
from pathlib import Path

def load_data():
    """Load fund_master and nav_history datasets"""
    print("\n" + "="*80)
    print("DAY 1: FUND MASTER EXPLORATION & AMFI VALIDATION")
    print("="*80 + "\n")
    
    try:
        fund_master = pd.read_csv("data/raw/fund_master.csv")
        print(" Loaded fund_master.csv")
        print(f"  Shape: {fund_master.shape}\n")
    except FileNotFoundError:
        print(" fund_master.csv not found")
        return None, None
    
    try:
        nav_history = pd.read_csv("data/raw/nav_history.csv")
        print(" Loaded nav_history.csv")
        print(f"  Shape: {nav_history.shape}\n")
    except FileNotFoundError:
        print("  nav_history.csv not found (will skip validation)")
        nav_history = None
    
    return fund_master, nav_history

def explore_fund_master(df):
    """Explore fund_master structure and unique values"""
    print("="*80)
    print("FUND MASTER EXPLORATION")
    print("="*80 + "\n")
    
    # 1. Schema
    print(" Schema:")
    print(df.dtypes)
    print()
    
 
    if 'Fund House' in df.columns or 'fundHouse' in df.columns:
        col_name = 'Fund House' if 'Fund House' in df.columns else 'fundHouse'
        fund_houses = df[col_name].unique()
        print(f"\n Unique Fund Houses: {len(fund_houses)}")
        for i, house in enumerate(fund_houses[:20], 1):
            print(f"   {i:2d}. {house}")
        if len(fund_houses) > 20:
            print(f"   ... and {len(fund_houses) - 20} more")

    if 'Category' in df.columns or 'category' in df.columns:
        col_name = 'Category' if 'Category' in df.columns else 'category'
        categories = df[col_name].unique()
        print(f"\n Unique Categories: {len(categories)}")
        for i, cat in enumerate(categories, 1):
            print(f"   {i:2d}. {cat}")
    
  
    if 'Sub Category' in df.columns or 'subcategory' in df.columns:
        col_name = 'Sub Category' if 'Sub Category' in df.columns else 'subcategory'
        subcats = df[col_name].unique()
        print(f"\n Unique Sub-Categories: {len(subcats)}")
        for i, subcat in enumerate(subcats[:15], 1):
            print(f"   {i:2d}. {subcat}")
        if len(subcats) > 15:
            print(f"   ... and {len(subcats) - 15} more")
    
    if 'Risk Grade' in df.columns or 'riskGrade' in df.columns:
        col_name = 'Risk Grade' if 'Risk Grade' in df.columns else 'riskGrade'
        risk_grades = df[col_name].unique()
        print(f"\n⚡ Unique Risk Grades: {len(risk_grades)}")
        for grade in sorted(risk_grades):
            count = (df[col_name] == grade).sum()
            print(f"   {grade}: {count} schemes")
   
    print(f"\n Sample Schemes:")
    print(df.head(10))

def understand_amfi_structure(df):
    """Understand AMFI scheme code structure"""
    print("\n" + "="*80)
    print("AMFI SCHEME CODE STRUCTURE")
    print("="*80 + "\n")
    
   
    code_col = None
    for col in df.columns:
        if 'code' in col.lower() or 'amfi' in col.lower():
            code_col = col
            break
    
    if code_col is None:
        print("  Could not find AMFI scheme code column")
        return
    
    print(f"Scheme Code Column: '{code_col}'")
    print(f"Total Schemes: {len(df)}")
    print(f"Unique Codes: {df[code_col].nunique()}")
    print(f"Code Data Type: {df[code_col].dtype}")
    
    print(f"\nSample AMFI Codes:")
    for code in df[code_col].head(10):
        print(f"   {code}")
    
    print(f"\nCode Statistics:")
    print(f"   Min Code: {df[code_col].min()}")
    print(f"   Max Code: {df[code_col].max()}")
    print(f"   Null Codes: {df[code_col].isnull().sum()}")
    
    return code_col

def validate_amfi_codes(fund_master, nav_history):
    """Validate that all AMFI codes in fund_master exist in nav_history"""
    print("\n" + "="*80)
    print("AMFI CODE VALIDATION")
    print("="*80 + "\n")

    fm_code_col = None
    nh_code_col = None
    
    for col in fund_master.columns:
        if 'code' in col.lower() or 'scheme' in col.lower():
            fm_code_col = col
            break
    
    for col in nav_history.columns:
        if 'code' in col.lower() or 'scheme' in col.lower():
            nh_code_col = col
            break
    
    if fm_code_col is None or nh_code_col is None:
        print("  Could not find scheme code columns for validation")
        return {}
    
    fm_codes = set(fund_master[fm_code_col].dropna().unique())
    nh_codes = set(nav_history[nh_code_col].dropna().unique())
    
    print(f"Fund Master Codes: {len(fm_codes)}")
    print(f"NAV History Codes: {len(nh_codes)}")
    
    # Validation
    missing_in_nav = fm_codes - nh_codes
    extra_in_nav = nh_codes - fm_codes
    
    print(f"\n Codes in both: {len(fm_codes & nh_codes)}")
    print(f" Codes in fund_master but NOT in nav_history: {len(missing_in_nav)}")
    print(f"  Codes in nav_history but NOT in fund_master: {len(extra_in_nav)}")
    
    if missing_in_nav:
        print(f"\n   Missing Codes (first 10):")
        for code in list(missing_in_nav)[:10]:
            print(f"      {code}")
        if len(missing_in_nav) > 10:
            print(f"      ... and {len(missing_in_nav) - 10} more")
    
    return {
        "fm_codes": len(fm_codes),
        "nh_codes": len(nh_codes),
        "matched": len(fm_codes & nh_codes),
        "missing": len(missing_in_nav),
        "extra": len(extra_in_nav)
    }

def generate_quality_summary(fund_master, nav_history, validation):
    """Generate comprehensive data quality summary"""
    print("\n" + "="*80)
    print("DATA QUALITY SUMMARY")
    print("="*80 + "\n")
    
    summary = {
        "timestamp": pd.Timestamp.now(),
        "datasets": {
            "fund_master": {
                "rows": len(fund_master),
                "columns": len(fund_master.columns),
                "missing_values": fund_master.isnull().sum().sum(),
                "duplicate_rows": fund_master.duplicated().sum(),
                "memory_mb": fund_master.memory_usage(deep=True).sum() / 1024**2
            }
        }
    }
    
    if nav_history is not None:
        summary["datasets"]["nav_history"] = {
            "rows": len(nav_history),
            "columns": len(nav_history.columns),
            "missing_values": nav_history.isnull().sum().sum(),
            "duplicate_rows": nav_history.duplicated().sum(),
            "memory_mb": nav_history.memory_usage(deep=True).sum() / 1024**2
        }
    
    summary["validation"] = validation
    
    # Print summary
    print(" Fund Master:")
    print(f"   Rows: {summary['datasets']['fund_master']['rows']:,}")
    print(f"   Columns: {summary['datasets']['fund_master']['columns']}")
    print(f"   Missing Values: {summary['datasets']['fund_master']['missing_values']}")
    print(f"   Duplicate Rows: {summary['datasets']['fund_master']['duplicate_rows']}")
    print(f"   Memory: {summary['datasets']['fund_master']['memory_mb']:.2f} MB")
    
    if "nav_history" in summary["datasets"]:
        print("\n NAV History:")
        print(f"   Rows: {summary['datasets']['nav_history']['rows']:,}")
        print(f"   Columns: {summary['datasets']['nav_history']['columns']}")
        print(f"   Missing Values: {summary['datasets']['nav_history']['missing_values']}")
        print(f"   Duplicate Rows: {summary['datasets']['nav_history']['duplicate_rows']}")
        print(f"   Memory: {summary['datasets']['nav_history']['memory_mb']:.2f} MB")
    
    print("\n Validation Summary:")
    if validation:
        print(f"   Matched Scheme Codes: {validation['matched']}")
        print(f"   Missing in NAV History: {validation['missing']}")
        print(f"   Extra in NAV History: {validation['extra']}")
    
   
    summary_file = "data/processed/day1_quality_summary.txt"
    Path("data/processed").mkdir(parents=True, exist_ok=True)
    
    with open(summary_file, "w") as f:
        f.write("DAY 1: DATA QUALITY SUMMARY\n")
        f.write("="*80 + "\n\n")
        f.write(str(summary))
    
    print(f"\n Summary saved to: {summary_file}")
    
    return summary

def main():
    """Main execution"""
    fund_master, nav_history = load_data()
    
    if fund_master is None:
        print(" Cannot proceed without fund_master.csv")
        return
    
   
    explore_fund_master(fund_master)
    

    understand_amfi_structure(fund_master)
    
   
    validation = {}
    if nav_history is not None:
        validation = validate_amfi_codes(fund_master, nav_history)
    

    quality_summary = generate_quality_summary(fund_master, nav_history, validation)
    
    print("\n" + "="*80)
    print("✓ Fund exploration and validation complete!")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
