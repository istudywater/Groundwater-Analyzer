import pandas as pd
from io import BytesIO


def load_data(path_or_buffer, sheet_name=None) -> pd.DataFrame:
    """
    Load an Excel file into a cleaned DataFrame.
    Accepts a file path or file-like buffer.
    Strips whitespace from column headers and returns the DataFrame.
    If the default sheet yields only one 'Unnamed' column, it switches to the next sheet.
    """
    df = pd.read_excel(
        path_or_buffer,
        sheet_name=sheet_name or 0,
        dtype=str,
        keep_default_na=False,
    )
    df.columns = df.columns.str.strip()

    # If only one column or all columns unnamed, try second sheet
    if len(df.columns) <= 1 or all(col.startswith("Unnamed") for col in df.columns):
        xls = pd.ExcelFile(path_or_buffer)
        if len(xls.sheet_names) > 1:
            df = pd.read_excel(
                path_or_buffer,
                sheet_name=xls.sheet_names[1],
                dtype=str,
                keep_default_na=False,
            )
            df.columns = df.columns.str.strip()

    return df


def generate_gw_summary(
    lab_source,
    gwps_source,
    output_path=None,
    wells=None,
    wells_source=None,
    sheet_name=None,
):
    """
    Generate a groundwater monitoring summary table.

    Parameters
    ----------
    lab_source : path or BytesIO
        Laboratory analytical data
    gwps_source : path or BytesIO
        GWPS table
    output_path : str or None
        Optional Excel output path
    wells : list[str] or None
        Explicit list of wells (highest priority)
    wells_source : path or BytesIO or None
        Optional file containing wells list (first column assumed)
    sheet_name : str or None
        Sheet name for lab data

    Returns
    -------
    pd.DataFrame
        Summary table
    """

    # ------------------------------------------------------------
    # Load data
    # ------------------------------------------------------------
    lab_df = load_data(lab_source, sheet_name=sheet_name)
    gwps_df = load_data(gwps_source)

    # ------------------------------------------------------------
    # Detect and standardize Client Sample ID column
    # ------------------------------------------------------------
    sample_cols = [
        c for c in lab_df.columns
        if "client" in c.lower() and "sample" in c.lower()
    ]
    if not sample_cols:
        raise KeyError(
            f"No 'Client Sample ID' column found. Available columns: {list(lab_df.columns)}"
        )

    lab_df.rename(columns={sample_cols[0]: "Client Sample ID"}, inplace=True)
    lab_df["Client Sample ID"] = lab_df["Client Sample ID"].astype(str).str.strip()

    # ------------------------------------------------------------
    # Load wells list (optional)
    # Priority: wells (explicit) > wells_source > all wells
    # ------------------------------------------------------------
    if wells is not None:
        wells = [str(w).strip() for w in wells]

    elif wells_source is not None:
        try:
            if isinstance(wells_source, BytesIO):
                wells_df = pd.read_excel(wells_source)
            else:
                wells_df = pd.read_excel(wells_source)
        except Exception:
            wells_df = pd.read_csv(wells_source)

        wells_df.columns = wells_df.columns.str.strip()
        wells = (
            wells_df.iloc[:, 0]
            .astype(str)
            .str.strip()
            .unique()
            .tolist()
        )

    else:
        wells = sorted(lab_df["Client Sample ID"].unique().tolist())

    # Filter lab data to wells
    lab_df = lab_df[lab_df["Client Sample ID"].isin(wells)].copy()
    if lab_df.empty:
        raise ValueError(f"No lab records found for wells: {wells}")

    # ------------------------------------------------------------
    # Prepare fields
    # ------------------------------------------------------------
    required_cols = ["Analyte", "Result", "High Limit"]
    for col in required_cols:
        if col not in lab_df.columns:
            raise KeyError(f"Required column missing from lab data: {col}")

    lab_df["Analyte"] = lab_df["Analyte"].astype(str).str.strip()
    lab_df["Result"] = lab_df["Result"].astype(str).str.strip()
    lab_df["High Limit"] = lab_df["High Limit"].astype(str).str.strip()

    # ------------------------------------------------------------
    # Prepare GWPS lookup
    # ------------------------------------------------------------
    gwps_df.iloc[:, 0] = gwps_df.iloc[:, 0].astype(str).str.strip()
    gwps_df.iloc[:, 1] = gwps_df.iloc[:, 1].astype(str).str.strip()

    gwps_lookup = pd.Series(
        gwps_df.iloc[:, 1].astype(float).values,
        index=gwps_df.iloc[:, 0],
    )

    # ------------------------------------------------------------
    # ND handling and numeric surrogate
    # ------------------------------------------------------------
    lab_df["Is_ND"] = (
        lab_df["Result"].str.upper().eq("ND")
        | lab_df["Result"].str.startswith("<")
    )

    lab_df["Formatted"] = lab_df.apply(
        lambda r: f"<{r['High Limit']}" if r["Is_ND"] else r["Result"],
        axis=1,
    )

    lab_df["Effective"] = lab_df.apply(
        lambda r: float(r["High Limit"])
        if r["Is_ND"]
        else float(r["Result"].lstrip("<").strip()),
        axis=1,
    )

    # ------------------------------------------------------------
    # Aggregate per analyte / well
    # ------------------------------------------------------------
    agg = lab_df.groupby(
        ["Analyte", "Client Sample ID"],
        as_index=False,
    ).agg(
        Formatted=("Formatted", "first"),
        Effective=("Effective", "first"),
        Is_ND=("Is_ND", "first"),
        DL=("High Limit", "first"),
    )

    # ------------------------------------------------------------
    # Pivot table
    # ------------------------------------------------------------
    pivot = (
        agg.pivot(index="Analyte", columns="Client Sample ID", values="Formatted")
        .reindex(columns=wells)
    )

    # ------------------------------------------------------------
    # Min / Max / GWPS Exceedance
    # ------------------------------------------------------------
    mins, maxs, exc = [], [], []

    for analyte in pivot.index:
        sub = (
            agg[agg["Analyte"] == analyte]
            .set_index("Client Sample ID")
            .reindex(wells)
        )

        nd = sub["Is_ND"]
        eff = sub["Effective"]
        fmt = sub["Formatted"]
        dl = sub["DL"]

        # Min
        if nd.all():
            mins.append(f"<{dl.dropna().iloc[0]}")
        elif nd.any():
            mins.append(f"<{dl.dropna().iloc[0]}")
        else:
            mins.append(fmt.loc[eff.idxmin()])

        # Max
        if (~nd).any():
            maxs.append(fmt.loc[eff[~nd].idxmax()])
        else:
            maxs.append("100% ND")

        # GWPS exceedance
        gwps_val = gwps_lookup.get(analyte, float("nan"))
        if pd.isna(gwps_val):
            exc.append("N/A")
        else:
            exc.append("Yes" if (eff > gwps_val).any() else "No")

    pivot["Min"] = mins
    pivot["Max"] = maxs
    pivot["GWPS Exceedance"] = exc

    # ------------------------------------------------------------
    # Output
    # ------------------------------------------------------------
    if output_path:
        pivot.to_excel(output_path, sheet_name="Summary")

    return pivot