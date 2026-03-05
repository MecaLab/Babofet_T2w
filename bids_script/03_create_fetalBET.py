import os
import sys
import re
import shutil
from pathlib import Path
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


def extract_orientation(filename):
    mapping = {
        "axial": "AX",
        "coronal": "COR",
        "sagital": "SAG",
        "ax": "AX",
        "cor": "COR",
        "sag": "SAG"
    }

    pattern = r"_(?:label-)?(axial|coronal|sagital|AX|COR|SAG)(?:_run-0?(\d+)|(2))?_"

    match = re.search(pattern, filename, re.IGNORECASE)

    if match:
        base = match.group(1).lower()
        run_number = match.group(2) or match.group(3)

        normalized = mapping.get(base, base.upper())

        if run_number == "2" or run_number == "02":
            return f"{normalized}2"
        return normalized

    return None


if __name__ == "__main__":

    VIEW_MATCH = {
        "AX": "01",
        "AX2": "02",
        "COR": "03",
        "COR2": "04",
        "SAG": "05",
        "SAG2": "06"
    }

    INPUT_PATH = os.path.join(cfg.BASE_NIOLON_PATH, "fetalBET_folder", "fetalBET_masks_V2")
    OUTPUT_PATH = os.path.join(cfg.DERIVATIVES_BIDS_PATH, "niftymic")

    # sub-<sub>_ses-<ses>_acq-haste_run-<01..06>_desc-brain_mask.nii.gz

    filenames = [
        "sub-Formule_ses-08_T2_HASTE_AX2_10_denoised_mask.nii.gz",
        "sub-Bibi_ses-07_acq-haste_label-axial_run-02_T2w_denoised_mask.nii",
        "sub-Bibi_ses-07_acq-haste_label-coronal_run-01_T2w.nii",
        "sub-Formule_ses-08_T2_HASTE_SAG_8_denoised_mask.nii.gz",
        "sub-Borgne_ses-01_acq-haste_label-sagital_T2w_denoised_mask.nii.gz",
        "sub-Borgne_ses-01_acq-haste_label-sagital_run-02_T2w_denoised_mask.nii.gz",
    ]

    for name in filenames:
        print(f"{name} -> {extract_orientation(name)}")

    exit()

    for folder in os.listdir(INPUT_PATH):
        print(f"Processing {folder}")
        folder_path = os.path.join(INPUT_PATH, folder)
        for file in os.listdir(folder_path):
            if not file.startswith("sub-Borgne"):
                continue
            if "Fabienne" in file:
                print(f"\tSkipping")
                continue

            if "HASTE" in file or "haste" in file:
                orientation = extract_orientation(file)
                print(orientation)
                if orientation is None:
                    print(f"\tAn error has occured with {file}")

                input_file_path = os.path.join(folder_path, file)

                sub_subject, sub_session = folder.split("_")
                filename_output = f"{sub_subject}_{sub_session}_acq-haste_run-{VIEW_MATCH[orientation]}_desc-brain_mask.nii.gz"
                output_file_path = os.path.join(OUTPUT_PATH, sub_subject, sub_session, "anat")

                if not os.path.exists(output_file_path):
                    os.makedirs(output_file_path)
                output_file_path = os.path.join(output_file_path, filename_output)
                shutil.copy(input_file_path, output_file_path)
