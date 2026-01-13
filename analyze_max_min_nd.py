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
    """
    df = df.copy()

    df[result_col] = df[result_col].astype(str).str.strip()
    df[analyte_col] = df[analyte_col].astype(str).str.strip()
    df[well_col] = df[well_col].astype(str).str.strip()
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

    df["Is_ND"] = (
        df[result_col].str.upper().eq("ND")
        | df[result_col].str.startswith("<")
    )

    def extract_numeric(val):
        try:
            val = str(val).strip()
            if val.upper() == "ND":
                return None
            if val.startswith("<"):
                return float(val.replace("<", "").strip())
            num = float(val)
            return num if num > 0 else None
        except Exception:
            return None

    df["Numeric"] = df[result_col].apply(extract_numeric)

    summary_rows = []
    nd_only_constituents = []

    for analyte, group in df.groupby(analyte_col):
        detected = group[group["Is_ND"] == False].dropna(subset=["Numeric"])

        if detected.empty:
            nd_only_constituents.append(analyte)
            summary_rows.append({
                "Constituent": analyte,
                "Max Value": "",
                "Well ID of Max": "",
                "Date of Max": "",
                "Min Value": "",
                "Well ID of Min": "",
                "Date of Min": "",
                "100% NDs": "Yes",
            })
            continue

        max_row = detected.loc[detected["Numeric"].idxmax()]
        min_row = detected.loc[detected["Numeric"].idxmin()]

        summary_rows.append({
            "Constituent": analyte,
            "Max Value": max_row[result_col],
            "Well ID of Max": max_row[well_col],
            "Date of Max": max_row[date_col].date() if pd.notna(max_row[date_col]) else "",
            "Min Value": min_row[result_col],
            "Well ID of Min": min_row[well_col],
            "Date of Min": min_row[date_col].date() if pd.notna(min_row[date_col]) else "",
            "100% NDs": "",
        })

    summary_df = pd.DataFrame(summary_rows)

    nd_statement = (
        "The following constituents resulted in 100% non-detect values: "
        + ", ".join(nd_only_constituents)
        if nd_only_constituents
        else "No constituents resulted in 100% non-detect values."
    )

    return summary_df, nd_only_constituents, nd_statement