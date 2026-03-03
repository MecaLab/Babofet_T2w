import os
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


INPUT_PATH = os.path.join(cfg.BASE_NIOLON_PATH, "subjects")
OUTPUT_PATH = "/envau/work/meca/data/babofet_BIDS/sourcedata/raw"

AX_MATCH = {
    "AX": "01",
    "AX2": "02",
    "COR": "03",
    "COR2": "04",
    "SAG": "05",
    "SAG2": "06"
}

subjects_data = {
    "Borgne": ["ses01", "ses03", "ses04", "ses05", "ses06", "ses07", "ses08", "ses09", "ses10"]
}

def format_session_str(sess):
    id_sess = sess[3:]
    return f"ses-{id_sess}"

def get_folder_scan_suffix(folder_name):
    return folder_name.split("_")[-1]

if __name__ == "__main__":

    for subject, sessions in subjects_data.items():
        print(f"Processing {subject}")
        output_subj_dir = os.path.join(OUTPUT_PATH, f"sub-{subject}")

        if not os.path.exists(output_subj_dir):
            os.makedirs(output_subj_dir)

        for session in sessions:
            print(f"\tProcessing {session}")
            session_formated = format_session_str(session)
            sub_session_dir = os.path.join(output_subj_dir, session_formated)

            if not os.path.exists(sub_session_dir):
                os.makedirs(sub_session_dir)

            anat_dir = os.path.join(sub_session_dir, "anat")
            if not os.path.exists(anat_dir):
                os.makedirs(anat_dir)

            input_subj_dir = os.path.join(INPUT_PATH, f"sub-{subject}_{session_formated}", "scans")

            for folder in os.listdir(input_subj_dir):
                if "HASTE" in folder:
                    suffix_scans = get_folder_scan_suffix(folder)
                    nii_path = os.path.join(input_subj_dir, folder, "resources", "NIFTI", "files")
                    nii_file = os.listdir(nii_path)[0]
                    nii_full_path = os.path.join(nii_path, nii_file)

                    # sub-<sub>_ses-<ses>_acq-<haste|trufi>_run-<01..06>_T2w.nii.gz

                    output_nii_filename = f"sub-{subject}_{session_formated}_haste_run-{AX_MATCH[suffix_scans]}_T2w.nii.gz"
                    print(f"\t\t{folder} -> {output_nii_filename}")

            exit()
