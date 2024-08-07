""" tools for QC using snasphots

"""

import os
import numpy as np
import nibabel as nib
import nisnap
import matplotlib.pyplot as plt


def qc_brainmask(path_anat_vol, path_brainmask_vol, file_figure_out):
    """

    :param path_anat_vol: path of the nifty file
    :param path_brainmask_vol:
    :param file_figure_out:
    :return:
    """

    figsize = {'x': (18, 4), 'y': (18, 4), 'z': (18, 5)}

    if not os.path.exists(path_brainmask_vol):
        print(path_brainmask_vol + " not found, skip!")
    else:
        anat_img = nib.load(path_anat_vol)
        bm_img = nib.load(path_brainmask_vol)

        brain_data = anat_img.get_fdata()
        brain_mask_data = bm_img.get_fdata()

        if brain_data.shape != brain_mask_data.shape:
            raise ValueError("Error shape")

        slice_indices = [18, 21, 24, 27, 30, 33]  # Indices de coupes à afficher
        fig, axes = plt.subplots(1, len(slice_indices), figsize=(15, 5))

        for i, slice_idx in enumerate(slice_indices):
            ax = axes[i]
            ax.imshow(brain_data[:, slice_idx, :], cmap='gray')
            ax.imshow(brain_mask_data[:, slice_idx, :], cmap='Reds', alpha=0.5)
            ax.set_title(f'Slice {slice_idx}')
            ax.axis('off')

        plt.tight_layout()
        plt.savefig(file_figure_out)

        # Afficher la coupe du cerveau

        """nisnap.plot_segment(
            [path_brainmask_vol],
            bg=path_anat_vol,
            axes="x",
            figsize=figsize,
            opacity=50,
            samebox=True,
            # labels=[1],
            # contours=True,
            savefig=file_figure_out,
        )"""


def qc_recontructed_3DHRvolume(path_anat_vol, file_figure_out):
    pass