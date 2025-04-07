import os
import nibabel as nib
from nibabel.processing import resample_from_to
import numpy as np
import matplotlib.pyplot as plt
from skimage.measure import profile_line

subject = "Aziza"
base_path = f"../data/recons_folder/{subject}/"
sessions = ["01", "05", "09"]

views = ["coronal", "axial", "sagital"]


for session in sessions:
    vol_1_path = os.path.join(base_path, f"ses{session}/manual_brainmask", f"sub-{subject}_ses-{session}_haste_3DHR_manual_bm_pipeline.nii.gz")
    mask_1_path = os.path.join(base_path, f"ses{session}/manual_brainmask", f"sub-{subject}_ses-{session}_haste_3DHR_manual_bm_pipeline_mask.nii.gz")

    """vol_2_path = os.path.join(base_path, f"ses{session}/mattia_brainmask", f"sub-{subject}_ses-{session}_haste_3DHR_mattia_bm_pipeline.nii.gz")
    mask_2_path = os.path.join(base_path, f"ses{session}/mattia_brainmask", f"sub-{subject}_ses-{session}_haste_3DHR_mattia_bm_pipeline_mask.nii.gz")"""

    vol_2_path = os.path.join(base_path, f"ses{session}/manual_brainmask/exp_param", f"sub-{subject}_ses-{session}_haste_3DHR_manual_bm_ISO3_pipeline.nii.gz")
    mask_2_path = os.path.join(base_path, f"ses{session}/manual_brainmask/exp_param", f"sub-{subject}_ses-{session}_haste_3DHR_manual_bm_ISO3_pipeline_mask.nii.gz")

    vol1 = nib.load(vol_1_path)
    vol2 = nib.load(vol_2_path)

    mask1_data = nib.load(mask_1_path).get_fdata()
    mask_data2 = nib.load(mask_2_path)

    data1 = vol1.get_fdata()

    nii2_resampled = resample_from_to(vol2, vol1)
    data2_resampled = nii2_resampled.get_fdata()

    mask2_resampled = resample_from_to(mask_data2, vol1, order=0).get_fdata()

    view_idxs = [25, 50, 65, 75, 90]

    for view in views:
        for view_idx in view_idxs:
            png_filename = f"comparaison_{subject.lower()}_ses-{session}_{view}_{view_idx}.png"
            if view == "axial":
                slice_idx = view_idx  # data1.shape[2]//2  # Coupe axiale
                slice_data1 = data1[:, :, slice_idx]
                slice_data_resampled = data2_resampled[:, :, slice_idx]
                slice_mask1 = mask1_data[:, :, slice_idx]
                slice_mask2 = mask2_resampled[:, :, slice_idx]
            elif view == "sagital":
                slice_idx = view_idx  # data1.shape[1] // 2  # Coupe sagital
                slice_data1 = data1[:, slice_idx, :]
                slice_data_resampled = data2_resampled[:, slice_idx, :]
                slice_mask1 = mask1_data[:, slice_idx, :]
                slice_mask2 = mask2_resampled[:, slice_idx, :]
            elif view == "coronal":
                slice_idx = view_idx  # data1.shape[0] // 2  # Coupe sagital
                slice_data1 = data1[slice_idx, :, :]
                slice_data_resampled = data2_resampled[slice_idx, :, :]
                slice_mask1 = mask1_data[slice_idx, :, :]
                slice_mask2 = mask2_resampled[slice_idx, :, :]

            # Définir plusieurs lignes horizontales à analyser
            """y_values = [50, 60, 70, 80, 90]  # Plusieurs valeurs de y
            x1, x2 = 0, 120  # Début et fin de la ligne"""
            y_values = np.where(np.any(slice_mask1 > 0, axis=1))[0]  # Prend les lignes contenant du masque
            if len(y_values) > 3:
                y_values = y_values[::max(1, len(y_values) // 3)]  # Évite un pas de 0

            # Déterminer le nombre de lignes

            if len(y_values) == 0:
                print(f"Aucune ligne trouvée pour {view} à l'indice {view_idx}, masque vide ?")
                continue  # Passe à l'itération suivante

            n_rows = len(y_values)
            fig, axes = plt.subplots(n_rows, 4, figsize=(19, 5 * n_rows))

            for i, y in enumerate(y_values):
                x1, x2 = np.where(slice_mask1[y, :] > 0)[0][[0, -1]]

                # Extraire les profils d'intensité pour cette ligne y
                intensity1 = profile_line(slice_data1, (y, x1), (y, x2))
                intensity2 = profile_line(slice_data_resampled, (y, x1), (y, x2))
                intensity_diff = np.subtract(intensity1, intensity2)
                intensity_diff_percent = 100 * (np.array(intensity1) - np.array(intensity2)) / np.array(intensity1)

                axes[i, 0].imshow(slice_data1, cmap="gray")
                axes[i, 0].imshow(slice_mask1, cmap="Reds", alpha=0.3)  # Masque en transparence
                axes[i, 0].plot([x1, x2], [y, y], 'r-')  # Ligne rouge sur la coupe
                axes[i, 0].set_title(f"Coupe originale (y={y})")

                axes[i, 1].imshow(slice_data_resampled, cmap="gray")
                axes[i, 1].imshow(slice_mask2, cmap="Reds", alpha=0.3)  # Masque en transparence
                axes[i, 1].plot([x1, x2], [y, y], 'r-')  # Ligne rouge sur la coupe
                axes[i, 1].set_title(f"Coupe rééchantillonnée (y={y})")

                axes[i, 2].plot(intensity1, label="Original", linestyle="dashed")
                axes[i, 2].plot(intensity2, label="Resampled", linestyle="solid")
                axes[i, 2].set_xlabel("Position le long de la ligne")
                axes[i, 2].set_ylabel("Intensité")
                axes[i, 2].legend()
                axes[i, 2].grid()
                axes[i, 2].set_title(f"Profil d'intensité (y={y})")

                axes[i, 3].plot(intensity_diff_percent, label="Variation (%)", color="purple")
                axes[i, 3].axhline(0, color="black", linestyle="--", label="Zéro Variation")  # Ligne de base à zéro
                axes[i, 3].set_xlabel("Position le long de la ligne")
                axes[i, 3].set_ylabel("Variation d'intensité (%)")
                axes[i, 3].grid()
                axes[i, 3].set_title(f"Variation en pourcentage (y={y})")

            # Affichage global
            plt.tight_layout()
            plt.savefig(png_filename)
            plt.close()
