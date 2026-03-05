import os
import sys
import shutil
from pathlib import Path
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg





if __name__ == "__main__":

    VIEW_MATCH = {
        "AX": "01",
        "AX2": "02",
        "COR": "03",
        "COR2": "04",
        "SAG": "05",
        "SAG2": "06"
    }

    INPUT_PATH = os.path.join(cfg.BASE_NIOLON_PATH, "fetalBET_masks_V2")
    OUTPUT_PATH = os.path.join(cfg.DERIVATIVES_BIDS_PATH, "niftymic")

    # sub-<sub>_ses-<ses>_acq-haste_run-<01..06>_desc-brain_mask.nii.gz

    for folder in os.listdir(INPUT_PATH):
        folder_path = os.path.join(INPUT_PATH, folder)
        print(folder_path)
        exit()
