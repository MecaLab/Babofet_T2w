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

    fig, axes = plt.subplots(4, 2, figsize=(15, 16))
    labels = [1, 2, 3, 4]

    middle_slice_index = anat_data.shape[2] // 2
    anatomy_slice = anat_data[:, :, middle_slice_index]
    gt_slice = true_label_data[:, :, middle_slice_index]
    predicted_slice = pred_label_data[:, :, middle_slice_index]

    for i, label in enumerate(labels):
        # Superposer avec le masque GT
        gt_overlay = np.ma.masked_where(gt_slice != label, gt_slice)
        axes[i, 0].imshow(anatomy_slice, cmap='gray')
        axes[i, 0].imshow(gt_overlay, cmap='viridis', alpha=0.5)
        axes[i, 0].set_title(f'Label {label} - GT Mask')
        axes[i, 0].axis('off')

        # Superposer avec le masque prédit
        pred_overlay = np.ma.masked_where(predicted_slice != label, predicted_slice)
        axes[i, 1].imshow(anatomy_slice, cmap='gray')
        axes[i, 1].imshow(pred_overlay, cmap='viridis', alpha=0.5)
        axes[i, 1].set_title(f'Label {label} - Predicted Mask')
        axes[i, 1].axis('off')

    plt.tight_layout()
    plt.show()