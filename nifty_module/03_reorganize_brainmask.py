import os
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


if __name__ == "__main__":
    base_path = cfg.MESO_OUTPUT_PATH


    subject_IDs = os.listdir(base_path)
    subject_processed_haste = list()
    subject_processed_truefisp = list()

    for subject in subject_IDs:
        print("Starting {}".format(subject))

        dir_list = os.listdir(os.path.join(base_path, subject, "brainmask_niftymic"))

        for d in dir_list:
            print(d)

        exit()