import os
import sys
import subprocess
import shutil
from pathlib import Path
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


def format_session_str(sess):
    id_sess = sess[3:]
    return f"ses-{id_sess}"

def get_denoised_from_meso(subject_sess, output_path):
    main_path = "/scratch/lbaptiste/data/dataset/babofet/derivatives/"

    input_path = os.path.join(main_path, subject_sess, "denoising")

    full_output_path = os.path.join(output_path, subject_sess)  # subject_sess is format sub-SUBJECT_ses-XX
    if not os.path.exists(full_output_path):
        os.makedirs(full_output_path)

    try:
        command = f"rsync -avz -e 'ssh -p 8822' lbaptiste@login.mesocentre.univ-amu.fr:{input_path} {full_output_path}"
        subprocess.run(command, shell=True)
    except:
        print(f"Something went wrong with {subject_sess}")

if __name__ == "__main__":
    subjects_data = {
        "Borgne": ["ses01", "ses03", "ses04", "ses05", "ses06", "ses07", "ses08", "ses09", "ses10"],
        "Formule": ["ses01", "ses02", "ses03", "ses04", "ses05", "ses06", "ses07", "ses08", "ses09"],
        "Bibi": ["ses01", "ses02", "ses03", "ses04", "ses05", "ses06", "ses07", "ses09"],
        "Filoutte": ["ses01", "ses02", "ses03", "ses04", "ses05", "ses06", "ses07", "ses08", "ses09", "ses10"],
        "Forme": ["ses01", "ses02", "ses03", "ses05", "ses06", "ses07", "ses08", "ses09", "ses10"],
        "Aziza": ["ses01", "ses02", "ses03", "ses04", "ses05", "ses06", "ses07", "ses08", "ses09", "ses10"],
    }
    OUTPUT_PATH = "/envau/work/meca/data/babofet_DB/2024_new_stuff/denoising_folder/"

    for subject, sessions in subjects_data.items():
        print(f"Processing {subject}")
        for session in sessions:
            print(f"\tProcessing {session}")
            subject_sess = f"sub-{subject}_{format_session_str(session)}"
            get_denoised_from_meso(subject_sess, OUTPUT_PATH)
            print(f"\tDone\n")