import os
import sys
import subprocess
import shutil
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


def format_session_str(sess):
    id_sess = sess[3:]
    return f"ses-{id_sess}"

def get_denoised_from_meso(subject_data, output_path):
    main_path = "/scratch/lbaptiste/data/dataset/babofet/derivatives/"
    login = "lbaptiste"  # mesocentre id

    for subject, sessions in subject_data.items():
        print(f"Processing {subject}")
        for session in sessions:
            print(f"\tProcessing {session}")

            subject_sess = f"sub-{subject}_{format_session_str(session)}"
            input_path = os.path.join(main_path, subject_sess, "denoising")

            full_output_path = os.path.join(output_path, subject_sess)  # subject_sess is format sub-SUBJECT_ses-XX
            if not os.path.exists(full_output_path):
                os.makedirs(full_output_path)

            try:
                command = f"rsync -avz -e 'ssh -p 8822' {login}@login.mesocentre.univ-amu.fr:{input_path} {full_output_path}"
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

    INPUT_PATH = "/envau/work/meca/data/babofet_DB/2024_new_stuff/denoising_folder/"
    if not os.path.exists(INPUT_PATH):
        get_denoised_from_meso(subjects_data, output_path=INPUT_PATH)

    OUTPUT_PATH = "/envau/work/meca/data/BaboFet_BIDS/derivatives/intermediate/niftymic"
    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)

    for folder in os.listdir(INPUT_PATH):
        print(f"Processing {folder}")
        subject_input_path = os.path.join(INPUT_PATH, folder, "denoising")

        sub_subject, sub_sess = folder.split("_")  # sub-XXXX_ses-YY
        subject_name = sub_subject.split("-")[-1]
        session_name = sub_sess.split("-")[-1]

        subject_output_path = os.path.join(OUTPUT_PATH, f"sub-{subject_name}", f"ses-{session_name}")
        if not os.path.exists(subject_output_path):
            os.makedirs(subject_output_path)

        for file in os.listdir(subject_input_path):
            input_file = os.path.join(subject_input_path, file)
            output_file = os.path.join(subject_output_path, file)
            shutil.copy(input_file, output_file)






