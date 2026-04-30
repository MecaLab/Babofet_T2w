import os.path
import sys
import pandas as pd
from pathlib import Path
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg

def generate_raw_summary(bids_root_path):
    """
    Scans a BIDS dataset to count .nii.gz files across anat, dwi, and func folders.
    Returns a formatted pandas DataFrame.
    """
    bids_root = Path(bids_root_path)
    raw_data_path = bids_root / 'sourcedata' / 'raw'

    if not raw_data_path.exists() or not raw_data_path.is_dir():
        print(f"Error: The path {raw_data_path} does not exist.")
        return None

    records = []
    # You need to add the folder you want to process
    modalities_to_check = ['anat', 'dwi', 'func']

    for subject_dir in raw_data_path.glob('sub-*'):
        if not subject_dir.is_dir():
            continue

        subject_id = subject_dir.name

        for session_dir in subject_dir.glob('ses-*'):
            if not session_dir.is_dir():
                continue

            session_id = session_dir.name

            # Check each modality folder
            for modality in modalities_to_check:
                modality_dir = session_dir / modality

                if modality_dir.exists() and modality_dir.is_dir():
                    # Count all files ending with .nii.gz
                    nifti_files = list(modality_dir.glob('*.nii.gz'))
                    file_count = len(nifti_files)

                    records.append({
                        'Subject': subject_id,
                        'Session': session_id,
                        'Modality': modality,
                        'File_Count': file_count
                    })

    # Convert the collected data into a DataFrame
    df = pd.DataFrame(records)

    if df.empty:
        print("No .nii.gz files were found in the specified structure.")
        return df

    # Create a pivot table for a cleaner, matrix-like display
    summary_table = pd.pivot_table(
        df,
        values='File_Count',
        index=['Subject', 'Session'],
        columns=['Modality'],
        fill_value=0,
        aggfunc='sum'
    )

    return summary_table


def generate_derivatives_summary(bids_root_path):
    """
    Scans the derivatives folder and checks specific file patterns for:
    longiseg, niftymic, surf-slam, and mrtrix pipelines.
    """
    bids_root = Path(bids_root_path)
    derivatives_path = bids_root / 'derivatives'

    if not derivatives_path.exists():
        print(f"Error: Derivatives folder not found at {derivatives_path}")
        return None

    # Define the rules for each pipeline
    # Format: pipeline_name: (subfolder_type, file_pattern)
    pipeline_rules = {
        'longiseg': ('anat', '*.nii.gz'),
        'niftymic': ('anat', '*niftymic_desc-brainbg_T2w.nii.gz'),
        'surf-slam': ('anat', '*.gii'),
        'mrtrix': ('dwi', '*_tensor.nii.gz')
    }

    records = []

    for pipeline, (modality, pattern) in pipeline_rules.items():
        pipeline_dir = derivatives_path / pipeline

        if not pipeline_dir.exists():
            continue

        # Iterate over subjects
        for subject_dir in pipeline_dir.glob('sub-*'):
            if not subject_dir.is_dir():
                continue

            subject_id = subject_dir.name

            # Iterate over sessions
            for session_dir in subject_dir.glob('ses-*'):
                if not session_dir.is_dir():
                    continue

                session_id = session_dir.name
                target_dir = session_dir / modality

                count = 0
                if target_dir.exists() and target_dir.is_dir():
                    files = list(target_dir.glob(pattern))
                    count = len(files)

                records.append({
                    'Pipeline': pipeline,
                    'Subject': subject_id,
                    'Session': session_id,
                    'File_Count': count
                })

    df = pd.DataFrame(records)

    if df.empty:
        print("No derivative files found matching the criteria.")
        return df

    # Create a pivot table to see pipelines as columns
    # Note: pd.pivot_table sorts columns alphabetically by default
    summary_table = pd.pivot_table(
        df,
        values='File_Count',
        index=['Subject', 'Session'],
        columns=['Pipeline'],
        fill_value=0
    )

    # Reorder columns to place 'niftymic' before 'mrtrix'
    desired_order = ['niftymic', 'longiseg', 'mrtrix', 'surf-slam']

    # Keep only the columns that exist in the dataframe to avoid errors
    # in case a pipeline directory was completely empty or missing
    ordered_columns = [col for col in desired_order if col in summary_table.columns]

    # Apply the correct order to the dataframe
    summary_table = summary_table[ordered_columns]

    return summary_table


def generate_bids_reports(derivatives_file, sourcedata_file):
    # Load and merge datasets
    df_deriv = pd.read_csv(derivatives_file)
    df_source = pd.read_csv(sourcedata_file)

    df = pd.merge(df_source, df_deriv, on=['Subject', 'Session'], how='outer')

    # Handle missing values
    df = df.fillna(0)

    # Sort values
    df = df.sort_values(by=['Subject', 'Session'])

    # Format the session string
    df['Session'] = '📅 ' + df['Session'].astype(str)

    # Initialize markdown content
    markdown_content = "# 🚀 BIDS Summary Report 🚀\n\n"

    # Loop through each subject to create separated sections
    for subject, group_data in df.groupby('Subject'):
        # Add a header for each subject
        markdown_content += f"## 👤 {subject} ✨\n\n"

        # Remove the 'Subject' column
        clean_group = group_data.drop(columns=['Subject']).copy()

        # Apply specific rules based on the column name
        cols_to_check = [col for col in clean_group.columns if col != 'Session']

        for col in cols_to_check:
            if col == 'longiseg':
                # Rule for 'longiseg': 1 becomes '✅', 0 becomes '❌', others remain unchanged
                clean_group[col] = clean_group[col].apply(
                    lambda x: '✅' if x == 1 else ('❌' if x == 0 else x)
                )
            elif col == 'surf-slam':
                # Rule for 'surf-slam': 2 becomes '✅', 0 becomes '❌', others remain unchanged
                clean_group[col] = clean_group[col].apply(
                    lambda x: '✅' if x == 2 else ('❌' if x == 0 else '1/2 ⚠️')
                )
            elif col == "niftymic" or col == "mrtrix":
                # Rule: 1 becomes '✅', 0 becomes '❌'
                clean_group[col] = clean_group[col].apply(
                    lambda x: '✅' if x == 1 else '❌'
                )
            else:
                # Default rule for all other columns: 0 becomes '❌', others remain unchanged
                clean_group[col] = clean_group[col].apply(
                    lambda x: '❌' if x == 0 else x
                )

        # Append the formatted table to the markdown content
        markdown_content += clean_group.to_markdown(index=False)

        # Add a visual separator
        markdown_content += "\n\n---\n\n"

    # Save the report to a file
    with open('../bids_summary.md', 'w', encoding='utf-8') as file:
        file.write(markdown_content)


# --- Execution ---
if __name__ == "__main__":
    DATABASE_PATH = cfg.BASE_BIDS_PATH

    raw_csv_path = "bids_summary_sourcedata.csv"
    derivatives_csv_path = "bids_summary_derivatives.csv"

    if not os.path.exists(raw_csv_path):
        result_table = generate_raw_summary(DATABASE_PATH)
        if result_table is not None and not result_table.empty:
            result_table.to_csv(raw_csv_path)

    if not os.path.exists(derivatives_csv_path):
        derivatives_summary = generate_derivatives_summary(DATABASE_PATH)
        if derivatives_summary is not None and not derivatives_summary.empty:

            derivatives_summary.to_csv(derivatives_csv_path)

    generate_bids_reports(
        derivatives_file=derivatives_csv_path,
        sourcedata_file=raw_csv_path
    )
