import os
import sys
import nibabel as nib
#  import qc_recons as qc_recons
from nibabel.processing import resample_from_to
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


def normalize_min_max(volume):
    return (volume - volume.min()) / (volume.max() - volume.min())


def freedman_diaconis_bins(data):
    """Calcule le nombre optimal de bins selon la règle de Freedman-Diaconis."""
    q75, q25 = np.percentile(data, [75, 25])
    iqr = q75 - q25
    n = len(data)
    bin_width = 2 * iqr / (n ** (1/3))
    return int((data.max() - data.min()) / bin_width)


def plot_histo(vol1_masked, vol2_masked):

    vol1 = normalize_min_max(vol1_masked)
    vol2 = normalize_min_max(vol2_masked)

    hist_range = (min(vol1.min(), vol2.min()), max(vol1.max(), vol2.max()))
    bins = freedman_diaconis_bins(np.concatenate([vol1, vol2]))

    hist1, bins1 = np.histogram(vol1, bins=bins, density=True, range=hist_range)
    hist2, bins2 = np.histogram(vol2, bins=bins, density=True, range=hist_range)

    bin_centers = (bins1[:-1] + bins1[1:]) / 2  # Centres des bins
    wasserstein_dist = stats.wasserstein_distance(bin_centers, bin_centers, hist1 * np.diff(bins1),
                                                  hist2 * np.diff(bins2))

    title = f"{subject} {session}"
    output_path = "C:/Users/leroux.b/Pictures"
    output_filename = f"{subject}_{session}_comparison.png"
    plt.figure(figsize=(10, 6), facecolor='white')
    plt.plot(bin_centers, hist1, label='Niftymic', linestyle='-', alpha=0.7)
    plt.plot(bin_centers, hist2, label="Nesvor", linestyle='--', alpha=0.7)
    plt.title(f"{title}\nWasserstein Distance: {wasserstein_dist:.4f}\nBins: {bins}")
    plt.xlabel("Intensité")
    plt.ylabel("Densité")
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.savefig(os.path.join(output_path, output_filename))
    plt.close()


if __name__ == "__main__":

    subject = "Fabienne"

    uncorrected_bias_path = os.path.join(cfg.BASE_NIOLON_PATH, "bounti/svrtk_BOUNTI/input_SRR_niftymic/haste/", subject)
    corrected_bias_path = os.path.join(cfg.BASE_NIOLON_PATH, "bounti/svrtk_BOUNTI/input_SRR_niftymic/haste/", f"{subject}_bc")

    bm_path = os.path.join(cfg.BASE_NIOLON_PATH, "bounti/svrtk_BOUNTI/output_BOUNTI_seg/haste/", subject)

    for session in os.listdir(uncorrected_bias_path):
        print(f"Computing session {session}")

        uncorrected_file = os.path.join(uncorrected_bias_path, session, "reo-SVR-output-brain_rhesus.nii.gz")
        corrected_file = os.path.join(corrected_bias_path, session, f"{subject}_{session}_reo-SVR-output-brain_rhesus_withbc.nii.gz")

        niftymic_bm_file = os.path.join(bm_path, session, "reo-SVR-output-brain_rhesus-mask-bet-1.nii.gz")

        if not os.path.exists(niftymic_bm_file):
            print(f"File {uncorrected_file} does not exist, skipping...")
            continue

    """
    subject = "Formule"
    
    niftymic_path = f"W:/meca/data/babofet_DB/2024_new_stuff/bounti/svrtk_BOUNTI/input_SRR_niftymic/haste/{subject}"
    niftymic_bm_path = f"W:/meca/data/babofet_DB/2024_new_stuff/bounti/svrtk_BOUNTI/output_BOUNTI_seg/haste/{subject}"
    nesvor_path = f"C:/Users/leroux.b/Documents/Archive (1)/res-{subject}"
    
    
    for session in os.listdir(niftymic_path):
        print(f"Computing session {session}")
        niftymic_file = os.path.join(niftymic_path, session, "reo-SVR-output-brain_rhesus.nii.gz")
        if not os.path.exists(niftymic_file):
            print(f"File {niftymic_file} does not exist, skipping...")
            continue
        niftymic_bm_file = os.path.join(niftymic_bm_path, session, "reo-SVR-output-brain_rhesus-mask-bet-1.nii.gz")
    
        nesvor_filename = f"sub-{subject}_ses-{session[3:]}_T2_HASTE_nesvor_rigide.nii.gz"
        nesvor_bm_filename = f"sub-{subject}_ses-{session[3:]}_T2_HASTE_nesvor_rigide-mask.nii.gz"
    
        nesvor_file = os.path.join(nesvor_path, nesvor_filename)
        if not os.path.exists(nesvor_file):
            print(f"File {nesvor_file} does not exist, skipping...")
            continue
    
        nesvor_bm_file = os.path.join(nesvor_path, nesvor_bm_filename)
    
        niftymic_data = nib.load(niftymic_file).get_fdata()
        nesvor_data = nib.load(nesvor_file).get_fdata()
    
        niftymic_bm_data = nib.load(niftymic_bm_file).get_fdata()
        nesvor_bm_data = nib.load(nesvor_bm_file).get_fdata()
    
        vol1_masked = niftymic_data[niftymic_bm_data > 0]
        vol2_masked = nesvor_data[nesvor_bm_data > 0]
    
        plot_histo(vol1_masked, vol2_masked)
        """
