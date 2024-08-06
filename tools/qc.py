""" tools for QC using snasphots

"""

import os
import numpy as np
import nibabel as nib
import nisnap


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
        if os.path.exists(file_figure_out):
            print(file_figure_out + " already exists, skip!")
        else:

            anat_img = nib.load(path_anat_vol)
            bm_img = nib.load(path_brainmask_vol)

            dims_anat = anat_img.shape
            dim_bm = bm_img.shape

            print(dims_anat, dim_bm)
            nisnap.plot_segment(
                path_brainmask_vol,
                bg=path_anat_vol,
                axes="x",
                figsize=figsize,
                opacity=50,
                samebox=True,
                # labels=[1],
                # contours=True,
                savefig=file_figure_out,
            )


def qc_recontructed_3DHRvolume(path_anat_vol, file_figure_out):
    pass