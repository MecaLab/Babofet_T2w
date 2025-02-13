import os
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg
from tools import qc_recons

if __name__ == "__main__":

    subject = "Fabienne"
    base_path = os.path.join(cfg.DATA_PATH, subject)
    qc_recons.qc_recons_bis(base_path)

    """base_path = cfg.MESO_OUTPUT_PATH
    model = "niftymic"  # niftymic or nesvor
    mode = "manual"  # manual bm or nifty bm
    debug = False

    qc_recons.qc_recons(
        base_path,
        model,
        mode,
    )"""