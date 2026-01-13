import pandas as pd

def analyze_max_min_nd(df, well_col, analyte_col, result_col, date_col):
    df = df.copy()
    df.columns = df.columns.str.strip()

    # Normalize and strip string values
    df[well_col] = df[well_col].astype(str).str.strip()
    df[analyte_col] = df[analyte_col].astype(str).str.strip()
    df[result_col] = df[result_col].astype(str).str.strip()
    df[date_col] = df[date_col].astype(str).str.strip()

    # Flag ND if value is not a valid float (e.g., "ND", "<0.5", "--", etc.)
    def is_nd(val):
        try:
            float(val)
            return False
        except:
            return True

    df["ND Flag"] = df[result_col].apply(is_nd)
    df["Result Value"] = pd.to_numeric(df[result_col], errors="coerce")

    summary = []
    nd_only = []

    for analyte, group in df.groupby(analyte_col):
        group = group.copy()

        if group["ND Flag"].all():
            nd_only.append(analyte)
            summary.append({
                "Constituent": analyte,
                "Max Value": "",
                "Well ID of Max": "",
                "Date of Max": "",
                "Min Value": "",
                "Well ID of Min": "",
                "Date of Min": "",
                "100% NDs": "Yes"
            })
            continue

        valid = group[~group["ND Flag"] & group["Result Value"].notna()]
        if valid.empty:
            continue

        max_row = valid.loc[valid["Result Value"].idxmax()]
        min_row = valid.loc[valid["Result Value"].idxmin()]

        summary.append({
            "Constituent": analyte,
            "Max Value": max_row[result_col],
            "Well ID of Max": max_row[well_col],
            "Date of Max": max_row[date_col],
            "Min Value": min_row[result_col],
            "Well ID of Min": min_row[well_col],
            "Date of Min": min_row[date_col],
            "100% NDs": ""
        })

    summary_df = pd.DataFrame(summary)
    return summary_df, nd_only