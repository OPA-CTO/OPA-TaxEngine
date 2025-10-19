"""Production-style pipeline transformations for OPA-TaxEngine.

Features:
- Load CSV/Excel sources
- Normalize orders
- Join SKU -> tax class, Device -> machine map
- Match jurisdiction rates by effective date
- Decompose tax into components (state, local, rtd, special)
- Produce fact and summary outputs
- Basic validations (unmapped SKUs/Jurisdictions, coverage summary)
"""
from pathlib import Path
import pandas as pd
from datetime import datetime
from typing import Tuple


def read_table(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Source not found: {path}")
    if path.suffix.lower() in ('.xls', '.xlsx'):
        return pd.read_excel(path)
    return pd.read_csv(path)


def normalize_orders(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # canonical names expected by pipeline
    mapping = {
        'Timestamp': 'Txn_Date',
        'Txn_Date': 'Txn_Date',
        'Date': 'Txn_Date',
        'Device_Number': 'Device_Number',
        'Device': 'Device_Number',
        'SKU': 'SKU',
        'Net_Sales': 'Net_Sales',
    }
    for k, v in mapping.items():
        if k in df.columns and v not in df.columns:
            df = df.rename(columns={k: v})
    if 'Txn_Date' in df.columns:
        df['Txn_Date'] = pd.to_datetime(df['Txn_Date']).dt.date
    if 'Net_Sales' in df.columns:
        df['Net_Sales'] = pd.to_numeric(df['Net_Sales'], errors='coerce').fillna(0.0)
    return df


def expand_rates_for_transactions(orders: pd.DataFrame, rates: pd.DataFrame) -> pd.DataFrame:
    """Return a dataframe with one row per order x rate component where the rate is effective for that Txn_Date and jurisdiction."""
    # ensure date types
    rates = rates.copy()
    rates['Rate_Effective_From'] = pd.to_datetime(rates['Rate_Effective_From']).dt.date
    rates['Rate_Effective_To'] = pd.to_datetime(rates['Rate_Effective_To']).dt.date

    orders_exp = orders.copy()
    rates_copy = rates.copy()
    orders_exp['__join_key'] = 1
    rates_copy['__join_key'] = 1

    # detect jurisdiction column names in orders and rates
    possible_jur_cols = ['Jurisdiction_Code', 'Jurisdiction', 'JurisdictionCode', 'Jurisdiction Code']
    left_jur = next((c for c in orders_exp.columns if c in possible_jur_cols), None)
    right_jur = next((c for c in rates_copy.columns if c in possible_jur_cols), None)
    # create a normalized join column 'JUR' on both frames
    orders_exp['JUR'] = orders_exp[left_jur] if left_jur is not None else pd.NA
    rates_copy['JUR'] = rates_copy[right_jur] if right_jur is not None else pd.NA

    # perform merge on join_key + JUR so only matching jurisdictions are combined
    merged = orders_exp.merge(rates_copy, on=['__join_key', 'JUR'])
    # filter by effective date window
    merged = merged[merged['Rate_Effective_From'] <= merged['Txn_Date']]
    merged = merged[merged['Txn_Date'] <= merged['Rate_Effective_To']]
    # Ensure a canonical Jurisdiction_Code exists for downstream
    # handle cases where pandas added suffixes like _x/_y during merge
    if left_jur and left_jur in merged.columns:
        merged['Jurisdiction_Code'] = merged[left_jur]
    elif f"{left_jur}_x" in merged.columns:
        merged['Jurisdiction_Code'] = merged[f"{left_jur}_x"]
    elif f"{left_jur}_y" in merged.columns:
        merged['Jurisdiction_Code'] = merged[f"{left_jur}_y"]
    elif right_jur and right_jur in merged.columns:
        merged['Jurisdiction_Code'] = merged[right_jur]
    elif f"{right_jur}_x" in merged.columns:
        merged['Jurisdiction_Code'] = merged[f"{right_jur}_x"]
    elif f"{right_jur}_y" in merged.columns:
        merged['Jurisdiction_Code'] = merged[f"{right_jur}_y"]
    elif 'JUR' in merged.columns:
        merged['Jurisdiction_Code'] = merged['JUR']
    else:
        merged['Jurisdiction_Code'] = pd.NA
    # clean helper columns
    drop_cols = [c for c in ['__join_key', 'JUR'] if c in merged.columns]
    merged = merged.drop(columns=drop_cols)
    return merged


def compute_components(orders_rates_expanded: pd.DataFrame) -> pd.DataFrame:
    """Given expanded orders x rate components, compute per-component tax amounts and aggregate to lines."""
    df = orders_rates_expanded.copy()
    df['Rate'] = pd.to_numeric(df['Rate'], errors='coerce').fillna(0.0)
    df['Component_Tax'] = (df['Net_Sales'] * df['Rate']).round(4)

    # If an order's Assumed_Taxability says 'Local Only', zero out State component
    df['Assumed_Taxability'] = df.get('Assumed_Taxability', pd.Series([''] * len(df)))
    mask_local_only = df['Assumed_Taxability'].str.lower().str.contains('local') & df['Assumed_Taxability'].str.lower().str.contains('only')
    state_mask = df['Component'].str.lower() == 'state'
    df.loc[mask_local_only & state_mask, 'Component_Tax'] = 0.0

    # aggregate back to per-order row using a unique OrderID
    df = df.reset_index(drop=True)
    df['OrderID'] = df.index
    per_order = df.groupby('OrderID').agg(
        Net_Sales=('Net_Sales', 'first'),
        Jurisdiction_Code=('Jurisdiction_Code', 'first'),
        SKU=('SKU', 'first'),
        Device_Number=('Device_Number', 'first'),
        Txn_Date=('Txn_Date', 'first')
    ).reset_index()

    # pivot component taxes into columns
    comp = df.pivot_table(index='OrderID', columns='Component', values='Component_Tax', aggfunc='sum', fill_value=0.0)
    comp.columns = [f"Tax_{c.replace(' ', '_')}" for c in comp.columns]
    per_order = per_order.merge(comp, on='OrderID', how='left')
    # total tax
    tax_cols = [c for c in per_order.columns if c.startswith('Tax_')]
    per_order['Tax_Total'] = per_order[tax_cols].sum(axis=1).round(2)
    # round components
    for c in tax_cols:
        per_order[c] = per_order[c].round(2)
    return per_order


def build_fact(orders: pd.DataFrame, tax_class: pd.DataFrame, machine_map: pd.DataFrame, jurisdiction_rates: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Build the transaction-level fact and validation reports.

    Returns (fact_df, validation_df)
    """
    orders_n = normalize_orders(orders)

    # Join SKU -> tax class
    # tax_class expected to include SKU key column (named SKU) or Class_Key
    tc = tax_class.copy()
    if 'SKU' not in tc.columns and 'Class_Key' in tc.columns:
        tc = tc.rename(columns={'Class_Key': 'SKU'})

    fact_base = orders_n.merge(tc, on='SKU', how='left')

    # Join device -> machine_map
    mm = machine_map.copy()
    fact_base = fact_base.merge(mm, on='Device_Number', how='left')

    # Expand rates and compute component taxes
    # Expand: merge fact_base with jurisdiction_rates by cartesian then filter by jurisdiction and effective dates
    expanded = expand_rates_for_transactions(fact_base, jurisdiction_rates.copy())

    # compute component taxes and aggregate
    fact = compute_components(expanded)

    # Validations
    unmapped_skus = fact_base[fact_base['Class'].isna()][['SKU']].drop_duplicates()
    unmapped_jurisdictions = fact_base[fact_base['Jurisdiction_Code'].isna()][['Device_Number']].drop_duplicates()
    validations = {
        'unmapped_skus': unmapped_skus,
        'unmapped_jurisdictions': unmapped_jurisdictions
    }

    return fact, validations


def build_summary(fact_df: pd.DataFrame) -> pd.DataFrame:
    # roll-up by jurisdiction
    summary = fact_df.groupby('Jurisdiction_Code', dropna=False).agg(
        Taxable_Sales=pd.NamedAgg(column='Net_Sales', aggfunc='sum'),
        Tax_Collected=pd.NamedAgg(column='Tax_Total', aggfunc='sum')
    ).reset_index()
    summary['Taxable_Sales'] = summary['Taxable_Sales'].round(2)
    summary['Tax_Collected'] = summary['Tax_Collected'].round(2)
    return summary
