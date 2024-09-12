import os
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg
from tools import qc_recons

if __name__ == "__main__":

    base_path = cfg.MESO_OUTPUT_PATH
    mode = "niftymic"
    debug = False

    qc_recons.qc_recons(
        base_path,
        mode,
    )