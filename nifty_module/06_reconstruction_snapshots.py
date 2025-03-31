import os
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg
from tools import qc_recons
import numpy as np
import nibabel as nib
import matplotlib.pyplot as plt
from scipy import stats


if __name__ == "__main__":
    subject = sys.argv[1]
    base_path = os.path.join(cfg.DATA_PATH, subject)
    modes = ["mattia"]
    datas = {}

    exp_list = [False, True] #    True, True, True, True]
    params = [None, "T-1"] # "B1", "B1_T-1", "B1_T13", "B1_T46"]
    names = ["default-param", "threshold_-1"] #  "bias-field-correction", "bias-field-correction_threshold_-1", "bias-field-correction_threshold_0.1_0.3", "bias-field-correction_threshold_0.4_0.6"]

    for i in range(len(exp_list)):
        exp_param_folder = exp_list[i]
        param = params[i]
        name = names[i]
        for session in os.listdir(base_path):
            if session != "ses01":
                continue
            datas[session] = {}
            subj_path = os.path.join(base_path, session)  # ../data/recons_folder/subj/session
            subj_session = f"sub-{subject}_ses-{session[3:]}"
            for mode in modes:
                print(f"Running {mode} for {session} with {param} param")
                # Plot the anat image with the BM using the rejected slices file
                qc_recons.qc_rejected_slices(subj_path, subject, subj_session, mode, exp_param_folder=exp_param_folder, param=param, name=name)

                # Plot 1 snapshot per reconstruction
                qc_recons.qc_recons_bis(subj_path, subject, mode, exp_param_folder=exp_param_folder, param=param, name=name)

                qc_recons.qc_intensity(subj_path, subject, mode, subj_session)

                datas[session][mode] = {}
                if not exp_param_folder:
                    datas[session][mode]["anat"] = os.path.join(base_path, session, f"{mode}_brainmask", f"sub-{subject}_ses-{session[3:]}_haste_3DHR_{mode}_bm_pipeline.nii.gz")
                else:
                    datas[session][mode]["anat"] = os.path.join(base_path, session, f"exp_param/{mode}_brainmask", f"sub-{subject}_ses-{session[3:]}_haste_3DHR_{mode}_bm_{param}_pipeline.nii.gz")

            qc_recons.qc_plot_table_params(subj_path, mode, subject, subj_session)
            qc_recons.plot_histo(subj_path, mode, subject, subj_session)
        # plot the matplotlib table format for the qc:
        # 1 row per slice in the anat img, 1 col per method (manual, nifty, etc) / 1 file per session
        # qc_recons.qc_plot_table_recons(datas, subject, name)
        # Lines above are commented because it is not working properly. Need to fix the orientation of the images (dim prb ?)"""



