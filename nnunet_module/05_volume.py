import os
import sys
import nibabel as nib
import matplotlib.pyplot as plt
import numpy as np


def compute_vol(mask, voxel_size, labels=[1, 2, 3, 4]):
    """
    Calcule le volume en mm^3 pour chaque label dans le masque.
    """
    volumes = {}
    for label in labels:
        bin_mask = (mask == label).astype(int)
        volume = np.sum(bin_mask) * voxel_size
        volumes[label] = volume
    return volumes


if __name__ == "__main__":
    subject = sys.argv[1]  # Nom du sujet, e.g., Fabienne / Formule / etc..
    model_id = sys.argv[2]  # ID du modèle, e.g., 1, 2, 3, 4 ...
    fusions_labels = True

    if fusions_labels:
        input_folder = "/scratch/lbaptiste/Babofet_T2w/snapshots/nnunet_res/fusion_labels"
    else:
        input_folder = f"/scratch/lbaptiste/Babofet_T2w/snapshots/nnunet_res/pred_dataset_{model_id}"

    output_path = "/scratch/lbaptiste/Babofet_T2w/snapshots/nnunet_res/volumes"

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    voxel_size = 0.5
    labels = [1, 2, 3, 4]  # Labels pour CSF, WM, GM, Ventricle
    labels_names = ["CSF", "WM", "GM", "Ventricle"]

    label_volumes = {label: [] for label in labels}

    sessions = []
    for file in sorted(os.listdir(input_folder)):
        if file.endswith(".nii.gz") and subject in file:
            print(f"Traitement de {file} pour le sujet {subject}...")
            session = file.split(".")[0].split("_")[-1]  # subject_sesXX.nii.gz => sesXX
            pred_path = os.path.join(input_folder, file)
            pred_img = nib.load(pred_path).get_fdata()

            vols = compute_vol(pred_img, voxel_size, labels)
            for label in labels:
                label_volumes[label].append(vols[label])
            sessions.append(session)

    fig, axes = plt.subplots(1, 4, figsize=(20, 6))
    for i, label in enumerate(labels):
        axes[i].plot(sessions, label_volumes[label], marker='o')
        axes[i].set_title(f'Label {labels_names[i]}')
        axes[i].set_xlabel('Session')
        axes[i].set_ylabel('Volume (mm³)')
        axes[i].grid(True)

    plt.tight_layout()
    plt.savefig(f"evolution_volumes_{subject}_{model_id}.png")