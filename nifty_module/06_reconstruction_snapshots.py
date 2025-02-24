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

    for session in os.listdir(base_path):
        datas[session] = {}
        for mode in modes:
            datas[session][mode] = {}
            datas[session][mode]["anat"] = os.path.join(base_path, session, f"{mode}_brainmask", f"sub-{subject}_ses-{session[3:]}_haste_3DHR_{mode}_bm_pipeline.nii.gz")
            datas[session][mode]["bm"] = os.path.join(base_path, session, f"{mode}_brainmask", f"sub-{subject}_ses-{session[3:]}_haste_3DHR_{mode}_bm_pipeline_mask.nii.gz")
        break

    qc_recons.qc_plot_table(datas)

    """subject = "Fabienne"
    modes = ["manual", "nifty"]
    base_path = os.path.join(cfg.DATA_PATH, subject)

    for mode in modes:
        qc_recons.qc_recons_bis(base_path, subject, mode)"""

    """base_path = cfg.MESO_OUTPUT_PATH
    model = "niftymic"  # niftymic or nesvor
    mode = "manual"  # manual bm or nifty bm
    debug = False

    qc_recons.qc_recons(
        base_path,
        model,
        mode,
    )"""