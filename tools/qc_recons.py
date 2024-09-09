import os
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
from tools import qc
import configuration as cfg


if __name__ == "__main__":
    MODE = "niftymic"  # "niftymic" | "nesvor"
    dir_snapshots = "snapshots"

    mid_dir_snapshots = os.path.join(dir_snapshots, "recons")
    if not os.path.exists(mid_dir_snapshots):
        os.mkdir(mid_dir_snapshots)

    mid_dir_snapshots = os.path.join(mid_dir_snapshots, MODE)
    if not os.path.exists(mid_dir_snapshots):
        os.mkdir(mid_dir_snapshots)

    subject = "sub-Aziza_ses-04"

    path_recons = os.path.join(cfg.MESO_OUTPUT_PATH, subject, "haste", "reconstruction_niftymic")

    dir_out = os.path.join(mid_dir_snapshots, subject)
    if not os.path.exists(dir_out):
        os.mkdir(dir_out)

    anat_filename = subject + "_haste_3DHR.nii.gz"
    bm_filename = subject + "_haste_3DHR_mask.nii.gz"

    anat_path = os.path.join(path_recons, anat_filename)
    bm_path = os.path.join(path_recons, bm_filename)

    #file_figure_out = os.path.join(dir_out, subject + "_recons.png")
    file_figure_out = os.path.join(dir_out, "tmp.png")

    qc.qc_recontructed_3DHRvolume(
        path_anat_vol=anat_path,
        path_brainmask_vol=None,
        file_figure_out=file_figure_out
    )


