import pandas as pd

def analyze_max_min_nd(df, well_col, analyte_col, result_col, date_col):
    df.columns = df.columns.str.strip()

    # Drop blank rows in required columns
    df = df.dropna(subset=[analyte_col, result_col])

    # Normalize result column
    df[result_col] = df[result_col].astype(str).str.strip()
    df['ND Flag'] = df[result_col].str.upper() == 'ND'

    # Convert results to float where possible
    def try_float(val):
        try:
            return float(val)
        except ValueError:
            return None

    df['Result Value'] = df[result_col].apply(try_float)

    results = []
    nd_constituents = []

    for constituent, group in df.groupby(analyte_col):
        group = group.copy()

        # Drop rows with empty results
        group = group[~group[result_col].isna()]
        group = group[group[result_col] != ""]

        if group.empty:
            continue

        if group['ND Flag'].all():
            nd_constituents.append(constituent)
            results.append({
                "Constituent": constituent,
                "Max Value": "",
                "Well ID of Max": "",
                "Date of Max": "",
                "Min Value": "",
                "Well ID of Min": "",
                "Date of Min": "",
                "100% NDs": "Yes"
            })
            continue

        numeric_group = group[group['ND Flag'] == False].dropna(subset=["Result Value"])
        if numeric_group.empty:
            continue

        max_row = numeric_group.loc[numeric_group["Result Value"].idxmax()]
        min_row = numeric_group.loc[numeric_group["Result Value"].idxmin()]

        results.append({
            "Constituent": constituent,
            "Max Value": max_row[result_col],
            "Well ID of Max": max_row[well_col],
            "Date of Max": max_row[date_col],
            "Min Value": min_row[result_col],
            "Well ID of Min": min_row[well_col],
            "Date of Min": min_row[date_col],
            "100% NDs": ""
        })

    result_df = pd.DataFrame(results)
    return result_df, nd_constituents