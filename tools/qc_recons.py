import os
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
from tools import qc
import configuration as cfg


if __name__ == "__main__":
    MODE = "niftymic"  # "niftymic" | "nesvor"
    dir_snapshots = "snapshots"

    subject = "sub-Aziza_ses-04"

    path_recons = os.path.join(cfg.MESO_OUTPUT_PATH, subject, "haste", "reconstruction_niftymic")

    for file in os.listdir(path_recons):
        print(file)


