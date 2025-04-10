import os
import sys
import shutil
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


output_folder = os.path.join(cfg.BASE_PATH, "Mask_RCNN", "MRI_dataset", "train")

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

subjects = ["Aziza"]
sessions = ["01"]


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


if __name__ == "__main__":
    for i, subject in enumerate(subjects):
        for session in sessions:
            get_data_for_subj(subject, session)