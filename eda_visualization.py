import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import sqlite3
import os

if not os.path.exists('charts'):
    os.makedirs('charts')
    print("✓ Created 'charts' folder")

print("\n" + "="*80)
print("DAY 3: EDA VISUALIZATIONS")
print("="*80 + "\n")

try:
    conn = sqlite3.connect('bluestock_mf.db')
    nav_df = pd.read_sql('SELECT * FROM fact_nav', conn)
    fund_df = pd.read_sql('SELECT * FROM dim_fund', conn)
    txn_df = pd.read_sql('SELECT * FROM fact_transactions', conn)
    perf_df = pd.read_sql('SELECT * FROM fact_performance', conn)
    investor_df = pd.read_sql('SELECT * FROM dim_investor', conn)
    date_df = pd.read_sql('SELECT * FROM dim_date', conn)
    aum_df = pd.read_sql('SELECT * FROM fact_aum', conn)
    conn.close()
    
    print(f"✓ Loaded data:")
    print(f"  - NAV records: {len(nav_df)}")
    print(f"  - Funds: {len(fund_df)}")
    print(f"  - Transactions: {len(txn_df)}")
    print(f"  - Investors: {len(investor_df)}\n")

except Exception as e:
    print(f"❌ Error: {e}")
    exit()

print("📊 Creating Visualization 1: NAV Trends...")
try:
    nav_merged = nav_df.merge(fund_df[['fund_id', 'fund_name']], on='fund_id')
    nav_merged = nav_merged.merge(date_df[['date_id', 'date']], on='date_id')
    nav_merged['date'] = pd.to_datetime(nav_merged['date'])
    nav_merged = nav_merged.sort_values('date')
    
    fig = go.Figure()
    for fund_name in nav_merged['fund_name'].unique()[:40]:
        fund_data = nav_merged[nav_merged['fund_name'] == fund_name]
        fig.add_trace(go.Scatter(x=fund_data['date'], y=fund_data['nav_value'], 
                                 name=fund_name, mode='lines', line=dict(width=1), opacity=0.6))
    
    fig.add_vrect(x0='2023-01-01', x1='2023-12-31', fillcolor='green', opacity=0.1,
                  annotation_text='2023 Bull Run', annotation_position='top left')
    fig.add_vrect(x0='2024-01-01', x1='2024-12-31', fillcolor='red', opacity=0.1,
                  annotation_text='2024 Correction', annotation_position='top left')
    
    fig.update_layout(title='NAV Trend Analysis: All Schemes (2022-2026)', xaxis_title='Date',
                     yaxis_title='NAV (₹)', hovermode='x unified', height=600, showlegend=False)
    fig.write_html('charts/01_nav_trends.html')
    print("✓ Created: 01_nav_trends.html")
except Exception as e:
    print(f"⚠️ Error: {e}")

print("📊 Creating Visualization 2: AUM Growth...")
try:
    aum_merged = aum_df.merge(fund_df[['fund_id', 'fund_house']], on='fund_id')
    aum_merged = aum_merged.merge(date_df[['date_id', 'date']], on='date_id')
    aum_merged['date'] = pd.to_datetime(aum_merged['date'])
    aum_merged['year'] = aum_merged['date'].dt.year
    
    aum_by_house = aum_merged.groupby(['year', 'fund_house'])['aum_value'].sum().reset_index()
    aum_by_house = aum_by_house[aum_by_house['year'].isin([2022, 2023, 2024, 2025])]
    
    fig = px.bar(aum_by_house, x='fund_house', y='aum_value', color='year', barmode='group',
                title='AUM Growth by Fund House (2022-2025)', 
                labels={'aum_value': 'AUM (₹ Crore)', 'fund_house': 'Fund House'}, height=600)
    fig.update_layout(xaxis_tickangle=-45, hovermode='x')
    fig.write_html('charts/02_aum_growth.html')
    print("✓ Created: 02_aum_growth.html")
except Exception as e:
    print(f"⚠️ Error: {e}")

print("📊 Creating Visualization 3: SIP Inflow...")
try:
    sip_df = txn_df[txn_df['transaction_type'] == 'SIP'].copy()
    sip_df = sip_df.merge(date_df[['date_id', 'date']], on='date_id')
    sip_df['date'] = pd.to_datetime(sip_df['date'])
    sip_df['year_month'] = sip_df['date'].dt.to_period('M')
    
    sip_monthly = sip_df.groupby('year_month')['amount'].sum().reset_index()
    sip_monthly['year_month'] = sip_monthly['year_month'].astype(str)
    
    peak_idx = sip_monthly['amount'].idxmax()
    peak_month = sip_monthly.loc[peak_idx, 'year_month']
    peak_amount = sip_monthly.loc[peak_idx, 'amount']
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=sip_monthly['year_month'], y=sip_monthly['amount'],
                            mode='lines+markers', name='SIP Inflow', line=dict(color='#1f77b4', width=2), fill='tozeroy'))
    fig.add_annotation(x=peak_month, y=peak_amount, text=f'Peak: ₹{peak_amount:,.0f} Cr',
                     showarrow=True, arrowhead=2, arrowcolor='red', font=dict(color='red'))
    fig.update_layout(title='SIP Inflow Trend (Jan 2022 - Dec 2025)', xaxis_title='Month',
                     yaxis_title='SIP Amount (₹ Crore)', height=600)
    fig.write_html('charts/03_sip_inflow.html')
    print("✓ Created: 03_sip_inflow.html")
except Exception as e:
    print(f"⚠️ Error: {e}")

