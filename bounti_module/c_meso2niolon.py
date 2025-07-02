import os
import sys
import subprocess
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg

if __name__ == "__main__":

    subject = sys.argv[1]  # subject name, e.g., Fabienne / Formule / etc..
    user_id = "lbaptiste"

    base_path = os.path.join(cfg.DATA_PATH, subject)

    command = f"scp -P 8822 -r {user_id}@login.mesocentre.univ-amu.fr:{base_path} {cfg.RECONS_FOLDER}"

    subprocess.run(command, shell=True)