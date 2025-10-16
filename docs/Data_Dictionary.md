# Data Dictionary (Fields expected downstream)

## Taxability_Map
- class_category (Text; UPPER(TRIM(Class/Category)); unique)
- assumed_taxability (Text; "Taxable" | "Exempt")
- rule_code (Text; enum; see contract)
- class_notes (Text)
- Tax_Class_Version (Text)
- Source_File (Text)
- Source_Sheet (Text)

## OPA_SalesTax_Fact_Rows (selected)
- device_id, device_name
- jurisdiction_code, jurisdiction_name
- timestamp, order_date
- gtin, description, class_category
- assumed_taxability_final, rule_code
- Taxability_Override_Source, Taxability_Decision_Path
- Eff_State_Rate, Eff_Local_Rate, Eff_Total_Rate
- extended_price, qty, discount
- Taxable_Gross, NonTax_Gross, True_Sales, Sales_Tax_Computed
- Source_File, Source_Sheet
