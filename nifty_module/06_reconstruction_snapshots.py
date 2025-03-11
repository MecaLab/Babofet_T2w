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

    subject = "Fabienne"
    base_path = os.path.join(cfg.DATA_PATH, subject)
    modes = ["manual", "nifty"]
    datas = {}

    exp_param_folder = False
    param = None

    if not exp_param_folder:
        name = "default-param"
    else:
        name = param

    for session in os.listdir(base_path):
        datas[session] = {}
        for mode in modes:
            print(f"Session {session} - Mode {mode}")
            subj_path = os.path.join(base_path, session)
            subj_session = f"sub-{subject}_ses-{session[3:]}"

            # Plot the anat image with the BM using the rejected slices file
            # qc_recons.qc_rejected_slices(subj_path, subject, subj_session, mode)

            # Plot 1 snapshot per reconstruction
            # qc_recons.qc_recons_bis(base_path, subject, mode, exp_param_folder=exp_param_folder, param=param)
            datas[session][mode] = {}

            if not exp_param_folder:
                datas[session][mode]["anat"] = os.path.join(base_path, session, f"{mode}_brainmask", f"sub-{subject}_ses-{session[3:]}_haste_3DHR_{mode}_bm_pipeline.nii.gz")
            else:
                datas[session][mode]["anat"] = os.path.join(base_path, session, f"exp_param/{mode}_brainmask", f"sub-{subject}_ses-{session[3:]}_haste_3DHR_{mode}_bm_{param}_pipeline.nii.gz")

        # plot the matplotlib table format for the qc:
        # 1 row per slice in the anat img, 1 col per method (manual, nifty, etc) / 1 file per session
        qc_recons.qc_plot_table_recons(datas, subject, name)
    exit()

    """

    session_id = "09"

    volume_ref = nib.load(f"/scratch/lbaptiste/data/recons_folder/Fabienne/ses{session_id}/manual_brainmask/sub-Fabienne_ses-{session_id}_haste_3DHR_manual_bm_pipeline.nii.gz")
    volume_1 = nib.load(f"/scratch/lbaptiste/data/recons_folder/Fabienne/ses{session_id}/manual_brainmask/exp_param/sub-Fabienne_ses-{session_id}_haste_3DHR_manual_bm_T-1_pipeline.nii.gz")
    volume_2 = nib.load(f"/scratch/lbaptiste/data/recons_folder/Fabienne/ses{session_id}/manual_brainmask/exp_param/sub-Fabienne_ses-{session_id}_haste_3DHR_manual_bm_T13_pipeline.nii.gz")
    volume_3 = nib.load(f"/scratch/lbaptiste/data/recons_folder/Fabienne/ses{session_id}/manual_brainmask/exp_param/sub-Fabienne_ses-{session_id}_haste_3DHR_manual_bm_T46_pipeline.nii.gz")

    volume_ref_data = volume_ref.get_fdata()
    volume_1_data = volume_1.get_fdata()
    volume_2_data = volume_2.get_fdata()
    volume_3_data = volume_3.get_fdata()

    origin_output_path = "/scratch/lbaptiste/Babofet_T2w/snapshots"

    fig, axs = plt.subplots(1, 4, figsize=(24, 10))
    idxs = [30, 40, 50, 60]
    for i, idx in enumerate(idxs):
        plot_histo(volume_1_data, "Threshold -1", slice_index=idx, ax=axs[i])
        plot_histo(volume_2_data, "Threshold 0.1/0.3", slice_index=idx, ax=axs[i])
        plot_histo(volume_3_data, "Threshold 0.4/0.6", slice_index=idx, ax=axs[i])
        plot_histo(volume_ref_data, "Default threshold", slice_index=idx, ax=axs[i])
    plt.tight_layout()
    plt.savefig(os.path.join(origin_output_path, f"threshold_histo_{session_id}.png"))
    plt.close()

    fig, axs = plt.subplots(1, 4, figsize=(22, 10))
    for i, idx in enumerate(idxs):
        plot_intensity_profile(volume_1_data, idx, axis=2, label=f"Threshold -1", ax=axs[i])
        plot_intensity_profile(volume_2_data, idx, axis=2, label=f"Threshold 0.1/0.3 ", ax=axs[i])
        plot_intensity_profile(volume_3_data, idx, axis=2, label=f"Threshold 0.4/0.6", ax=axs[i])
        plot_intensity_profile(volume_ref_data, idx, axis=2, label=f"Default threshold", ax=axs[i])
        axs[i].set_title(f"Slice {idx}")
    plt.tight_layout()
    plt.savefig(os.path.join(origin_output_path, f"threshold_intensity_{session_id}.png"))
    plt.close()

    mean1, std1 = np.mean(volume_ref_data), np.std(volume_ref_data)
    mean2, std2 = np.mean(volume_1_data), np.std(volume_1_data)
    mean3, std3 = np.mean(volume_2_data), np.std(volume_2_data)
    mean4, std4 = np.mean(volume_3_data), np.std(volume_3_data)
    print(f'Volume 1 (ref) - Moyenne: {mean1} | Écart-type: {std1}')
    print(f'Volume 2 - Moyenne: {mean2} | Écart-type: {std2}')
    print(f'Volume 3 - Moyenne: {mean3} | Écart-type: {std3}')
    print(f'Volume 4 - Moyenne: {mean4} | Écart-type: {std4}')
    """
