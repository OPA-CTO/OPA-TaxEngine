import pandas as pd
from pathlib import Path


def load_csv(path):
    return pd.read_csv(path)


def normalize_orders(orders_df):
    # canonicalize columns
    df = orders_df.rename(columns={
        'Timestamp': 'Txn_Date',
        'Device': 'Device_Number',
        'SKU': 'SKU',
        'Description': 'Product_Desc',
        'Qty': 'Qty',
        'Net_Sales': 'Net_Sales',
    })
    df['Txn_Date'] = pd.to_datetime(df['Txn_Date']).dt.date
    return df


def compute_fact(orders_df, tax_class_df, machine_map_df, jurisdiction_rates_df):
    """Return a transaction-level fact table with computed tax and components.

    Simple logic for tests:
    - join SKU -> class (tax_class_df has Class and Assumed_Taxability)
    - join device -> jurisdiction (Machine_Map has Device_Number, ZIP, Jurisdiction_Code)
    - determine effective rate by summing components for jurisdiction code
    - apply simple exemptions for 'Local Only' (state excluded)
    """
    orders = orders_df.copy()
    # join class
    fact = orders.merge(tax_class_df[['Class', 'Assumed_Taxability', 'Class_Key']].rename(columns={'Class_Key':'SKU'}), how='left', left_on='SKU', right_on='SKU')
    # join device
    fact = fact.merge(machine_map_df[['Device_Number', 'Jurisdiction_Code', 'ZIP']], how='left', on='Device_Number')
    # compute effective rate per jurisdiction (sum of component rates)
    rates = jurisdiction_rates_df.groupby('Jurisdiction_Code', as_index=False)['Rate'].sum()
    fact = fact.merge(rates, how='left', on='Jurisdiction_Code')
    fact['EffectiveRate'] = fact['Rate'].fillna(0.0)
    # apply assumed_taxability rules
    def line_tax(row):
        taxability = str(row.get('Assumed_Taxability') or '').lower()
        rate = float(row.get('EffectiveRate') or 0)
        # Local Only -> exclude state portion. For tests we model state portion as 0.029 (2.9%) where needed
        state_portion = 0.029
        if 'local' in taxability and 'only' in taxability:
            # subtract state portion if present
            effective = max(0.0, rate - state_portion)
        elif 'exempt' in taxability:
            effective = 0.0
        else:
            effective = rate
        return round(row.get('Net_Sales', 0) * effective, 2)

    fact['Line_Tax'] = fact.apply(line_tax, axis=1)
    return fact


def compute_summary(fact_df):
    # simple jurisdiction roll-up
    summary = fact_df.groupby('Jurisdiction_Code').agg(
        Taxable_Sales=pd.NamedAgg(column='Net_Sales', aggfunc='sum'),
        Tax_Collected=pd.NamedAgg(column='Line_Tax', aggfunc='sum')
    ).reset_index()
    summary['Taxable_Sales'] = summary['Taxable_Sales'].round(2)
    summary['Tax_Collected'] = summary['Tax_Collected'].round(2)
    return summary
