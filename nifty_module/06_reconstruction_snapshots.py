import os
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg
from tools import qc_recons
import numpy as np
import nibabel as nib
import matplotlib.pyplot as plt
from scipy import stats


def freedman_diaconis_bins(data):
    """Calcule le nombre optimal de bins selon la règle de Freedman-Diaconis."""
    q75, q25 = np.percentile(data, [75, 25])
    iqr = q75 - q25
    n = len(data)
    bin_width = 2 * iqr / (n ** (1/3))
    return int((data.max() - data.min()) / bin_width)


def normalize_min_max(volume):
    return (volume - volume.min()) / (volume.max() - volume.min())


def plot_histo(vol1, vol2, title):
    vol1 = normalize_min_max(vol1)
    vol2 = normalize_min_max(vol2)

    hist_range = (min(vol1.min(), vol2.min()), max(vol1.max(), vol2.max()))
    bins = freedman_diaconis_bins(np.concatenate([vol1, vol2]))

    hist1, bins1 = np.histogram(vol1, bins=bins, density=True, range=hist_range)
    hist2, bins2 = np.histogram(vol2, bins=bins, density=True, range=hist_range)

    bin_centers = (bins1[:-1] + bins1[1:]) / 2  # Centres des bins
    wasserstein_dist = stats.wasserstein_distance(bin_centers, bin_centers, hist1 * np.diff(bins1), hist2 * np.diff(bins2))
    print(f"Wasserstein distance: {wasserstein_dist}")

    plt.figure(figsize=(10, 6))
    plt.plot(bin_centers, hist1, label='Volume 1', linestyle='-', alpha=0.7)
    plt.plot(bin_centers, hist2, label='Volume 2', linestyle='--', alpha=0.7)
    plt.title(f"{title}\n(Wasserstein Distance = {wasserstein_dist:.4f})")
    plt.legend()
    plt.xlabel("Intensité")
    plt.ylabel("Densité")
    plt.grid()
    plt.savefig(f"{title}.png")


if __name__ == "__main__":
    subject = sys.argv[1]
    base_path = os.path.join(cfg.DATA_PATH, subject)
    modes = ["manual"]
    datas = {}

    param = "T13"
    session = "09"

    vol_1 = nib.load(f"../data/recons_folder/Fabienne/ses{session}/manual_brainmask/sub-Fabienne_ses-{session}_haste_3DHR_manual_bm_pipeline.nii.gz").get_fdata()
    vol_2 = nib.load(f"../data/recons_folder/Fabienne/ses{session}/manual_brainmask/exp_param/sub-Fabienne_ses-{session}_haste_3DHR_manual_bm_{param}_pipeline.nii.gz").get_fdata()

    bm_1 = nib.load(f"../data/recons_folder/Fabienne/ses{session}/manual_brainmask/sub-Fabienne_ses-{session}_haste_3DHR_manual_bm_pipeline_mask.nii.gz").get_fdata()
    bm_2 = nib.load(f"../data/recons_folder/Fabienne/ses{session}/manual_brainmask/exp_param/sub-Fabienne_ses-{session}_haste_3DHR_manual_bm_{param}_pipeline.nii.gz").get_fdata()

    volume1_masked = vol_1[bm_1 > 0]
    volume2_masked = vol_2[bm_2 > 0]

    plot_histo(volume1_masked, volume2_masked, f"Fabienne_ses09 default vs {param}")

    """
    exp_list = [False, True, True, True, ] # True, True, True, True]
    params = [None, "T-1", "T13", "T46", ] # "B1", "B1_T-1", "B1_T13", "B1_T46"]
    names = ["default-param", "threshold_-1", "threshold_0.1_0.3", "threshold_0.4_0.6", ] # "bias-field-correction", "bias-field-correction_threshold_-1", "bias-field-correction_threshold_0.1_0.3", "bias-field-correction_threshold_0.4_0.6"]

    for i in range(len(exp_list)):
        exp_param_folder = exp_list[i]
        param = params[i]
        name = names[i]
        for session in os.listdir(base_path):
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
        # plot the matplotlib table format for the qc:
        # 1 row per slice in the anat img, 1 col per method (manual, nifty, etc) / 1 file per session
        # qc_recons.qc_plot_table_recons(datas, subject, name)
        # Lines above are commented because it is not working properly. Need to fix the orientation of the images (dim prb ?)"""



