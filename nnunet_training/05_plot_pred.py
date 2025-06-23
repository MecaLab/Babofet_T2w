import os
import sys
import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


def overlay_masks(image_data, mask_data, label):
    """
    Superpose les masques sur l'image et retourne l'image superposée pour un label donné.
    """
    overlay_image = np.copy(image_data)
    overlay_image[mask_data == label] = 255
    return overlay_image


if __name__ == "__main__":
    subject = sys.argv[1]
    session = sys.argv[2]

    base_path = os.path.join(cfg.SEG_OUTPUT_PATH_NIOLON, subject, session)

    anat_img = os.path.join(cfg.SEG_INPUT_PATH_NIOLON, subject, session, "reo-SVR-output-brain_rhesus.nii.gz")
    true_label_path = os.path.join(base_path, "reo-SVR-output-brain_rhesus-mask-brain_bounti-4.nii.gz")
    pred_label_path = os.path.join(base_path, "pred_Borgne_ses05.nii.gz")

    anat_img = nib.load(anat_img)
    anat_data = anat_img.get_fdata()

    true_label_img = nib.load(true_label_path)
    true_label_data = true_label_img.get_fdata()

    pred_label_img = nib.load(pred_label_path)
    pred_label_data = pred_label_img.get_fdata()

    fig, axs = plt.subplots(4, 2, figsize=(12, 24))

    for label in range(4):
        # Superposer et afficher le masque 1
        image_superposee1 = overlay_masks(anat_data, true_label_data, label)
        axs[label, 0].imshow(image_superposee1[:, :, anat_data.shape[2] // 2], cmap='jet')
        axs[label, 0].set_title(f'Label {label} - True mask')

        # Superposer et afficher le masque 2
        image_superposee2 = overlay_masks(anat_data, pred_label_data, label)
        axs[label, 1].imshow(image_superposee2[:, :, anat_data.shape[2] // 2], cmap='jet')
        axs[label, 1].set_title(f'Label {label} - Pred mask')

    # Ajuster l'espacement entre les sous-graphiques
    plt.tight_layout()

    # Afficher la figure
    plt.show()