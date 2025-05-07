import os
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg
import subprocess


subjects = ["Formule", ] # "Formule", "Fabienne"]
sessions = ["01", "02", "03", "04", "05", "07", "08", "09"] # "05", "08", "09"]

stacks_base_path = cfg.MESO_DATA_PATH  # cfg.MESO_OUTPUT_PATH  DATA_PATH is for raw data / OUTPUT_PATH is for denoised data
bm_base_path = cfg.MESO_OUTPUT_PATH
recons_base_path = cfg.DATA_PATH

archive_output_path = "archive/"
if not os.path.exists(archive_output_path):
    os.makedirs(archive_output_path)

for subject in subjects:
    subject_output_path = os.path.join(archive_output_path, subject)

    if not os.path.exists(subject_output_path):
        os.makedirs(subject_output_path)

    for session in sessions:
        if not os.path.exists(os.path.join(recons_base_path, subject, f"ses{session}")):
            continue

        subject_session_output_path = os.path.join(subject_output_path, f"ses{session}")

        if not os.path.exists(subject_session_output_path):
            os.makedirs(subject_session_output_path)

        print(f"Processing {subject}: session {session}")

        # Copy the stacks
        stack_output_path = os.path.join(subject_session_output_path, "stacks")
        if not os.path.exists(stack_output_path):
            os.makedirs(stack_output_path)

        stacks_path = os.path.join(stacks_base_path, f"sub-{subject}_ses-{session}", "scans")

        # Accesing raw data
        for folder in os.listdir(stacks_path):
            if "HASTE" in folder:
                full_path = os.path.join(stacks_path, folder, "resources", "NIFTI", "files")
                for file in os.listdir(full_path):
                    if file.endswith(".nii"):
                        file_full_path = os.path.join(full_path, file)
                        subprocess.run(["cp", file_full_path, stack_output_path])


        # Uncomment the following lines to access the denoised files
        """
        stacks_path = os.path.join(stacks_base_path, f"sub-{subject}_ses-{session}", "denoising")
        for file in os.listdir(stacks_path):
            if "HASTE" in file:
                file_path = os.path.join(stacks_path, file)
                subprocess.run(["cp", file_path, stack_output_path])
        """

        # Copy the BM
        bm_output_path = os.path.join(subject_session_output_path, "fetalbet_brainmask")
        if not os.path.exists(bm_output_path):
            os.makedirs(bm_output_path)

        bm_path = os.path.join(bm_base_path, f"sub-{subject}_ses-{session}", "fetalbet_masks_v2")
        for file in os.listdir(bm_path):
            file_path = os.path.join(bm_path, file)
            subprocess.run(["cp", file_path, bm_output_path])

        # Copy the reconstructions
        recons_output_path = os.path.join(subject_session_output_path, "reconstructions")
        if not os.path.exists(recons_output_path):
            os.makedirs(recons_output_path)

        """recons_file = [
            f"sub-{subject}_ses-{session}_haste_3DHR_manual_bm_pipeline.nii.gz",  # anat recons
            f"sub-{subject}_ses-{session}_haste_3DHR_manual_bm_pipeline_mask.nii.gz"  # mask recons
        ]
        recons_path = os.path.join(recons_base_path, subject, f"ses{session}", "manual_brainmask")

        for file_recons in recons_file:
            file_output_path = os.path.join(recons_path, file_recons)
            subprocess.run(["cp", file_output_path, recons_output_path])"""