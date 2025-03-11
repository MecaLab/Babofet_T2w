import os
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg
from tools import qc_recons
import numpy as np
import nibabel as nib
import matplotlib.pyplot as plt


def plot_histo(data, label, slice_index, ax=None):
    ax.hist(data[:, :, slice_index].flatten(), bins=50, alpha=0.6, label=label)
    ax.set_xlabel("Intensité")
    ax.set_ylabel("Fréquence")
    ax.legend()


def plot_intensity_profile(data, slice_index, axis=0, label='', ax=None):
    if axis == 0:
        profile = data[slice_index, :, :].mean(axis=1)
    elif axis == 1:
        profile = data[:, slice_index, :].mean(axis=1)
    elif axis == 2:
        profile = data[:, :, slice_index].mean(axis=1)

    ax.plot(profile, label=label)
    ax.set_xlabel('Position')
    ax.set_ylabel('Intensité')
    ax.legend()


if __name__ == "__main__":

    subject = "Aziza"
    base_path = os.path.join(cfg.DATA_PATH, subject)
    modes = ["manual"]
    datas = {}

    exp_list = [False]
    params = [None]
    names = ["default-param"]

    for i in range(len(exp_list)):
        exp_param_folder = exp_list[i]
        param = params[i]
        name = names[i]
        for session in os.listdir(base_path):
            datas[session] = {}
            for mode in modes:
                print(f"Session {session} - Mode {mode}")
                subj_path = os.path.join(base_path, session)  # ../data/recons_folder/subj/session
                subj_session = f"sub-{subject}_ses-{session[3:]}"

                # Plot the anat image with the BM using the rejected slices file
                # qc_recons.qc_rejected_slices(subj_path, subject, subj_session, mode, exp_param_folder=exp_param_folder, param=param, name=name)

                # Plot 1 snapshot per reconstruction
                # qc_recons.qc_recons_bis(base_path, subject, mode, exp_param_folder=exp_param_folder, param=param, name=name)

                qc_recons.qc_intensity(subj_path, mode, subj_session, param="T")
                exit()

                datas[session][mode] = {}
                if not exp_param_folder:
                    datas[session][mode]["anat"] = os.path.join(base_path, session, f"{mode}_brainmask", f"sub-{subject}_ses-{session[3:]}_haste_3DHR_{mode}_bm_pipeline.nii.gz")
                else:
                    datas[session][mode]["anat"] = os.path.join(base_path, session, f"exp_param/{mode}_brainmask", f"sub-{subject}_ses-{session[3:]}_haste_3DHR_{mode}_bm_{param}_pipeline.nii.gz")

        # plot the matplotlib table format for the qc:
        # 1 row per slice in the anat img, 1 col per method (manual, nifty, etc) / 1 file per session
        # qc_recons.qc_plot_table_recons(datas, subject, name)
        # Lines above are commented because it is not working properly. Need to fix the orientation of the images (dim prb ?)



