""" tools for QC using snasphots

"""

import os
import numpy as np
import nibabel as nib
import nisnap
import matplotlib.pyplot as plt
from scipy.ndimage import affine_transform


def qc_brainmask(path_anat_vol, path_brainmask_vol, file_figure_out):
    """

    :param path_anat_vol: path of the nifty file
    :param path_brainmask_vol:
    :param file_figure_out:
    :return:
    """
    if not os.path.exists(path_brainmask_vol):
        print(path_brainmask_vol + " not found, skip!")
    else:
        anat_img = nib.load(path_anat_vol)
        bm_img = nib.load(path_brainmask_vol)

        brain_data = anat_img.get_fdata()
        brain_mask_data = bm_img.get_fdata()

        anat_affine = anat_img.affine
        seg_affine = bm_img.affine

        """# Calculer la transformation nécessaire pour aligner les volumes
        transform = np.linalg.inv(seg_affine).dot(anat_affine)

        # Appliquer la transformation au volume de segmentation
        aligned_seg_data = affine_transform(brain_mask_data, transform[:3, :3], offset=transform[:3, 3],
                                            output_shape=brain_data.shape)"""

        if brain_data.shape != brain_mask_data.shape:
            raise ValueError("Error shape")

        """slice_indices = np.random.randint(0, brain_data.shape[2], size=6)

        fig, axes = plt.subplots(2, 3, figsize=(12, 8))

        # Afficher les images
        for i, slice_idx in enumerate(slice_indices):
            ax = axes[i // 3, i % 3]
            ax.imshow(brain_data[:, :, slice_idx], cmap='gray')
            ax.imshow(aligned_seg_data[:, :, slice_idx], cmap='Reds', alpha=0.3)
            ax.set_title(f'Slice {slice_idx}')
            ax.axis('off')

        plt.tight_layout()
        plt.savefig(file_figure_out)"""

        # Afficher la coupe du cerveau

        nisnap.plot_segment(
            [path_brainmask_vol],
            bg=path_anat_vol,
            axes="x",
            opacity=50,
            samebox=True,
            # labels=[1],
            # contours=True,
            savefig=file_figure_out,
        )


def qc_recontructed_3DHRvolume(path_anat_vol, file_figure_out):
    pass