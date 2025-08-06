import os
import sys
import shutil
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg

if __name__ == "__main__":

    subject = sys.argv[1]

    input_dir = cfg.MESO_OUTPUT_PATH
    output_dir = os.path.join(cfg.DATA_PATH, subject)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for subject_sess in os.listdir(input_dir):
        if subject not in subject_sess:
            continue

        full_subject_input_dir = os.path.join(input_dir, subject_sess, "haste", "reconstruction_niftymic_full_pipeline_rhesus_macaque")
        if not os.path.exists(full_subject_input_dir):
            continue
        print(f"Processing {subject_sess}...")
        session = "".join(subject_sess.split("_")[-1].split("-"))  # sub-SUBJECT_ses-XX  => sesXX

        session_output_dir = os.path.join(output_dir, session)
        if not os.path.exists(session_output_dir):
            os.makedirs(session_output_dir)

        output_path = os.path.join(session_output_dir, "recons_rhesus")
        if not os.path.exists(output_path):
            os.makedirs(output_path)
            shutil.copytree(full_subject_input_dir, output_path, dirs_exist_ok=True)
        else:
            print(f"\tOutput directory {output_path} already exists. Skipping copy.")



