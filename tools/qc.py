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
        brain_data = np.transpose(brain_data, (2, 0, 1))
        brain_mask_data = np.transpose(brain_mask_data, (2, 0, 1))
        brain_mask_data = np.squeeze(brain_mask_data)

        brain_shape = brain_data.shape
        bm_shape = brain_mask_data.shape

        if debug:
            print(f"ANAT header: {anat_img.header}")
            print(f"BM header: {bm_img.header}")

            print(f"ANAT shape: {brain_shape}")
            print(f"BM shape: {brain_mask_data.shape}")

        if brain_shape != bm_shape:
            raise ValueError(f"Error shape: {brain_shape} | {bm_shape}")
        """
        anat_affine = anat_img.affine
        seg_affine = bm_img.affine
        
        # Calculer la transformation nécessaire pour aligner les volumes
        transform = np.linalg.inv(seg_affine).dot(anat_affine)

        # Appliquer la transformation au volume de segmentation
        # aligned_seg_data = affine_transform(brain_mask_data, transform[:3, :3], offset=transform[:3, 3],
        #                                    output_shape=brain_data.shape)

        slice_indices = np.random.randint(0, brain_data.shape[2], size=6)

        fig, axes = plt.subplots(2, 3, figsize=(12, 8))

        # Afficher les images
        for i, slice_idx in enumerate(slice_indices):
            ax = axes[i // 3, i % 3]
            ax.imshow(brain_data[:, :, slice_idx], cmap='gray')
            ax.imshow(brain_mask_data[:, :, slice_idx], cmap='Reds', alpha=0.3)
            ax.set_title(f'Slice {slice_idx}')
            ax.axis('off')

        plt.tight_layout()
        plt.savefig(file_figure_out)

        """
        # Afficher la coupe du cerveau

        anat_img_reoriented = nib.Nifti1Image(brain_data, anat_img.affine, anat_img.header)
        bm_img_reoriented = nib.Nifti1Image(brain_mask_data, bm_img.affine, bm_img.header)

        # Sauvegarde des fichiers réorganisés
        nib.save(anat_img_reoriented, path_anat_vol)
        nib.save(bm_img_reoriented, path_brainmask_vol)

        done = 0
        d_max = max(brain_shape)
        step = 15
        while (done < 1) and (d_max > 20):
            try:
                slices = {
                    'x': list(range(0, brain_shape[2], step)),
                    'y': list(range(0, brain_shape[1], step)),
                    'z': list(range(0, brain_shape[0], step))
                }
                nisnap.plot_segment(
                    [path_brainmask_vol],
                    bg=path_anat_vol,
                    slices=slices,
                    opacity=50,
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