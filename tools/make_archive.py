import os
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


subjects = ["Fabienne", "Aziza", "Formule"]
sessions = ["01", "05", "08", "09"]

stacks_base_path = cfg.MESO_OUTPUT_PATH
recons_base_path = cfg.DATA_PATH

archive_output_path = "archive/"
if not os.path.exists(archive_output_path):
    os.makedirs(archive_output_path)

for subject in subjects:
    for session in sessions:
        subj_session = f"sub-{subject}_ses-{session}"
        print(subj_session)
        # get all stacks
        stacks_path = os.path.join(stacks_base_path, subj_session, "denoising")
        print(os.listdir(stacks_path))
        exit()