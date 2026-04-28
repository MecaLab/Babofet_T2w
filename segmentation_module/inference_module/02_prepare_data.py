import os
import shutil
import argparse
import sys
from collections import defaultdict
import json
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


def get_previous_session(session_str):
    """
    Calculates the previous session ID.
    Example: 'ses-05' -> 'ses-04'
    Returns None if session is 'ses-01' or cannot be parsed.
    """
    try:
        # Assumes format 'ses-XX'
        prefix, num_str = session_str.split('-')
        current_val = int(num_str)

        if current_val <= 1:
            return None

        # Maintains padding (e.g., 04 instead of 4)
        prev_val = current_val - 1
        return f"{prefix}-{prev_val:02d}"
    except (ValueError, IndexError):
        return None


def mv_files(data, input_path, output_path):
    for subject, sessions in data.items():
        print(f"Processing {subject}")

        for session in sessions:
            if session is None:
                continue
            print(f"\tProcessing {session}")

            # sub-SUBJECT_SESS_rec-niftymic_desc-brainbg_T2w.nii
            vol_3d_filename = f"{subject}_{session}_rec-niftymic_desc-brainbg_T2w.nii.gz"
            input_3d_path = os.path.join(input_path, subject, session, "anat", vol_3d_filename)

            output_3d_path = os.path.join(output_path, f"{subject}_{session}_0000.nii.gz")

            if os.path.exists(input_3d_path):
                shutil.copy(input_3d_path, output_3d_path)
            else:
                print(f"Error: The file {input_3d_path} does not exist.")


def generate_patient_sessions_json(directory_path, output_filename="patientsTs.json"):
    # defaultdict handles the creation of lists for new keys automatically
    patient_data = defaultdict(list)

    if not os.path.exists(directory_path):
        print(f"Error: The directory '{directory_path}' does not exist.")
        return

    files = os.listdir(directory_path)
    files.sort()

    for filename in files:
        if filename.endswith(".nii.gz"):
            # Format: "Borgne_ses-01_0000.nii.gz"
            parts = filename.split('_')
            if len(parts) >= 2:
                patient_name = parts[0]
                session_id = parts[1] # This will capture "ses-01"

                session_entry = f"{patient_name}_{session_id}"
                print("\t", session_entry)
                if session_entry not in patient_data[patient_name]:
                    patient_data[patient_name].append(session_entry)

    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(dict(patient_data), f, indent=4)

    print(f"File '{output_filename}' has been created successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Denoise data for a specific subject and session.")
    parser.add_argument("--subject", required=True, help="Subject ID (e.g., sub-Aziza)")
    parser.add_argument("--session", required=True, help="Session ID (e.g., ses-01)")
    args = parser.parse_args()

    subject = args.subject
    target_session = args.session

    # Logic to include t-1
    sessions_to_process = []
    prev_session = get_previous_session(target_session)

    if prev_session:
        sessions_to_process.append(prev_session)

    sessions_to_process.append(target_session)

    subj_sess = {subject: sessions_to_process}

    input_path = os.path.join(cfg.DERIVATIVES_BIDS_PATH, "niftymic")
    output_path = os.path.join(cfg.DERIVATIVES_BIDS_PATH, "intermediate", "longiseg", "inference_data")
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    else:
        shutil.rmtree(output_path)
        os.makedirs(output_path)

    mv_files(subj_sess, input_path, output_path)

    test_pred_json = os.path.join(output_path, "patientsTs.json")
    generate_patient_sessions_json(directory_path=output_path, output_filename=test_pred_json)
