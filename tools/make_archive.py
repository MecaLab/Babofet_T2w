import os
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg
import subprocess


subjects = ["Fabienne", "Aziza", "Formule"]
sessions = ["01", "05", "08", "09"]

stacks_base_path = cfg.MESO_OUTPUT_PATH
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

        subject_session_output_path = os.path.join(subject_output_path, f"ses-{session}")

        if not os.path.exists(subject_session_output_path):
            os.makedirs(subject_session_output_path)

        print(subject, session)
        # Copy the stacks
        stacks_path = os.path.join(stacks_base_path, f"sub-{subject}_ses-{session}", "denoising")
        for file in os.listdir(stacks_path):
            if "HASTE" in file:
                file_path = os.path.join(stacks_path, file)
                subprocess.run(["cp", file_path, subject_session_output_path])
        exit()