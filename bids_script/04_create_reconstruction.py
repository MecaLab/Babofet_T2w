import os
import sys
import shutil
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


if __name__ == "__main__":
    INPUT_PATH = os.path.join(cfg.BASE_NIOLON_PATH, "recons_folder")
    OUTPUT_PATH = os.path.join(cfg.DERIVATIVES_BIDS_PATH, "niftymic")

    for subject in os.listdir(INPUT_PATH):
        print(subject)
