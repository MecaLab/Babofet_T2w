import os
import sys
import nibabel as nib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import friedmanchisquare, wilcoxon
import itertools
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


def plot_full_comparison(raw_data, model_paths, model_names, file_id, output, axis=2, pct_range=(0.2, 0.8)):
    axis_names = {0: "SAGITTAL", 1: "CORONAL", 2: "AXIAL"}
    num_slices = 8
    num_models = len(model_paths)
    num_rows = 1 + num_models

    if not os.path.exists(output):
        os.makedirs(output)
    output_filename = os.path.join(output, f"segmentation_comparison_{axis_names[axis]}_{file_id}.png")

    z_max = raw_data.shape[axis]
    slice_indices = np.linspace(int(z_max * pct_range[0]), int(z_max * pct_range[1]), num_slices).astype(int)

    fig, axes = plt.subplots(num_rows, num_slices, figsize=(22, 3.5 * num_rows))
    fig.suptitle(f"Vue {axis_names[axis]} - {file_id}", fontsize=22, y=0.98, fontweight='bold')

    cmap_seg = plt.get_cmap('tab10', 5)
    all_row_names = ["IMAGE SOURCE"] + model_names

    for row in range(num_rows):
        if row == 0:
            data = raw_data
            current_cmap = 'gray'
            vmax_val = np.percentile(raw_data, 99)  # Optionnel: meilleur contraste
        else:
            # On ne charge le modèle que si nécessaire
            data = nib.load(model_paths[row - 1]).get_fdata()
            current_cmap = cmap_seg
            vmax_val = 4

        for col in range(num_slices):
            ax = axes[row, col]
            idx = slice_indices[col]

            # Extraction de la coupe selon l'axe
            if axis == 0:
                slice_data = data[idx, :, :]
            elif axis == 1:
                slice_data = data[:, idx, :]
            else:
                slice_data = data[:, :, idx]

            slice_data = np.rot90(slice_data)

            ax.imshow(slice_data, cmap=current_cmap,
                      vmin=0,
                      vmax=vmax_val,
                      interpolation='nearest')

            if row == 0:
                ax.set_title(f"Coupe {idx}\n", fontsize=11, fontweight='bold')
            if col == 0:
                ax.annotate(all_row_names[row], xy=(0, 0.5), xycoords='axes fraction',
                            xytext=(-20, 0), textcoords='offset points',
                            ha='right', va='center', fontsize=14, fontweight='bold')
            ax.axis('off')

    plt.subplots_adjust(left=0.2, right=0.9, top=0.9, bottom=0.1, wspace=0.05, hspace=0.2)
    cbar_ax = fig.add_axes([0.92, 0.15, 0.015, 0.4])
    fig.colorbar(plt.cm.ScalarMappable(cmap=cmap_seg, norm=plt.Normalize(0, 4)),
                 cax=cbar_ax, ticks=range(5))
    plt.savefig(output_filename, dpi=300)
    plt.close(fig)


def compute_dice(data1, data2):
    bin1 = (data1 > 0).astype(np.uint8)
    bin2 = (data2 > 0).astype(np.uint8)

    intersection = np.sum(bin1 * bin2)
    denominator = np.sum(bin1) + np.sum(bin2)

    if denominator == 0:
        return 1.0
    return (2. * intersection) / denominator


def run_stats(df):
    print("\n" + "=" * 30 + "\nRAPPORT STATISTIQUE\n" + "=" * 30)

    # On pivote pour avoir une colonne par paire de comparaison
    pivot_df = df.pivot(index=['Subject', 'Session'], columns='Pair', values='Dice').dropna()

    stat, p_f = friedmanchisquare(*(pivot_df[c] for c in pivot_df.columns))
    print(f"Test de Friedman (Global): p-value = {p_f:.4e}")

    print("\nComparaisons détaillées (Wilcoxon) :")
    results = []
    for p1, p2 in itertools.combinations(pivot_df.columns, 2):
        _, p_w = wilcoxon(pivot_df[p1], pivot_df[p2])
        results.append({"Comparaison": f"{p1} vs {p2}", "p-value": p_w, "Significatif": p_w < 0.05})

    print(pd.DataFrame(results).to_string(index=False))

