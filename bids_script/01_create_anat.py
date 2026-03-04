import os
import sys
import shutil
from pathlib import Path
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


INPUT_PATH = os.path.join(cfg.BASE_NIOLON_PATH, "subjects")
OUTPUT_PATH = "/envau/work/meca/data/BaboFet_BIDS/sourcedata/raw"

AX_MATCH = {
    "AX": "01",
    "AX2": "02",
    "COR": "03",
    "COR2": "04",
    "SAG": "05",
    "SAG2": "06"
}

subjects_data = {
    "Borgne": ["ses01", "ses03", "ses04", "ses05", "ses06", "ses07", "ses08", "ses09", "ses10"],
    "Formule": ["ses01", "ses02", "ses03", "ses04", "ses05", "ses06", "ses07", "ses08", "ses09"],
    "Bibi": ["ses01", "ses02", "ses03", "ses04", "ses05", "ses06", "ses07", "ses09"],
    "Filoutte": ["ses01", "ses02", "ses03", "ses04", "ses05", "ses06", "ses07", "ses08", "ses09", "ses10"],
    "Forme": ["ses01", "ses02", "ses03", "ses05", "ses06", "ses07", "ses08", "ses09", "ses10"],
    "Aziza": ["ses01", "ses02", "ses03", "ses04", "ses05", "ses06", "ses07", "ses08", "ses09", "ses10"],
}

def format_session_str(sess):
    id_sess = sess[3:]
    return f"ses-{id_sess}"

def get_folder_scan_suffix(folder_name):
    return folder_name.split("_")[-1]


def remove_anat_directories(base_directory_path):
    """
    Finds and removes all 'anat' directories matching the pattern: subject/ses-XX/anat
    """
    base_dir = Path(base_directory_path)

    # Pattern to match the specific folder structure
    # Assumes base_dir contains the subject folders
    target_pattern = "*/ses-*/anat"

    for anat_dir in base_dir.glob(target_pattern):
        if anat_dir.is_dir():
            try:
                shutil.rmtree(anat_dir)
                print(f"Successfully deleted: {anat_dir}")
            except OSError as error:
                print(f"Error deleting {anat_dir}: {error}")

if __name__ == "__main__":
    remove_anat_directories(OUTPUT_PATH)
    exit()
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
                    for file in os.listdir(nii_path):
                        if file.endswith(".nii.gz") or file.endswith(".json"):

                            extension = file.split(".")[-1]
                            if extension == "gz":
                                extension = "nii.gz"

                            file_full_path = os.path.join(nii_path, file)

                            # sub-<sub>_ses-<ses>_acq-<haste|trufi>_run-<01..06>_T2w.nii.gz
                            try:
                                output_filename = f"sub-{subject}_{session_formated}_acq-haste_run-{AX_MATCH[suffix_scans]}_T2w.{extension}"
                                print(f"\t\t{folder} | {file} -> {output_filename}")
                                shutil.copy(file_full_path, os.path.join(anat_dir, output_filename))
                            except KeyError:
                                print(f"\t\tKeyError with {suffix_scans}")
