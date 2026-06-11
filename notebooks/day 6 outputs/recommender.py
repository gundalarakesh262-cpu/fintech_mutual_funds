"""
Fund Recommender — Bluestock MF Dashboard
Usage: python recommender.py
"""
import pandas as pd

sp = pd.read_csv("07_scheme_performance.csv")

def recommend_funds(risk_appetite):
    filtered = sp[sp["risk_grade"] == risk_appetite]
    top3 = filtered.nlargest(3, "sharpe_ratio")[
        ["scheme_name","category","sharpe_ratio","return_3yr_pct","std_dev_ann_pct","risk_grade"]
    ].reset_index(drop=True)
    top3.index += 1
    return top3

def main():
    print("=" * 65)
    print("        BLUESTOCK MUTUAL FUND RECOMMENDER")
    print("=" * 65)
    risk = input("\nEnter risk appetite (Low / Moderate / High): ").strip().capitalize()
    if risk not in ["Low","Moderate","High"]:
        print("Invalid! Please enter Low, Moderate or High.")
        return
    result = recommend_funds(risk)
    print(f"\n✅ Top 3 Recommended Funds for {risk} Risk:\n")
    print(result.to_string())
    print("\n" + "="*65)

if __name__ == "__main__":
    main()
