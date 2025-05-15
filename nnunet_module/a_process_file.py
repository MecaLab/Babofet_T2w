import os
import shutil
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg

subject = "Aziza"

input_path = os.path.join(cfg.SEG_INPUT_PATH, subject)
output_path = os.path.join(cfg.NNUNET_RAW_PATH, "imagesTr")

for session in os.listdir(input_path):
    recons_file = os.path.join(input_path, session, "reo-SVR-output-brain_rhesus.nii.gz")

    if not os.path.exists(recons_file):
        print(f"File {recons_file} does not exist.")
        continue

    print(f"Processing {recons_file}...")

    output_filename = f"{subject.lower()}_0{session[3:]}_0000.nii.gz"
    output_full_path = os.path.join(output_path, output_filename)

    shutil.copy2(recons_file, output_full_path)
    exit()





