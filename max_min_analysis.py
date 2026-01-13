import pandas as pd
import numpy as np


# ----------------------
# TESTING

print("✅ Using updated analyze_max_min_nd with well_col")

# -----------------------
def analyze_max_min_nd(
    df: pd.DataFrame,
    well_col: str,
    analyte_col: str,
    result_col: str,
    date_col: str,
):
    """
    Analyze minimum, maximum, and 100% non-detects from lab results.

    Parameters:
        df (pd.DataFrame): Full input dataframe containing lab data.
        well_col (str): Column name for well/sample IDs.
        analyte_col (str): Column name for analyte names.
        result_col (str): Column name for result values.
        date_col (str): Column name for collection dates.

    Returns:
        summary_df (pd.DataFrame): Summary table with max, min, and 100% ND info.
        nd_only (list): List of analytes with 100% non-detects.
        nd_statement (str): Printable statement listing those analytes.
    """

    df = df.copy()

    # Drop rows with missing critical fields
    df = df.dropna(subset=[well_col, analyte_col, result_col, date_col])

    # Standardize Result column to string
    df[result_col] = df[result_col].astype(str).str.strip()

    # Flag non-detects
    df["Is_ND"] = df[result_col].str.upper().eq("ND")

    # Parse numerical values for processing
    def parse_value(x):
        try:
            return float(x.lstrip("<").strip())
        except:
            return np.nan

    df["Value"] = df[result_col].apply(parse_value)

    grouped = df.groupby(analyte_col)

    summary = []
    nd_only = []

    for analyte, group in grouped:
        group = group.dropna(subset=["Value"])
        is_nd = group["Is_ND"]

        # Skip analytes with no values
        if group.empty:
            continue

        if is_nd.all():
            nd_only.append(analyte)

            summary.append({
                "Constituent": analyte,
                "Max Value": "BDL",
                "Well ID of Max": "",
                "Date of Max": "",
                "Min Value": "BDL",
                "Well ID of Min": "",
                "Date of Min": "",
                "100% NDs": "Yes",
            })
        else:
            max_row = group.loc[group["Value"].idxmax()]
            min_row = group.loc[group["Value"].idxmin()]

            summary.append({
                "Constituent": analyte,
                "Max Value": max_row["Value"],
                "Well ID of Max": max_row[well_col],
                "Date of Max": max_row[date_col],
                "Min Value": min_row["Value"],
                "Well ID of Min": min_row[well_col],
                "Date of Min": min_row[date_col],
                "100% NDs": "No" if not is_nd.all() else "Yes",
            })

    summary_df = pd.DataFrame(summary)

    if nd_only:
        nd_statement = "The following constituents resulted in 100% non-detect values: " + ", ".join(sorted(nd_only)) + "."
    else:
        nd_statement = "No constituents were found to be 100% non-detect."

    return summary_df, nd_only, nd_statement