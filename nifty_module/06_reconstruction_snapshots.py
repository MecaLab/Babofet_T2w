import os
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg
from tools import qc_recons
import numpy as np
import nibabel as nib
import matplotlib.pyplot as plt


def plot_histo(data, label):
    plt.hist(data.flatten(), bins=50, alpha=0.6, label=label)
    plt.xlabel("Intensité")
    plt.ylabel("Fréquence")
    plt.legend(loc="upper right")


def plot_intensity_profile(data, slice_index, axis=0, label=''):
    """Trace le profil d'intensité le long d'une ligne dans une tranche donnée."""
    if axis == 0:
        profile = data[slice_index, :, :].mean(axis=1)
    elif axis == 1:
        profile = data[:, slice_index, :].mean(axis=1)
    elif axis == 2:
        profile = data[:, :, slice_index].mean(axis=0)

    plt.plot(profile, label=label)
    plt.xlabel('Position')
    plt.ylabel('Intensité')
    plt.legend(loc='upper right')


if __name__ == "__main__":
    subject = "Fabienne"
    base_path = os.path.join(cfg.DATA_PATH, subject)
    modes = ["manual", "nifty", "mattia"]

    datas = {}
    # plot the matplotlib table format for the qc:
    # 1 row per slice in the anat img, 1 col per method (manual, nifty, etc)
    # 1 file per session
    name = "default-param"
    for session in os.listdir(base_path):
        datas[session] = {}
        for mode in modes:
            datas[session][mode] = {}
            datas[session][mode]["anat"] = os.path.join(base_path, session, f"{mode}_brainmask", f"sub-{subject}_ses-{session[3:]}_haste_3DHR_{mode}_bm_pipeline.nii.gz")

    # qc_recons.qc_plot_table_recons(datas, name)
    volume_1 = nib.load("/scratch/lbaptiste/data/recons_folder/Fabienne/ses01/manual_brainmask/exp_param/sub-Fabienne_ses-01_haste_3DHR_manual_bm_T-1_pipeline.nii.gz")
    volume_2 = nib.load("/scratch/lbaptiste/data/recons_folder/Fabienne/ses01/manual_brainmask/sub-Fabienne_ses-01_haste_3DHR_manual_bm_pipeline.nii.gz")

    volume_1_data = volume_1.get_fdata()
    volume_2_data = volume_2.get_fdata()

    plt.figure(figsize=(12, 6))
    plot_histo(volume_1_data, "Threshold -1")
    plot_histo(volume_2_data, "Default threshold")
    plt.savefig("tmp.png")
    plt.close()

    plt.figure(figsize=(12, 6))
    plot_intensity_profile(volume_1_data, 50, axis=2, label="Threshold -1")
    plot_intensity_profile(volume_2_data, 50, axis=2, label="Default threshold")
    plt.savefig("tmp2.png")
    plt.close()

    mean1, std1 = np.mean(volume_1_data), np.std(volume_1_data)
    mean2, std2 = np.mean(volume_2_data), np.std(volume_2_data)
    print(f'Volume 1 - Moyenne: {mean1} | Écart-type: {std1}')
    print(f'Volume 2 - Moyenne: {mean2} | Écart-type: {std2}')

    """# 1 snapshot per reconstruction
    modes = ["manual"]
    base_path = os.path.join(cfg.DATA_PATH, subject)

    for mode in modes:
        qc_recons.qc_recons_bis(base_path, subject, mode)"""

    """
    base_path = cfg.MESO_OUTPUT_PATH
    model = "niftymic"  # niftymic or nesvor
    mode = "manual"  # manual bm or nifty bm
    debug = False

    qc_recons.qc_recons(
        base_path,
        model,
        mode,
    )
    """