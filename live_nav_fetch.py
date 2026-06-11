
import requests
import pandas as pd
import json
from datetime import datetime
from pathlib import Path


API_BASE = "https://api.mfapi.in/mf"


SCHEMES = {
    "HDFC Top 100 Direct": "125497",
    "SBI Bluechip": "119551",
    "ICICI Bluechip": "120503",
    "Nippon Large Cap": "118632",
    "Axis Bluechip": "119092",
    "Kotak Bluechip": "120841"
}

def ensure_directories():
    """Create data directory if it doesn't exist"""
    Path("data/raw").mkdir(parents=True, exist_ok=True)
    print("✓ Data directory ready\n")

def fetch_nav(scheme_code, scheme_name):
    """Fetch NAV data for a single scheme from API"""
    url = f"{API_BASE}/{scheme_code}"
    
    print(f"📡 Fetching: {scheme_name} (Code: {scheme_code})")
    print(f"   URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Check if response has data
        if "meta" not in data or "data" not in data:
            print(f" Invalid response format\n")
            return None

        meta = data.get("meta", {})
        nav_data = data.get("data", [])
        
        print(f"    Success!")
        print(f" Fund House: {meta.get('fundHouse', 'N/A')}")
        print(f" Scheme Name: {meta.get('schemeName', 'N/A')}")
        print(f" Total NAV Records: {len(nav_data)}")
        
        if nav_data:
            latest_nav = nav_data[0]
            print(f"   - Latest NAV: ₹{latest_nav.get('nav', 'N/A')} ({latest_nav.get('date', 'N/A')})")
        
        print()
        
        return {
            "scheme_code": scheme_code,
            "scheme_name": scheme_name,
            "meta": meta,
            "nav_data": nav_data
        }
    
    except requests.exceptions.RequestException as e:
        print(f"    Error: {str(e)}\n")
        return None

def save_nav_to_csv(scheme_code, scheme_name, nav_data):
    """Convert NAV data to DataFrame and save as CSV"""
    try:

        df = pd.DataFrame(nav_data)
        
        filename = f"data/raw/nav_live_{scheme_code}_{scheme_name.replace(' ', '_').lower()}.csv"
        df.to_csv(filename, index=False)
        
        print(f"     Saved: {filename}")
        print(f"   - Shape: {df.shape}")
        print(f"   - Columns: {list(df.columns)}\n")
        
        return df
    
    except Exception as e:
        print(f"    Error saving CSV: {str(e)}\n")
        return None

def main():
    """Main execution"""
    print("\n" + "="*80)
    print("DAY 1: LIVE NAV FETCH FROM MFAPI.IN")
    print("="*80 + "\n")
    
    ensure_directories()
    
    results = {}
    
    # Fetch data for all schemes
    for scheme_name, scheme_code in SCHEMES.items():
        nav_response = fetch_nav(scheme_code, scheme_name)
        
        if nav_response:
            results[scheme_name] = nav_response
            
            # Save to CSV
            df = save_nav_to_csv(
                scheme_code,
                scheme_name,
                nav_response["nav_data"]
            )
            
            if df is not None:
                results[scheme_name]["dataframe"] = df
    
    # Summary Report
    print("\n" + "="*80)
    print("SUMMARY REPORT")
    print("="*80 + "\n")
    
    print(f"✓ Successfully fetched: {len(results)}/{len(SCHEMES)} schemes\n")
    
    # Table of latest NAVs
    print("Latest NAV Summary:")
    print("-" * 80)
    print(f"{'Scheme Name':<35} {'NAV':<15} {'Date':<15}")
    print("-" * 80)
    
    for scheme_name, result in results.items():
        nav_data = result.get("nav_data", [])
        if nav_data:
            latest = nav_data[0]
            nav_value = latest.get("nav", "N/A")
            nav_date = latest.get("date", "N/A")
            print(f"{scheme_name:<35} {nav_value:<15} {nav_date:<15}")
    
    print("-" * 80)
    
    # Data Quality Check
    print("\nData Quality Checks:")
    print("-" * 80)
    
    for scheme_name, result in results.items():
        df = result.get("dataframe")
        if df is not None:
            missing = df.isnull().sum().sum()
            duplicates = df.duplicated().sum()
            status = "✓" if (missing == 0 and duplicates == 0) else "⚠️"
            print(f"{status} {scheme_name:<35} Missing: {missing}, Duplicates: {duplicates}")
    
    print("-" * 80)
    
    print(f"\n{'='*80}")
    print("✓ Live NAV fetch complete!")
    print("Next: Load and explore fund_master data for validation")
    print(f"{'='*80}\n")
    
    return results

if __name__ == "__main__":
    nav_data = main()
