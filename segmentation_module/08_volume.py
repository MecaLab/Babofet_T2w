import os
import sys
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np

sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


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


def plot_one_subject(subject, input_folder, labels, labels_names, voxel_size):
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
    plt.savefig(os.path.join(output_path, f"evolution_volumes_{subject}_{model_id}.png"))


def plot_every_subject(input_folder, labels, labels_names, voxel_size):
    label_volumes = {label: [] for label in labels}
    for file in sorted(os.listdir(input_folder)):
        if file.endswith(".nii.gz"):
            subject_session = file.split(".")[0]  # SUJET_SESXX
            subject = "_".join(subject_session.split("_")[:-1])
            session = subject_session.split("_")[-1]  # SESXX
            pred_path = os.path.join(input_folder, file)
            pred_img = nib.load(pred_path).get_fdata()
            vols = compute_vol(pred_img, voxel_size, labels)

            for label in labels:
                if subject not in label_volumes[label]:
                    label_volumes[label][subject] = {"sessions": [], "volumes": []}
                label_volumes[label][subject]["sessions"].append(session)
                label_volumes[label][subject]["volumes"].append(vols[label])

    for label in labels:
        fig, ax = plt.subplots(figsize=(12, 6))
        for subject in label_volumes[label]:
            sessions = label_volumes[label][subject]["sessions"]
            volumes = label_volumes[label][subject]["volumes"]
            ax.plot(sessions, volumes, marker='o', label=subject)

        ax.set_title(f'Label {labels_names[label]}')
        ax.set_xlabel('Session')
        ax.set_ylabel('Volume (mm³)')
        ax.grid(True)
        ax.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(output_path, f"evolution_volumes_{labels_names[label]}.png"))
        plt.close()

if __name__ == "__main__":
    subject = sys.argv[1]  # Nom du sujet, e.g., Fabienne / Formule / etc..
    model_id = sys.argv[2]  # should be: 'fusion' or a model's ID
    model_type = sys.argv[3]  # should be: 'nnunet' or 'longiseg'

    if model_id == "fusion":
        input_folder = os.path.join(cfg.CODE_PATH, f"snapshots/{model_type}/fusion_labels")
    else:
        input_folder = os.path.join(cfg.CODE_PATH, f"snapshots/{model_type}/pred_dataset_{model_id}")

    input_folder = os.path.join(cfg.CODE_PATH, "nnunet_mattia")
    output_path = os.path.join(cfg.CODE_PATH, f"snapshots/{model_type}/volumes")

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    voxel_size = np.power(0.5, 3)
    labels = [2, 3]  # Labels pour CSF, WM, GM, Ventricle
    labels_names = ["WM", "GM"]

    # plot_one_subject(subject, input_folder, labels, labels_names, voxel_size)
    plot_every_subject(input_folder, labels, labels_names, voxel_size)

