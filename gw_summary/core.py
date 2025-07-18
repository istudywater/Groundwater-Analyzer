import pandas as pd


def load_data(path_or_buffer, sheet_name=None) -> pd.DataFrame:
    """
    Load an Excel file into a cleaned DataFrame.
    Accepts a file path or file-like buffer.
    Strips whitespace from column headers and returns the DataFrame.
    If the default sheet yields only one 'Unnamed' column, it switches to the next sheet.
    """
    # Try initial read
    df = pd.read_excel(path_or_buffer, sheet_name=sheet_name or 0, dtype=str, keep_default_na=False)
    df.columns = df.columns.str.strip()
    # If only one column or all columns unnamed, try the second sheet
    if len(df.columns) <= 1 or all(col.startswith('Unnamed') for col in df.columns):
        # Identify sheets and pick the second one if exists
        xls = pd.ExcelFile(path_or_buffer)
        if len(xls.sheet_names) > 1:
            df = pd.read_excel(path_or_buffer, sheet_name=xls.sheet_names[1], dtype=str, keep_default_na=False)
            df.columns = df.columns.str.strip()
    return df


def generate_gw_summary(
    lab_source,
    gwps_source,
    output_path: str,
    wells: list[str],
    sheet_name: str | None = None
) -> None:
    """
    Reads lab data and GWPS tables, then generates a groundwater monitoring summary Excel.
    """
    # Load data
    lab = load_data(lab_source, sheet_name)
    gwps = load_data(gwps_source)

    # Detect and rename sample ID column
    sample_cols = [c for c in lab.columns if 'client' in c.lower() and 'sample' in c.lower()]
    if not sample_cols:
        raise KeyError(f"No 'Client Sample ID' column found. Available columns: {list(lab.columns)}")
    lab.rename(columns={sample_cols[0]: 'Client Sample ID'}, inplace=True)

    # Filter by wells
    lab = lab[lab['Client Sample ID'].isin(wells)].copy()
    if lab.empty:
        raise ValueError(f"No lab records found for wells: {wells}")

    # Prepare fields
    lab['Analyte'] = lab['Analyte'].astype(str).str.strip()
    lab['High Limit'] = lab['High Limit'].astype(str).str.strip()

    # Clean GWPS columns
    gwps.columns = gwps.columns.str.strip()
    gwps.iloc[:,0] = gwps.iloc[:,0].astype(str).str.strip()
    gwps.iloc[:,1] = gwps.iloc[:,1].astype(str).str.strip()
    gwps_lookup = pd.Series(
        gwps.iloc[:,1].astype(float).values,
        index=gwps.iloc[:,0]
    )

    # Flag ND and formatted
    lab['Is_ND'] = lab['Result'].astype(str).str.strip().str.upper().eq('ND') | lab['Result'].astype(str).str.startswith('<')
    lab['Formatted'] = lab.apply(lambda r: f"<{r['High Limit']}" if r['Is_ND'] else r['Result'].strip(), axis=1)
    lab['Effective'] = lab.apply(lambda r: float(r['High Limit']) if r['Is_ND'] else float(r['Result'].lstrip('<').strip()), axis=1)

    # Aggregate
    agg = lab.groupby(['Analyte','Client Sample ID'], as_index=False).agg(
        Formatted=('Formatted','first'),
        Effective=('Effective','first'),
        Is_ND=('Is_ND','first'),
        DL=('High Limit','first')
    )

    # Pivot
    pivot = agg.pivot(index='Analyte', columns='Client Sample ID', values='Formatted').reindex(columns=wells)

    # Summaries
    mins, maxs, exc = [], [], []
    for analyte in pivot.index:
        sub = agg[agg['Analyte']==analyte].set_index('Client Sample ID').reindex(wells)
        nd, eff, fmt, dl = sub['Is_ND'], sub['Effective'], sub['Formatted'], sub['DL']
        if nd.any() and not nd.all(): mins.append(f"<{dl.iloc[0]}")
        elif nd.all(): mins.append(f"<{dl.iloc[0]}")
        else: mins.append(fmt.loc[eff.idxmin()])
        if (~nd).any(): maxs.append(fmt.loc[eff[~nd].idxmax()])
        else: maxs.append("100% ND")
        gwps_val = gwps_lookup.get(analyte,float('nan'))
        exc.append("N/A" if pd.isna(gwps_val) else ("Yes" if (eff>gwps_val).any() else "No"))
    pivot['Min'], pivot['Max'], pivot['GWPS Exceedance'] = mins, maxs, exc
    pivot.to_excel(output_path, sheet_name='Summary')
