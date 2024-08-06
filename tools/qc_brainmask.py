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
        print("Starting {}".format(subject))

        dir_list = os.listdir(os.path.join(base_path, subject, "denoising"))

        dir_out = os.path.join(dir_snapshots, subject)

        if not os.path.exists(dir_out):
            os.mkdir(dir_out)

        for f in dir_list:

            filename = f.split(".")

            file_figure_out = os.path.join(dir_out, filename[0] + "_bounti_seg.png")

            print(file_figure_out)

        exit()

        # qc.qc_brainmask(path_anat_vol, path_brainmask_vol, file_figure_out)