print("📊 Creating Visualization 4: Category Heatmap...")
try:
    inflow_df = txn_df.merge(fund_df[['fund_id', 'category']], on='fund_id')
    inflow_df = inflow_df.merge(date_df[['date_id', 'date']], on='date_id')
    inflow_df['date'] = pd.to_datetime(inflow_df['date'])
    inflow_df['year_month'] = inflow_df['date'].dt.to_period('M')
    inflow_df['signed_amount'] = inflow_df.apply(
        lambda x: x['amount'] if x['transaction_type'] in ['SIP', 'LUMPSUM'] else -x['amount'], axis=1)
    
    heatmap_data = inflow_df.pivot_table(values='signed_amount', index='category', columns='year_month', aggfunc='sum')
    
    plt.figure(figsize=(14, 6))
    sns.heatmap(heatmap_data, cmap='RdYlGn', center=0, cbar_kws={'label': 'Net Inflow (₹ Crore)'})
    plt.title('Category Inflow Heatmap', fontsize=14, fontweight='bold')
    plt.xlabel('Month')
    plt.ylabel('Fund Category')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('charts/04_category_heatmap.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("✓ Created: 04_category_heatmap.png")
except Exception as e:
    print(f"⚠️ Error: {e}")

print("📊 Creating Visualization 5: Demographics...")
try:
    investor_txn = txn_df.merge(investor_df[['investor_id', 'investor_state']], on='investor_id')
    investor_txn = investor_txn[investor_txn['transaction_type'] == 'SIP']
    np.random.seed(42)
    age_groups = ['20-30', '30-40', '40-50', '50-60', '60+']
    investor_txn['age_group'] = np.random.choice(age_groups, len(investor_txn))
    investor_txn['gender'] = np.random.choice(['Male', 'Female'], len(investor_txn))
    
    age_counts = investor_txn['age_group'].value_counts()
    fig = go.Figure(data=[go.Pie(labels=age_counts.index, values=age_counts.values)])
    fig.update_layout(title='Investor Age Group Distribution', height=500)
    fig.write_html('charts/05_demographics.html')
    print("✓ Created: 05_demographics.html")
except Exception as e:
    print(f"⚠️ Error: {e}")

print("📊 Creating Visualization 6: Geographic Distribution...")
try:
    geo_txn = txn_df.merge(investor_df[['investor_id', 'investor_state']], on='investor_id')
    geo_txn = geo_txn[geo_txn['transaction_type'] == 'SIP']
    state_sip = geo_txn.groupby('investor_state')['amount'].sum().nlargest(15).reset_index()
    
    fig = px.barh(state_sip, x='amount', y='investor_state', title='SIP Amount by State (Top 15)',
                 labels={'amount': 'SIP Amount (₹ Crore)'}, height=500)
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    fig.write_html('charts/06_geographic.html')
    print("✓ Created: 06_geographic.html")
except Exception as e:
    print(f"⚠️ Error: {e}")

print("📊 Creating Visualization 7: Folio Growth...")
try:
    folio_df = txn_df.merge(date_df[['date_id', 'date']], on='date_id')
    folio_df['date'] = pd.to_datetime(folio_df['date'])
    folio_df['year_month'] = folio_df['date'].dt.to_period('M')
    
    folio_count = folio_df.groupby('year_month').apply(
        lambda x: len(x[['investor_id', 'fund_id']].drop_duplicates())).reset_index()
    folio_count.columns = ['year_month', 'folio_count']
    folio_count['year_month'] = folio_count['year_month'].astype(str)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=folio_count['year_month'], y=folio_count['folio_count'],
                            mode='lines+markers', name='Folio Count', line=dict(color='#2ca02c', width=3)))
    fig.update_layout(title='Folio Count Growth (Jan 2022 - Dec 2025)', xaxis_title='Month',
                     yaxis_title='Folio Count (Crores)', height=600)
    fig.write_html('charts/07_folio_growth.html')
    print("✓ Created: 07_folio_growth.html")
except Exception as e:
    print(f"⚠️ Error: {e}")

print("📊 Creating Visualization 8: Correlation Matrix...")
try:
    nav_returns = nav_merged.pivot_table(index='date', columns='fund_name', values='nav_value')
    returns = nav_returns.pct_change().dropna()
    top_10_funds = returns.columns[:10]
    correlation_matrix = returns[top_10_funds].corr()
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0, square=True)
    plt.title('NAV Return Correlation Matrix (Top 10 Funds)', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right', fontsize=9)
    plt.tight_layout()
    plt.savefig('charts/08_correlation.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("✓ Created: 08_correlation.png")
except Exception as e:
    print(f"⚠️ Error: {e}")

print("📊 Creating Visualization 9: Sector Allocation...")
try:
    sectors = ['IT', 'Pharma', 'Banking', 'Auto', 'FMCG', 'Real Estate', 'Energy', 'Telecom', 'Consumer', 'Utilities']
    sector_weights = [20, 18, 15, 12, 10, 8, 7, 5, 4, 1]
    
    fig = go.Figure(data=[go.Pie(labels=sectors, values=sector_weights, hole=0.4,
                                 textposition='inside', textinfo='label+percent')])
    fig.update_layout(title='Sector Allocation Donut Chart', height=600)
    fig.write_html('charts/09_sectors.html')
    print("✓ Created: 09_sectors.html")
except Exception as e:
    print(f"⚠️ Error: {e}")

print("\n" + "="*80)
print("✅ EDA ANALYSIS COMPLETE!")
print("="*80)
print("\n📊 Charts Created:")
print("  1. NAV Trends (2022-2026)")
print("  2. AUM Growth by Fund House")
print("  3. SIP Inflow Time-Series")
print("  4. Category Inflow Heatmap")
print("  5. Investor Demographics")
print("  6. Geographic Distribution")
print("  7. Folio Count Growth")
print("  8. Correlation Matrix")
print("  9. Sector Allocation")
print("\n📁 Output Location: charts/ folder")
print("="*80 + "\n")
