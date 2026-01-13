import pandas as pd

def analyze_max_min_nd(df, well_col, analyte_col, result_col, date_col):
    df.columns = df.columns.str.strip()

    # Strip and uppercase the result column for consistent parsing
    df[result_col] = df[result_col].astype(str).str.strip()
    df['ND Flag'] = df[result_col].str.upper() == 'ND'
    
    # Remove entries where the well ID is blank (associated with lab QC results)
    df = df[df[well_col].notna() & (df[well_col].astype(str).str.strip() != "")]

    # Remove rows where Result is missing/blank
    clean_df = df[df[result_col].notna() & (df[result_col].str.strip() != "")]

    results = []
    nd_constituents = []

    for constituent, group in clean_df.groupby(analyte_col):
        group = group.copy()

        # Skip if the group has no valid rows
        if group.empty:
            continue

        # Check if all are ND
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

        # Convert values to numeric if not ND
        def try_float(val):
            try:
                return float(val)
            except:
                return None

        group["Result Value"] = group[~group['ND Flag']][result_col].apply(try_float)

        numeric_group = group.dropna(subset=["Result Value"])
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