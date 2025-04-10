import os
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg

output_folder = os.path.join(cfg.BASE_PATH, "Mask_RCNN", "MRI_dataset")

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

subjects = ["Aziza"]
sessions = ["01"]


def get_data_for_subj(subject, session):
    full_subject_name = f"sub-{subject}_ses-{session}"
    subject_path = os.path.join(cfg.MESO_OUTPUT_PATH, full_subject_name)

    subject_anat_path = os.path.join(subject_path, "denoising")
    subject_bm_path = os.path.join(subject_path, "manual_masks")

    for anat_file in os.listdir(subject_anat_path):
        if "HASTE" in anat_file:
            anat_file_path = os.path.join(subject_anat_path, anat_file)
            bm_file_path = os.path.join(subject_bm_path, anat_file.replace(".nii", "_mask.nii.gz"))
            print(os.path.exists(anat_file_path), os.path.exists(bm_file_path), bm_file_path)


if __name__ == "__main__":
    for subject in subjects:
        for session in sessions:
            get_data_for_subj(subject, session)