import os
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
from tools import qc
import configuration as cfg


if __name__ == "__main__":
    dir_snapshots = "snapshots"

    base_path = cfg.MESO_OUTPUT_PATH

    subject_IDs = os.listdir(base_path)

    for subject in subject_IDs:
        
        dir_denoised = os.path.join(base_path, subject, "denoising")
        dir_brainmask = os.path.join(base_path, subject, "brainmask_niftymic")
        print("Starting {}".format(subject))

        dir_list_denoised = os.listdir(dir_denoised)
        dir_list_bm = os.listdir(dir_brainmask)

        dir_out = os.path.join(dir_snapshots, subject)

        if not os.path.exists(dir_out):
            os.mkdir(dir_out)

        for f in dir_list_denoised:
            filename = f.split(".")
            bm_nifti_filename = filename[0] + "_seg.nii.gz"

            file_figure_out = os.path.join(dir_out, filename[0] + "_bounti_seg.png")

            qc.qc_brainmask(
                os.path.join(dir_denoised, f),
                os.path.join(dir_brainmask, filename[0], bm_nifti_filename),
                file_figure_out
            )
            print(f"End {f} for {subject}")

