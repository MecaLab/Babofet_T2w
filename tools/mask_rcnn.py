import os
import sys
import shutil
import numpy as np
import nibabel as nib
import re
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


output_folder = os.path.join(cfg.BASE_PATH, "Mask_RCNN", "MRI_dataset", "train")

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

subjects = ["Aziza", "Formule", "Fabienne"]
sessions = ["01", "05", "09"]


def get_data_for_subj(subject, session):
    full_subject_name = f"sub-{subject}_ses-{session}"
    subject_path = os.path.join(cfg.MESO_OUTPUT_PATH, full_subject_name)

    subject_anat_path = os.path.join(subject_path, "denoising")
    subject_bm_path = os.path.join(subject_path, "manual_masks")

    subj_name = f"{subject}_{session}"
    cpt_orientation = {}
    for anat_file in os.listdir(subject_anat_path):
        if "HASTE" in anat_file:
            anat_file_path = os.path.join(subject_anat_path, anat_file)
            bm_file_path = os.path.join(subject_bm_path, anat_file.replace(".nii", "_mask.nii.gz"))

            if not os.path.exists(bm_file_path):
                print(f"Brain mask not found for {os.path.basename(anat_file_path)}")
                continue

            orientation = anat_file.split("HASTE")[-1].split("_")[1]
            if 'AX' in orientation:
                orientation = "axial"
            elif "SAG" in orientation:
                orientation = "sagittal"
            elif "COR" in orientation:
                orientation = "coronal"

            if orientation not in cpt_orientation:
                cpt_orientation[orientation] = 1
            else:
                cpt_orientation[orientation] += 1

            new_filename_anat = f"{subj_name}_{orientation}_{cpt_orientation[orientation]}.nii"
            new_filename_bm = f"{subj_name}_{orientation}_{cpt_orientation[orientation]}_mask.nii.gz"

            shutil.copy2(anat_file_path, os.path.join(output_folder, new_filename_anat))
            shutil.copy2(bm_file_path, os.path.join(output_folder, new_filename_bm))

            print(f"OK for {os.path.basename(anat_file_path)} and {os.path.basename(bm_file_path)}")


output_img_dir = os.path.join(cfg.BASE_PATH, "Mask_RCNN", "MRI_dataset_png", "images")
output_mask_dir = os.path.join(cfg.BASE_PATH, "Mask_RCNN", "MRI_dataset_png", "masks")

os.makedirs(output_img_dir, exist_ok=True)
os.makedirs(output_mask_dir, exist_ok=True)


def normalize_slice(slice_data):
    """ Normalise une slice entre 0 et 255 pour le PNG """
    slice_data = np.nan_to_num(slice_data)
    slice_min = np.min(slice_data)
    slice_max = np.max(slice_data)
    if slice_max - slice_min == 0:
        return np.zeros_like(slice_data, dtype=np.uint8)
    normalized = (slice_data - slice_min) / (slice_max - slice_min)
    return (normalized * 255).astype(np.uint8)


def stack2png(input_dir):
    nii_files = sorted([f for f in os.listdir(input_dir) if f.endswith(".nii") and not f.endswith("_mask.nii.gz")])
    for nii in nii_files:
        match = re.match(r"(.*)_(axial|coronal|sagittal)_(\d+)\.nii", nii)
        sujet_id, orientation, slice_index = match.groups()

        mask_file = f"{sujet_id}_{orientation}_{slice_index}_mask.nii.gz"

        nii_path = os.path.join(input_dir, nii)
        mask_path = os.path.join(input_dir, mask_file)

        img_vol = nib.load(nii_path).get_fdata()
        mask_vol = nib.load(mask_path).get_fdata()

        print(nii)
        print(img_vol.shape)
        print(mask_vol.shape)
        break



if __name__ == "__main__":
    """for i, subject in enumerate(subjects):
        for session in sessions:
            get_data_for_subj(subject, session)"""
    stack2png(input_dir=output_folder)