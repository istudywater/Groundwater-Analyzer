import pandas as pd


def analyze_max_min_nd(
    df: pd.DataFrame,
    well_col: str,
    analyte_col: str,
    result_col: str,
    date_col: str,
):
    """
    Analyze max/min detections by constituent and identify 100% ND analytes.

    Parameters
    ----------
    df : pd.DataFrame
        Long-format analytical dataset
    well_col : str
        Column name containing well IDs
    analyte_col : str
        Column name containing analyte / constituent names
    result_col : str
        Column name containing result values (numeric or 'ND')
    date_col : str
        Column name containing sample date

    Returns
    -------
    summary_df : pd.DataFrame
        Summary table with max/min values and metadata
    nd_only : list[str]
        List of constituents that are 100% ND
    """

    # ------------------------------------------------------------
    # Normalize column names and values
    # ------------------------------------------------------------
    df = df.copy()
    df.columns = df.columns.str.strip()

    df[result_col] = df[result_col].astype(str).str.strip()
    df[analyte_col] = df[analyte_col].astype(str).str.strip()
    df[well_col] = df[well_col].astype(str).str.strip()

    # ------------------------------------------------------------
    # ND flagging (STRICT: ND only)
    # ------------------------------------------------------------
    df["ND Flag"] = df[result_col].str.upper() == "ND"

    # ------------------------------------------------------------
    # Numeric extraction (ignore ND rows)
    # ------------------------------------------------------------
    def to_float(val):
        try:
            return float(val)
        except:
            return None

    df["Numeric Value"] = df[result_col].apply(to_float)

    # ------------------------------------------------------------
    # Per-constituent analysis
    # ------------------------------------------------------------
    results = []
    nd_constituents = []

    for constituent, group in df.groupby(analyte_col):
        group = group.copy()

        # --------------------------------------------
        # Case 1: 100% ND
        # --------------------------------------------
        if group["ND Flag"].all():
            nd_constituents.append(constituent)
            results.append({
                "Constituent": constituent,
                "Max Value": "BDL",
                "Well ID of Max": "Not Applicable",
                "Date of Max": "Not Applicable",
                "Min Value": "BDL",
                "Well ID of Min": "Not Applicable",
                "Date of Min": "Not Applicable",
                "100% NDs": "Yes",
            })
            continue

        # --------------------------------------------
        # Case 2: At least one numeric value exists
        # --------------------------------------------
        numeric_group = group[
            (~group["ND Flag"]) & (group["Numeric Value"].notna())
        ]

        if numeric_group.empty:
            # Defensive fallback (should be rare)
            nd_constituents.append(constituent)
            results.append({
                "Constituent": constituent,
                "Max Value": "BDL",
                "Well ID of Max": "Not Applicable",
                "Date of Max": "Not Applicable",
                "Min Value": "BDL",
                "Well ID of Min": "Not Applicable",
                "Date of Min": "Not Applicable",
                "100% NDs": "Yes",
            })
            continue

        max_row = numeric_group.loc[numeric_group["Numeric Value"].idxmax()]
        min_row = numeric_group.loc[numeric_group["Numeric Value"].idxmin()]

        results.append({
            "Constituent": constituent,
            "Max Value": max_row[result_col],
            "Well ID of Max": max_row[well_col],
            "Date of Max": pd.to_datetime(max_row[date_col]).date(),
            "Min Value": min_row[result_col],
            "Well ID of Min": min_row[well_col],
            "Date of Min": pd.to_datetime(min_row[date_col]).date(),
            "100% NDs": "",
        })

    summary_df = pd.DataFrame(results)

    return summary_df, nd_constituents