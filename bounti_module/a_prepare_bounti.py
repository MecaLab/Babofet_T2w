import os
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg

if __name__ == "__main__":

    subject = "Formule"

    input_dir = os.path.join(cfg.MESO_OUTPUT_PATH)

    for subject_sess in os.listdir(input_dir):
        if subject not in subject_sess:
            continue

        print(subject_sess)
