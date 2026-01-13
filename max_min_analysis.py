import pandas as pd

def analyze_max_min_nd(
    df: pd.DataFrame,
    well_col: str,
    analyte_col: str,
    result_col: str,
    date_col: str
):
    """Analyze max, min, and 100% ND constituents."""

    # Clean headers and values
    df.columns = df.columns.str.strip()
    df[analyte_col] = df[analyte_col].astype(str).str.strip()
    df[well_col] = df[well_col].astype(str).str.strip()
    df[result_col] = df[result_col].astype(str).str.strip()
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

    # Flag ND results (treat exact "ND", case-insensitive, as non-detect)
    df["ND Flag"] = df[result_col].str.upper() == "ND"

    # Convert results to float where possible
    def to_numeric(val):
        try:
            return float(val)
        except ValueError:
            return None

    df["Result Value"] = df[result_col].apply(to_numeric)

    results = []
    nd_only_list = []

    grouped = df.groupby(analyte_col)
    for analyte, group in grouped:
        group = group.copy()

        if group["ND Flag"].all():
            nd_only_list.append(analyte)
            results.append({
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

        numeric_data = group[~group["ND Flag"] & group["Result Value"].notna()]
        if numeric_data.empty:
            continue

        max_row = numeric_data.loc[numeric_data["Result Value"].idxmax()]
        min_row = numeric_data.loc[numeric_data["Result Value"].idxmin()]

        results.append({
            "Constituent": analyte,
            "Max Value": max_row[result_col],
            "Well ID of Max": max_row[well_col],
            "Date of Max": max_row[date_col].strftime("%Y-%m-%d") if pd.notnull(max_row[date_col]) else "",
            "Min Value": min_row[result_col],
            "Well ID of Min": min_row[well_col],
            "Date of Min": min_row[date_col].strftime("%Y-%m-%d") if pd.notnull(min_row[date_col]) else "",
            "100% NDs": ""
        })

    return pd.DataFrame(results), nd_only_list