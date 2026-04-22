import os
import shutil
import argparse
import sys
from collections import defaultdict
import json
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg

def generate_patients_json():
    pass


def mv_files(data, input_path, output_path):
    for subject, sessions in data.items():
        print(f"Processing {subject}")

        for session in sessions:
            print(f"\tProcessing {session}")

            # sub-SUBJECT_SESS_rec-niftymic_desc-brainbg_T2w.nii
            vol_3d_filename = f"sub-{subject}_{session}_rec-niftymic_desc-brainbg_T2w.nii.gz"
            input_3d_path = os.path.join(input_path, subject, session, "anat", vol_3d_filename)

            output_3d_path = os.path.join(output_path, f"{subject}_{session}_0000.nii.gz")

            if os.path.exists(input_3d_path):
                shutil.copy(input_3d_path, output_3d_path)


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
    session = args.session
    subj_sess = {subject: [session]}

    input_path = os.path.join(cfg.DERIVATIVES_BIDS_PATH, "niftymic")
    output_path = os.path.join(cfg.DERIVATIVES_BIDS_PATH, "intermediate", "longiseg", "inference_data")
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    else:
        shutil.rmtree(output_path)
        os.makedirs(output_path)

    print("here")
    mv_files(subj_sess, input_path, output_path)

    test_pred_json = os.path.join(output_path, "patientsTs.json")
    generate_patient_sessions_json(directory_path=output_path, output_filename=test_pred_json)