if __name__ == "__main__":
    subjects = {
        "Borgne": [
            "ses06",
            "ses07",
            "ses08",
            "ses09",
            "ses10"
        ],
        "Bibi": [
            "ses05",
            "ses06",
            "ses07",
            "ses09"
        ],
        "Filoutte": [
            "ses05",
            "ses06",
            "ses07",
            "ses08",
            "ses09",
            "ses10"
        ],
        "Formule": [
            "ses05",
            "ses06",
            "ses07",
            "ses08",
            "ses09",
        ],
    }

    names = ["LongiSeg", "LongiSegDiff", "nnUNetLongi"]
    all_dice_results = []

    for subject in subjects:
        for session in subjects[subject]:
            print(f"Processing subject {subject}, session {session}...")

            raw_path = os.path.join(cfg.DATA_PATH, subject, session, "recons_rhesus/recon_template_space",
                                    "srr_template_debiased.nii.gz")
            raw_data = nib.load(raw_path).get_fdata()

            model_paths = [
                f"results_seg/longisegtrainer/{subject}/{subject}_{session}.nii.gz",
                f"results_seg/longisegtrainerdiffweighting/{subject}/{subject}_{session}.nii.gz",
                f"results_seg/nnunetlongi/{subject}/pred_{session}/{subject}_{session}.nii.gz",
                # f"inference_all/12_segmentations/{subject}_{session}.nii.gz",
            ]

            model_data_list = [nib.load(p).get_fdata() for p in model_paths]

            for (idx1, n1), (idx2, n2) in itertools.combinations(enumerate(names), 2):
                d_score = compute_dice(model_data_list[idx1], model_data_list[idx2])
                all_dice_results.append({
                    "Subject": subject,
                    "Session": session,
                    "Pair": f"{n1}_vs_{n2}",
                    "Dice": d_score
                })

            for a in [2, 1, 0]:
                print(f"\tProcessing axis {a}...")
                # plot_full_comparison(raw_data, model_paths, names, f"{subject}_{session}",
                #                     output="snapshots/model_comparison", axis=a, pct_range=(0.35, 0.70))

    df_stats = pd.DataFrame(all_dice_results)
    run_stats(df_stats)


    """
    Sans FORME et AZIZA:
        Test de Friedman (Global): p-value = 3.1592e-12
    
    Comparaisons détaillées (Wilcoxon) :
                                                  Comparaison  p-value  Significatif
    LongiSegDiff_vs_BestnnUNet vs LongiSegDiff_vs_nnUNetLongi   0.647655         False
    LongiSegDiff_vs_BestnnUNet vs LongiSeg_vs_BestnnUNet    0.000004          True
    LongiSegDiff_vs_BestnnUNet vs LongiSeg_vs_LongiSegDiff  0.000002          True
    LongiSegDiff_vs_BestnnUNet vs LongiSeg_vs_nnUNetLongi   0.348810         False
    LongiSegDiff_vs_BestnnUNet vs nnUNetLongi_vs_BestnnUNet 0.230513         False
    LongiSegDiff_vs_nnUNetLongi vs LongiSeg_vs_BestnnUNet   0.701181         False
    LongiSegDiff_vs_nnUNetLongi vs LongiSeg_vs_LongiSegDiff 0.000002          True
    LongiSegDiff_vs_nnUNetLongi vs LongiSeg_vs_nnUNetLongi  0.000010          True
    LongiSegDiff_vs_nnUNetLongi vs nnUNetLongi_vs_BestnnUNet0.388376         False
    LongiSeg_vs_BestnnUNet vs LongiSeg_vs_LongiSegDiff      0.000002          True
    LongiSeg_vs_BestnnUNet vs LongiSeg_vs_nnUNetLongi       0.756166         False
    LongiSeg_vs_BestnnUNet vs nnUNetLongi_vs_BestnnUNet     0.000395          True
    LongiSeg_vs_LongiSegDiff vs LongiSeg_vs_nnUNetLongi     0.000002          True
    LongiSeg_vs_LongiSegDiff vs nnUNetLongi_vs_BestnnUNet   0.000002          True
    LongiSeg_vs_nnUNetLongi vs nnUNetLongi_vs_BestnnUNet    0.002712          True
         
    Test de Friedman (Global): p-value = 1.4303e-15
    Sans FORME et AZIZA:
    Comparaisons détaillées (Wilcoxon) :
                                                  Comparaison      p-value  Significatif
    LongiSegDiff_vs_BestnnUNet vs LongiSegDiff_vs_nnUNetLongi 9.338708e-01         False
         LongiSegDiff_vs_BestnnUNet vs LongiSeg_vs_BestnnUNet 9.313226e-10          True
       LongiSegDiff_vs_BestnnUNet vs LongiSeg_vs_LongiSegDiff 9.313226e-10          True
        LongiSegDiff_vs_BestnnUNet vs LongiSeg_vs_nnUNetLongi 7.796160e-03          True
      LongiSegDiff_vs_BestnnUNet vs nnUNetLongi_vs_BestnnUNet 7.468256e-01         False
        LongiSegDiff_vs_nnUNetLongi vs LongiSeg_vs_BestnnUNet 1.106481e-01         False
      LongiSegDiff_vs_nnUNetLongi vs LongiSeg_vs_LongiSegDiff 4.656613e-10          True
       LongiSegDiff_vs_nnUNetLongi vs LongiSeg_vs_nnUNetLongi 4.656613e-09          True
     LongiSegDiff_vs_nnUNetLongi vs nnUNetLongi_vs_BestnnUNet 7.891259e-01         False
           LongiSeg_vs_BestnnUNet vs LongiSeg_vs_LongiSegDiff 3.615216e-03          True
            LongiSeg_vs_BestnnUNet vs LongiSeg_vs_nnUNetLongi 8.464598e-01         False
          LongiSeg_vs_BestnnUNet vs nnUNetLongi_vs_BestnnUNet 2.947409e-03          True
          LongiSeg_vs_LongiSegDiff vs LongiSeg_vs_nnUNetLongi 9.061266e-04          True
        LongiSeg_vs_LongiSegDiff vs nnUNetLongi_vs_BestnnUNet 4.718150e-04          True
         LongiSeg_vs_nnUNetLongi vs nnUNetLongi_vs_BestnnUNet 9.909525e-03          True
    
    """