import os
import sys
import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


def compute_volume(subject, label, resolution=0.5):
    volumes_cm3 = []
    voxel_volume = resolution**3  # Volume of a single voxel in mm^3
    print(f"Computing volume for subject '{subject}' and label '{label}' with resolution {resolution} mm...")

    subject_path = os.path.join(cfg.BASE_NIOLON_PATH, "atlas_fetal_rhesus_v2", "Seg_Hemi", subject)

    timepoints = len(os.listdir(subject_path))

    for session in os.listdir(subject_path):
        session_path = os.path.join(subject_path, session)

        hemi_split_path = os.path.join(session_path, f"{subject}_{session}_hemi_corrected.nii.gz")

        img = nib.load(hemi_split_path)
        data = img.get_fdata()

        voxel_count = np.sum(np.isin(data, label))

        total_volume_mm3 = voxel_count * voxel_volume

        # 4. Convertir en cm³ (mL) pour l'affichage
        total_volume_cm3 = total_volume_mm3 / 1000.0

        volumes_cm3.append(total_volume_cm3)
        print(f"Fichier : {hemi_split_path} | Voxels : {voxel_count} | Volume : {total_volume_cm3:.3f} cm³")

    plt.figure(figsize=(10, 6))
    plt.plot(timepoints, volumes_cm3, marker='o', linestyle='-', linewidth=2, color='#2c3e50')

    plt.title(f'Évolution du volume de la matière blanche', fontsize=14)
    plt.xlabel('Points temporels (Acquisitions)', fontsize=12)
    plt.ylabel('Volume (cm³ ou mL)', fontsize=12)

    plt.xticks(timepoints)
    # plt.grid(True, linestyle='--', alpha=0.7)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    compute_volume("Borgne", 1, resolution=0.5)