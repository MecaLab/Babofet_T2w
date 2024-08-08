""" tools for QC using snasphots

"""

import os
import numpy as np
import nibabel as nib
import nisnap
import matplotlib.pyplot as plt
from scipy.ndimage import affine_transform


def qc_brainmask(path_anat_vol, path_brainmask_vol, file_figure_out, debug=False):
    """

    :param path_anat_vol: path of the nifty file
    :param path_brainmask_vol:
    :param file_figure_out:
    :return:
    """
    if not os.path.exists(path_brainmask_vol):
        print(path_brainmask_vol + " not found, skip!")
    else:
        figsize = {'x': (18, 4), 'y': (18, 4), 'z': (18, 5)}
        anat_img = nib.load(path_anat_vol)
        bm_img = nib.load(path_brainmask_vol)

        brain_data = anat_img.get_fdata()
        brain_mask_data = bm_img.get_fdata()

        # From (x, y, z) to (z, x, y)
        if brain_data.shape[0] > brain_data.shape[-1]:
            brain_data = np.transpose(brain_data, (2, 0, 1))
            if debug:
                print(f"ANAT shape after Transpose: {brain_data.shape}")

        brain_mask_data = np.squeeze(brain_mask_data)
        if brain_mask_data.shape != brain_data.shape:
            if debug:
                brain_mask_data = np.transpose(brain_mask_data, (2, 0, 1))
                print(f"ANAT shape after Transpose: {brain_data.shape}")

        brain_shape = brain_data.shape
        bm_shape = brain_mask_data.shape

        if debug:
            print(f"ANAT header: {anat_img.header}")
            print(f"BM header: {bm_img.header}")

            print(f"ANAT shape: {brain_shape}")
            print(f"BM shape: {bm_shape}")

        if brain_shape != bm_shape:
            raise ValueError(f"Error shape: {brain_shape} | {bm_shape}")

        # Afficher la coupe du cerveau

        anat_img_reoriented = nib.Nifti1Image(brain_data, anat_img.affine, anat_img.header)
        bm_img_reoriented = nib.Nifti1Image(brain_mask_data, bm_img.affine, bm_img.header)

        # Sauvegarde des fichiers réorganisés
        nib.save(anat_img_reoriented, path_anat_vol)
        nib.save(bm_img_reoriented, path_brainmask_vol)

        done = 0
        d_max = max(brain_shape)
        step = 4
        while (done < 1) and (d_max > 20):
            try:
                slices = {
                    'x': list(range(0, brain_shape[2], 4)),
                    'y': list(range(0, brain_shape[1], step)),
                    'z': list(range(0, brain_shape[0], step))
                }
                nisnap.plot_segment(
                    [path_brainmask_vol],
                    bg=path_anat_vol,
                    # slices=range(160, 174, 2),
                    opacity=50,
                    axes="AS",
                    figsize=figsize,
                    samebox=True,
                    # labels=[1],
                    # contours=True,
                    savefig=file_figure_out,
                )
                done = 1
            except Exception as e:
                d_max -= 20
                step = max(step - 5, 1)
                print(f"Error: {e} | d_max is now set to {d_max}")



def qc_recontructed_3DHRvolume(path_anat_vol, file_figure_out):
    pass