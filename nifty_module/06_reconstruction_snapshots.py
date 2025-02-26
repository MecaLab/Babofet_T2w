import os
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg
from tools import qc_recons

if __name__ == "__main__":

    subject = "Fabienne"
    base_path = os.path.join(cfg.DATA_PATH, subject)
    modes = ["manual", "nifty"]

    datas = {}
    # plot the matplotlib table format for the qc:
    # 1 row per slice in the anat img, 1 col per method (manual, nifty, etc)
    # 1 file per session
    name = "thresholds-1"
    for session in os.listdir(base_path):
        datas[session] = {}
        for mode in modes:
            datas[session][mode] = {}
            datas[session][mode]["anat"] = os.path.join(base_path, session, f"{mode}_brainmask/exp_param", f"sub-{subject}_ses-{session[3:]}_haste_3DHR_{mode}_bm_T-1_pipeline.nii.gz")

    qc_recons.qc_plot_table_recons(datas, name)


    """# 1 snapshot per reconstruction
    modes = ["manual"]
    base_path = os.path.join(cfg.DATA_PATH, subject)

    for mode in modes:
        qc_recons.qc_recons_bis(base_path, subject, mode)"""

    """
    base_path = cfg.MESO_OUTPUT_PATH
    model = "niftymic"  # niftymic or nesvor
    mode = "manual"  # manual bm or nifty bm
    debug = False

    qc_recons.qc_recons(
        base_path,
        model,
        mode,
    )
    """