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
    print(data.shape)
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

    """
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
    

    # 1 snapshot per reconstruction
    modes = ["manual"]
    base_path = os.path.join(cfg.DATA_PATH, subject)

    for mode in modes:
        qc_recons.qc_recons_bis(base_path, subject, mode)
    """

    volume_ref = nib.load("/scratch/lbaptiste/data/recons_folder/Fabienne/ses01/manual_brainmask/sub-Fabienne_ses-01_haste_3DHR_manual_bm_pipeline.nii.gz")
    volume_1 = nib.load("/scratch/lbaptiste/data/recons_folder/Fabienne/ses01/manual_brainmask/exp_param/sub-Fabienne_ses-01_haste_3DHR_manual_bm_T-1_pipeline.nii.gz")
    volume_2 = nib.load("/scratch/lbaptiste/data/recons_folder/Fabienne/ses01/manual_brainmask/exp_param/sub-Fabienne_ses-01_haste_3DHR_manual_bm_T13_pipeline.nii.gz")
    volume_3 = nib.load("/scratch/lbaptiste/data/recons_folder/Fabienne/ses01/manual_brainmask/exp_param/sub-Fabienne_ses-01_haste_3DHR_manual_bm_T46_pipeline.nii.gz")

    volume_ref_data = volume_ref.get_fdata()
    volume_1_data = volume_1.get_fdata()
    volume_2_data = volume_2.get_fdata()
    volume_3_data = volume_3.get_fdata()

    origin_output_path = "/scratch/lbaptiste/Babofet_T2w/snapshots"

    """plt.figure(figsize=(12, 6))
    plot_histo(volume_1_data, "Threshold -1")
    plot_histo(volume_2_data, "Threshold 13")
    plot_histo(volume_3_data, "Threshold 46")
    plot_histo(volume_ref_data, "Default threshold")
    plt.savefig(os.path.join(origin_output_path, "histo_tsc.png"))
    plt.close()"""

    plt.figure(figsize=(12, 6))
    idxs = [25]
    for idx in idxs:
        plot_intensity_profile(volume_1_data, idx, axis=2, label=f"Threshold -1 ({idx})")
        plot_intensity_profile(volume_2_data, idx, axis=2, label=f"Threshold 0.1/0.3 ({idx})")
        plot_intensity_profile(volume_3_data, idx, axis=2, label=f"Threshold 0.4/0.6 ({idx})")
        plot_intensity_profile(volume_ref_data, idx, axis=2, label=f"Default two step cycle ({idx})")
    plt.savefig(os.path.join(origin_output_path, "intensity_threshold.png"))
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