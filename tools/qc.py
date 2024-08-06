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

        print(path_brainmask_vol)
        print(path_anat_vol)

        anat_img = nib.load(path_anat_vol)
        bm_img = nib.load(path_brainmask_vol)
        """
        dims_anat = anat_img.shape
        dim_bm = bm_img.shape
        """

        brain_data = anat_img.get_fdata()
        brain_mask_data = bm_img.get_fdata()

        slice_index = brain_data.shape[0] // 2

        # Afficher la coupe du cerveau
        plt.figure(figsize=(6, 6))

        plt.title("Superposition de la coupe de cerveau et du brainmask")
        plt.imshow(brain_data[:, :, slice_index], cmap='gray')
        plt.imshow(brain_mask_data[:, :, slice_index], cmap='hot',
                   alpha=0.3)  # Ajuster l'alpha pour la transparence
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