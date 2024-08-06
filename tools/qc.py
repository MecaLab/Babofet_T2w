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
            anat_data = anat_img.get_fdata()
            dims = anat_data.shape

            print(dims)

            done = 0
            d_max = min(240, dims[2]) #  d_max = 240
            step = 30
            while (done < 1) and (d_max > 20):
                try:
                    slices = {'x': list(range(30, min(d_max, dims[0]), step)),
                              'y': list(range(60, min(d_max, dims[1]), step)),
                              'z': list(range(0, min(d_max, dims[2]), step))}
                    nisnap.plot_segment(
                        path_brainmask_vol,
                        bg=path_anat_vol,
                        slices=slices,
                        figsize=figsize,
                        opacity=50,
                        samebox=True,
                        # labels=[1],
                        # contours=True,
                        savefig=file_figure_out,
                    )
                    done = 1
                except Exception as e:
                    print(e)
                    print(slices)
                    d_max -= 20
                    step = max(1, step - 5)
                    print("d_max is now set to ", d_max)


def qc_recontructed_3DHRvolume(path_anat_vol, file_figure_out):
    pass