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


if __name__ == "__main__":

    subject = "Fabienne"
    base_path = os.path.join(cfg.DATA_PATH, subject)
    """modes = ["manual"]
    datas = {}

    exp_list = [False, True, True, True]
    params = [None, "T-1", "T13", "T46"]
    names = ["default-param", "threshold_-1", "threshold_0.1_0.3", "threshold_0.4_0.6"]"""

    vol1 = nib.load(os.path.join(base_path, "ses01", "manual_brainmask", "sub-Fabienne_ses-01_haste_3DHR_manual_bm_pipeline.nii.gz")).get_fdata()
    vol2 = nib.load(os.path.join(base_path, "ses01", "manual_brainmask/exp_param", "sub-Fabienne_ses-01_haste_3DHR_manual_bm_T-1_pipeline.nii.gz")).get_fdata()
    vol3 = nib.load(os.path.join(base_path, "ses01", "manual_brainmask/exp_param",
                                 "sub-Fabienne_ses-01_haste_3DHR_manual_bm_T13_pipeline.nii.gz")).get_fdata()
    vol4 = nib.load(os.path.join(base_path, "ses01", "manual_brainmask/exp_param",
                                 "sub-Fabienne_ses-01_haste_3DHR_manual_bm_T46_pipeline.nii.gz")).get_fdata()

    vols = {
        "default-param": vol1,
        "threshold_-1": vol2,
        "threshold_0.1_0.3": vol3,
        "threshold_0.4_0.6": vol4
    }
    indices = [20, 40, 60, 80, 100]

    fig, axes = plt.subplots(nrows=len(indices), ncols=len(vols), figsize=(15, 10))

    for i, idx in enumerate(indices):
        for j, (param, vol) in enumerate(vols.items()):
            ax = axes[i, j]
            axes[0, j].set_title(f"{param}", fontsize=12, fontweight='bold')
            slice_data = vol[:, :, idx]
            ax.imshow(slice_data, cmap="gray")
            ax.axis("off")

    # Ajustement de la mise en page
    plt.suptitle("Session 01 Fabienne")
    plt.tight_layout()
    plt.savefig("tmp.png")

    exit()
    for i in range(len(exp_list)):
        exp_param_folder = exp_list[i]
        param = params[i]
        name = names[i]
        for session in os.listdir(base_path):
            datas[session] = {}
            for mode in modes:
                print(f"Running {mode} for {session} with {param} param")
                subj_path = os.path.join(base_path, session)  # ../data/recons_folder/subj/session

                subj_session = f"sub-{subject}_ses-{session[3:]}"

                # Plot the anat image with the BM using the rejected slices file
                qc_recons.qc_rejected_slices(subj_path, subject, subj_session, mode, exp_param_folder=exp_param_folder, param=param, name=name)

                # Plot 1 snapshot per reconstruction
                qc_recons.qc_recons_bis(subj_path, subject, mode, exp_param_folder=exp_param_folder, param=param, name=name)

                qc_recons.qc_intensity(subj_path, subject, mode, subj_session, param="B")

                datas[session][mode] = {}
                if not exp_param_folder:
                    datas[session][mode]["anat"] = os.path.join(base_path, session, f"{mode}_brainmask", f"sub-{subject}_ses-{session[3:]}_haste_3DHR_{mode}_bm_pipeline.nii.gz")
                else:
                    datas[session][mode]["anat"] = os.path.join(base_path, session, f"exp_param/{mode}_brainmask", f"sub-{subject}_ses-{session[3:]}_haste_3DHR_{mode}_bm_{param}_pipeline.nii.gz")

        # plot the matplotlib table format for the qc:
        # 1 row per slice in the anat img, 1 col per method (manual, nifty, etc) / 1 file per session
        # qc_recons.qc_plot_table_recons(datas, subject, name)
        # Lines above are commented because it is not working properly. Need to fix the orientation of the images (dim prb ?)



