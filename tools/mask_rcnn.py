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

    for anat_file, bm_file in zip(os.listdir(subject_anat_path), os.listdir(subject_bm_path)):
        print(anat_file, bm_file)


if __name__ == "__main__":
    for subject in subjects:
        for session in sessions:
            get_data_for_subj(subject, session)