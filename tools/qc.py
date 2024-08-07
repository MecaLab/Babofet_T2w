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

        dims_anat = anat_img.shape
        dims_bm = bm_img.shape

        brain_data = anat_img.get_fdata()
        brain_mask_data = bm_img.get_fdata()

        print(brain_data.shape, dims_anat)
        print(brain_mask_data.shape, dims_bm)

        exit()

        slice_index = brain_data.shape[1] // 2

        brain_slice = brain_data[:, slice_index, :]
        mask_slice = brain_mask_data[:, slice_index, :]

        # Afficher la coupe du cerveau
        plt.figure(figsize=(6, 6))
        plt.title(f"Superposition de la coupe COR")
        plt.imshow(brain_slice, cmap='gray')
        plt.imshow(mask_slice, cmap='hot', alpha=0.5)
        plt.axis('off')

        plt.savefig(file_figure_out)

        """nisnap.plot_segment(
            path_brainmask_vol,
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