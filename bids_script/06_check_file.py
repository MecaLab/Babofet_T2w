import pandas as pd
from pathlib import Path


def generate_bids_summary_table(bids_root_path):
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
    modalities_to_check = ['anat', 'dwi', 'func']

    # Iterate over all subject directories
    for subject_dir in raw_data_path.glob('sub-*'):
        if not subject_dir.is_dir():
            continue

        subject_id = subject_dir.name

        # Iterate over all session directories for the current subject
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


# --- Execution ---
if __name__ == "__main__":
    # Replace the string below with the actual absolute or relative path to your BIDS database
    DATABASE_PATH = "/envau/work/meca/data/BaboFet_BIDS"

    result_table = generate_bids_summary_table(DATABASE_PATH)

    if result_table is not None and not result_table.empty:
        print("--- NIfTI Files Count Summary ---")
        print(result_table)