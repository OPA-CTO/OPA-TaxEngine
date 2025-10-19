import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_parameters_json_exists_and_parseable():
    p = ROOT / "config" / "Parameters.json"
    assert p.exists(), "Parameters.json must exist in config/"
    data = json.loads(p.read_text())
    for key in ("Imports_Folder_Path", "Filing_Frequency", "Timezone"):
        assert key in data, f"Parameters.json missing required key: {key}"


def test_column_map_exists():
    p = ROOT / "config" / "Column_Map.csv"
    assert p.exists(), "config/Column_Map.csv must exist"
    text = p.read_text()
    assert "SKU" in text or "sku" in text, "Column_Map.csv should contain SKU mapping"


def test_pipeline_golden_scenarios():
    import sys
    sys.path.insert(0, str(ROOT))
    from pipeline.core import load_csv, normalize_orders, compute_fact, compute_summary
    data_dir = ROOT / 'tests' / 'data'
    orders = load_csv(data_dir / 'sample_orders.csv')
    tax_class = load_csv(data_dir / 'sample_tax_class.csv')
    machine_map = load_csv(data_dir / 'sample_machine_map.csv')
    rates = load_csv(data_dir / 'sample_jurisdiction_rates.csv')

    orders_n = normalize_orders(orders)
    fact = compute_fact(orders_n, tax_class, machine_map, rates)
    summary = compute_summary(fact)

    # find Twix (SKU-TWIX) in Castle Rock (80104) -> Local Only
    twix = fact[(fact['SKU'] == 'SKU-TWIX')].iloc[0]
    # Expected Twix tax: 1.50 * (0.081 - 0.029) = 0.078 -> rounded 0.08
    assert abs(twix['Line_Tax'] - 0.08) <= 0.02

    # Skittles in Lone Tree (80124) taxable full: 1.00 * 0.075 = 0.075 -> ~0.08
    sk = fact[(fact['SKU'] == 'SKU-SKITTLES')].iloc[0]
    assert abs(sk['Line_Tax'] - 0.08) <= 0.02

    # Water exempt -> 0
    water = fact[(fact['SKU'] == 'SKU-WATER')].iloc[0]
    assert water['Line_Tax'] == 0.0

    # Summary checks: Castle Rock (80104) tax collected should be approx twix+coffee
    castle = summary[summary['Jurisdiction_Code'] == 80104]
    assert not castle.empty
    castle_tax = float(castle.iloc[0]['Tax_Collected'])
    expected_castle = float(twix['Line_Tax'] + fact[(fact['SKU']=='SKU-COFFEE')]['Line_Tax'].sum())
    assert abs(castle_tax - expected_castle) <= 0.02

