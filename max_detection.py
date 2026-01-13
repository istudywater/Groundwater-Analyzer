import pandas as pd

def load_data(file_path):
    """Load Excel file and return DataFrame."""
    df = pd.read_excel(file_path, dtype=str)
    df.columns = df.columns.str.strip()
    return df

def analyze_max_min_nd(df):
    df.columns = df.columns.str.strip()

    # Ensure columns exist
    required_cols = ['Constituent', 'Result', 'Client Sample ID', 'Date']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    # Normalize result column
    df['Result'] = df['Result'].astype(str).str.strip()
    df['ND Flag'] = df['Result'].str.upper() == 'ND'

    # Try to extract numeric values where possible
    def try_float(val):
        try:
            return float(val)
        except ValueError:
            return None

    df['Result Value'] = df['Result'].apply(try_float)

    results = []
    nd_constituents = []

    for constituent, group in df.groupby("Constituent"):
        group = group.copy()

        if group['ND Flag'].all():
            # All values are ND
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

        # Filter out rows that aren't numeric
        numeric_group = group[group["ND Flag"] == False].dropna(subset=["Result Value"])
        if numeric_group.empty:
            continue

        max_row = numeric_group.loc[numeric_group["Result Value"].idxmax()]
        min_row = numeric_group.loc[numeric_group["Result Value"].idxmin()]

        results.append({
            "Constituent": constituent,
            "Max Value": max_row["Result"],
            "Well ID of Max": max_row["Client Sample ID"],
            "Date of Max": max_row["Date"],
            "Min Value": min_row["Result"],
            "Well ID of Min": min_row["Client Sample ID"],
            "Date of Min": min_row["Date"],
            "100% NDs": ""
        })

    result_df = pd.DataFrame(results)
    return result_df, nd_constituents

if __name__ == "__main__":
    # Replace this with your file path
    input_file = "2025-2H WNB Data2.xlsx"

    df = load_data(input_file)
    summary_df, nd_only = analyze_max_min_nd(df)

    # Save to Excel
    output_file = "Max_Detection_Summary.xlsx"
    summary_df.to_excel(output_file, index=False)
    print(f"✅ Summary saved to {output_file}")

    # Print list of constituents that were 100% ND
    if nd_only:
        print("\n🧪 Constituents with 100% ND results:")
        for c in nd_only:
            print(f" - {c}")
    else:
        print("\n✅ No constituents were 100% ND.")