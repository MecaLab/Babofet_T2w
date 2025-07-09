import os
import sys
import subprocess
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg

if __name__ == "__main__":

    subject = sys.argv[1]  # subject name, e.g., Fabienne / Formule / etc..
    user_id = "lbaptiste"

    # Path for BOUNTI
    base_vol_path = os.path.join(cfg.SEG_INPUT_PATH_NIOLON, subject)
    base_seg_path = os.path.join(cfg.SEG_OUTPUT_PATH_NIOLON, subject)

    output_vol_path = os.path.join(cfg.SEG_INPUT_PATH, subject)
    output_seg_path = os.path.join(cfg.SEG_OUTPUT_PATH, subject)

    """command = f"scp -P 8822 -r {base_vol_path}/* {user_id}@login.mesocentre.univ-amu.fr:{output_vol_path}"
    subprocess.run(command, shell=True)

    command = f"scp -P 8822 -r {base_seg_path}/* {user_id}@login.mesocentre.univ-amu.fr:{output_seg_path}"
    subprocess.run(command, shell=True)"""

    # Path for recons folder
    base_vol_path = os.path.join(cfg.RECONS_FOLDER, subject)

    output_vol_path = os.path.join(cfg.DATA_PATH, subject)
    command = f"rsync -avz -e 'ssh -p 8822' {base_vol_path} {user_id}@login.mesocentre.univ-amu.fr:{output_vol_path}"
    subprocess.run(command, shell=True)

    print("Data copied successfully to the mesocentre.")