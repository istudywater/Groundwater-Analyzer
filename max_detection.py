
import pandas as pd

def analyze_max_detection(input_file, output_file):
    df = pd.read_excel(input_file)

    # Clean up: Remove trailing and leading whitespace and special characters
    df.columns = df.columns.str.strip()
    df['Result'] = df['Result'].astype(str).str.replace('<<', '<', regex=False).str.strip()
    df['Result'] = df['Result'].replace('', 'NR')

    # Convert date to datetime and remove time from min date
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    summary = []

    for analyte in df['Analyte'].unique():
        analyte_df = df[df['Analyte'] == analyte].copy()

        # Filter valid results (exclude NR, ND, NS)
        numeric_df = analyte_df[analyte_df['Result'].str.contains(r'^[<>]?\d', na=False)].copy()
        numeric_df['Result_clean'] = numeric_df['Result'].str.replace('<', '', regex=False).astype(float)

        if not numeric_df.empty:
            max_row = numeric_df.loc[numeric_df['Result_clean'].idxmax()]
            min_candidates = numeric_df[numeric_df['Result'].str.contains('<')]
            if not min_candidates.empty:
                min_row = min_candidates.loc[min_candidates['Result_clean'].idxmin()]
                min_val, min_well, min_date = min_row['Result'], min_row['Client Sample ID'], min_row['Date'].date()
            else:
                min_val, min_well, min_date = 'No Data', 'Not Applicable', 'Not Applicable'

            summary.append({
                'Constituent': analyte,
                'Max Value': max_row['Result'],
                'Well ID of Max': max_row['Client Sample ID'],
                'Date of Max': max_row['Date'].date(),
                'Min Value': min_val,
                'Well ID of Min': min_well,
                'Date of Min': min_date
            })
        else:
            summary.append({
                'Constituent': analyte,
                'Max Value': 'No Data',
                'Well ID of Max': 'Not Applicable',
                'Date of Max': 'Not Applicable',
                'Min Value': 'No Data',
                'Well ID of Min': 'Not Applicable',
                'Date of Min': 'Not Applicable'
            })

    result_df = pd.DataFrame(summary)
    result_df.to_excel(output_file, index=False)
    return result_df
