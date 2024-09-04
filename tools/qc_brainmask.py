import os
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
from tools import qc
import configuration as cfg


if __name__ == "__main__":
    MODE = "nesvor"  # "niftymic" | "nesvor"
    dir_snapshots = "snapshots"

    full_dir_snapshots = os.path.join(dir_snapshots, MODE)

    base_path = cfg.MESO_OUTPUT_PATH

    subject_IDs = os.listdir(base_path)

    for subject in subject_IDs:
        
        dir_denoised = os.path.join(base_path, subject, "denoising")
        dir_list_denoised = os.listdir(dir_denoised)

        if MODE == "niftymic":
            dir_brainmask = os.path.join(base_path, subject, "brainmask_niftymic")
            print(f"Starting {subject}")
            dir_list_bm = os.listdir(dir_brainmask)

            dir_out = os.path.join(full_dir_snapshots, subject)

            if not os.path.exists(dir_out):
                os.mkdir(dir_out)

            for f in dir_list_denoised:
                if "HASTE" in f:
                    filename = f.split(".")
                    bm_nifti_filename = filename[0] + "_seg.nii.gz"

                    file_figure_out = os.path.join(dir_out, filename[0] + "_bounti_seg.png")

                    qc.qc_brainmask(
                        os.path.join(dir_denoised, f),
                        os.path.join(dir_brainmask, filename[0], bm_nifti_filename),
                        file_figure_out,
                        debug=False,
                    )
                    print(f"End {f} for {subject}")
        elif MODE == "nesvor":
            dir_brainmask = os.path.join(base_path, subject, "brainmask")
            print(f"Starting {subject}")
            dir_list_bm = os.listdir(dir_brainmask)

            dir_out = os.path.join(full_dir_snapshots, subject)

            if not os.path.exists(dir_out):
                os.mkdir(dir_out)

            for f in dir_list_denoised:
                if "HASTE" in f:
                    filename = f.split(".")
                    bm_nifti_filename = filename[0] + "_brainmask.nii"

                    file_figure_out = os.path.join(dir_out, filename[0] + "_bounti_seg.png")

                    qc.qc_brainmask(
                        os.path.join(dir_denoised, f),
                        os.path.join(dir_brainmask, bm_nifti_filename),
                        file_figure_out,
                        debug=True,
                    )
                    print(f"End {f} for {subject}")