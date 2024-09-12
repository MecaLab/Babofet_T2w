import os
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
from tools import qc
import configuration as cfg


def qc_brainmask(base_path, mode, debug=False):
    """
    Function that use the anatomic and the brainmask data to snapshot them
    The mode string is used to split between niftymic and nesvor

    :param base_path: str, path to the list of the subjects
    :param mode: str, nesvor or niftymic
    :return: None
    """
    dir_snapshots = "snapshots"  # Main directory that will contain the snapshots

    full_dir_snapshots = os.path.join(dir_snapshots, mode)

    subject_IDs = os.listdir(base_path)

    for subject in subject_IDs:
        dir_denoised = os.path.join(base_path, subject, "denoising")
        dir_list_denoised = os.listdir(dir_denoised)

        if mode == "niftymic":
            dir_brainmask = os.path.join(base_path, subject, "brainmask_niftymic")
            print(f"Starting {subject}")

            dir_out = os.path.join(full_dir_snapshots, subject)  # each subject has his own folder

            if not os.path.exists(dir_out):
                os.mkdir(dir_out)

            for f in dir_list_denoised:
                if "HASTE" in f:
                    filename = f.split(".")
                    bm_nifti_filename = filename[0] + "_seg.nii.gz"

                    file_figure_out = os.path.join(dir_out, filename[0] + ".png")

                    qc.qc_brainmask(
                        os.path.join(dir_denoised, f),
                        os.path.join(dir_brainmask, filename[0], bm_nifti_filename),
                        file_figure_out,
                        mode=mode,
                        debug=debug,
                    )
                    print(f"End {f} for {subject}")

        elif mode == "nesvor":
            dir_brainmask = os.path.join(base_path, subject, "brainmask")
            print(f"Starting {subject}")

            dir_out = os.path.join(full_dir_snapshots, subject)

            if not os.path.exists(dir_out):
                os.mkdir(dir_out)

            for f in dir_list_denoised:
                if "HASTE" in f:
                    filename = f.split(".")
                    bm_nifti_filename = filename[0] + "_brainmask.nii"

                    file_figure_out = os.path.join(dir_out, filename[0] + ".png")

                    if os.path.exists(file_figure_out):
                        print(f"\tSkipped {f} for {subject}")
                    else:
                        qc.qc_brainmask(
                            os.path.join(dir_denoised, f),
                            os.path.join(dir_brainmask, bm_nifti_filename),
                            file_figure_out,
                            mode=mode,
                            debug=debug,
                        )
                        print(f"End {f} for {subject}")