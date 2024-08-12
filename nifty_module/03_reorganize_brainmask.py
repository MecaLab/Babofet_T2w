import os
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg
import shutil


if __name__ == "__main__":
    base_path = cfg.MESO_OUTPUT_PATH


    subject_IDs = os.listdir(base_path)
    subject_processed_haste = list()
    subject_processed_truefisp = list()

    for subject in subject_IDs:
        print("Starting {}".format(subject))

        dir_list = os.path.join(base_path, subject, "brainmask_niftymic")

        for d in os.listdir(dir_list):
            if os.path.isdir(os.path.join(dir_list, d)):
                input_full_path = os.path.join(dir_list, d, d + "_seg.nii.gz")
                output_full = os.path.join(dir_list, d + "_seg.nii.gz")
                try:
                    shutil.copy(input_full_path, output_full)
                except FileNotFoundError:
                    if os.path.exists(output_full):
                        print(f"\tOK for {d}")
                    else:
                        print(f"\tError from {d}")
                        exit()

        exit()