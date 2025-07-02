import os
import sys
import subprocess
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg

if __name__ == "__main__":

    subject = sys.argv[1]  # subject name, e.g., Fabienne / Formule / etc..
    user_id = "lbaptiste"

    base_vol_path = os.path.join(cfg.SEG_INPUT_PATH_NIOLON, subject)
    base_seg_path = os.path.join(cfg.SEG_OUTPUT_PATH_NIOLON, subject)

    output_vol_path = os.path.join(cfg.SEG_INPUT_PATH, subject)
    output_seg_path = os.path.join(cfg.SEG_OUTPUT_PATH, subject)

    command = f"scp -P 8822 -r {base_vol_path} {user_id}@login.mesocentre.univ-amu.fr:{output_vol_path}"

    print(command)

    subprocess.run(command, shell=True)
    print("Volume data copied successfully.")