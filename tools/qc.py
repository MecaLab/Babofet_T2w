""" tools for QC using snasphots

"""

import os
import numpy as np
import nibabel as nib
import nisnap
import tempfile


def qc_brainmask(path_anat_vol, path_brainmask_vol, file_figure_out, mode, debug=False):
    """
    :param path_anat_vol: path of the nifty file
    :param path_brainmask_vol: path of the nifty file (brainmask)
    :param file_figure_out: path of the output file
    :return:
    """

    """elif os.path.exists(file_figure_out):
        print(f"{file_figure_out} already exist, skip!")"""
    if not os.path.exists(path_brainmask_vol):
        print(path_brainmask_vol + " not found, skip!")
    else:
        figsize = {'z': (10, 7)}
        anat_img = nib.load(path_anat_vol)
        bm_img = nib.load(path_brainmask_vol)

        brain_data = anat_img.get_fdata()
        brain_mask_data = bm_img.get_fdata()

        with tempfile.NamedTemporaryFile(suffix=".nii.gz") as tmpfile_mask:

            data = np.ones_like(brain_mask_data)
            data[brain_mask_data == 1] = 2

            if debug:
                print("Before squeeze: ", brain_data.shape, data.shape)

            # the mask have a unique last dim. Exemple: (320, 320, 32, 1))
            data = np.squeeze(data)

            if debug:
                print("After squeeze: ", brain_data.shape, data.shape)

            # Convert shape form (dim1, dim2, nb_slice) to (nb_slice, dim1, dim2)
            if mode == "niftymic":
                brain_data = np.transpose(brain_data, (2, 0, 1))
                data = np.transpose(data, (2, 0, 1))
            elif mode == "nesvor":
                brain_data = np.transpose(brain_data, (2, 0, 1))
                if data.shape[0] > data.shape[-1]:
                    data = np.transpose(data, (2, 0, 1))

            if debug:
                print("After transpose: ", brain_data.shape, data.shape)

            anat_img_reoriented = nib.Nifti1Image(brain_data, anat_img.affine, anat_img.header)

            # Used to store the transposed anat img. This file will be deleted at the end of the function
            tmp_filename = "tmp.nii.gz"

            nib.save(anat_img_reoriented, tmp_filename)

            fake_mask = nib.Nifti1Image(
                data,
                affine=bm_img.affine,
                header=bm_img.header,
            )
            nib.save(fake_mask, tmpfile_mask.name)
            nisnap.plot_segment(
                tmpfile_mask.name,
                bg=tmp_filename,
                slices=range(0, data.shape[0]),
                opacity=50,
                axes="z",
                figsize=figsize,
                samebox=True,
                # labels=[1],
                # contours=True,
                savefig=file_figure_out,
            )

            os.remove(tmp_filename)


def qc_recontructed_3DHRvolume(path_anat_vol, path_brainmask_vol, file_figure_out):
    if path_brainmask_vol is not None:
        bm_img = nib.load(path_brainmask_vol)
        brain_mask_data = bm_img.get_fdata()
        brain_mask_data = np.squeeze(brain_mask_data)

    vol = nib.load(path_anat_vol)
    vol_intensity = vol.get_fdata()
    brain_shape = vol_intensity.shape
    figsize = {'x': (10, 7)}

    with tempfile.NamedTemporaryFile(suffix=".nii.gz") as tmpfile_mask, tempfile.NamedTemporaryFile(
            suffix=".nii.gz") as tmpfile_vol:

        if path_brainmask_vol is not None:
            data = np.ones_like(brain_mask_data, dtype=np.int16)
            data[brain_mask_data.round() == 1] = 2
            fake_header = bm_img.header
            fake_header.set_data_dtype(np.int16)
            fake_mask = nib.Nifti1Image(
                data,
                affine=bm_img.affine,
                header=fake_header,
            )
        else:
            data = np.ones_like(vol_intensity, dtype=np.int16)
            fake_header = vol.header
            fake_header.set_data_dtype(np.int16)
            fake_mask = nib.Nifti1Image(
                data,
                affine=vol.affine,
                header=fake_header,
            )

        nib.save(fake_mask, tmpfile_mask.name)
        if path_brainmask_vol is not None:
            fake_int = vol_intensity + 10
        else:
            fake_int = vol_intensity * 700 + 10
            print("Multiplication by 700 bc values btwn 0 and 1 ")
        fake_vol = nib.Nifti1Image(
            fake_int,
            affine=vol.affine,
            header=vol.header,
        )
        nib.save(fake_vol, tmpfile_vol.name)

        if path_brainmask_vol is None:
            opacity = 0
        else:
            opacity = 50

        nisnap.plot_segment(
            tmpfile_mask.name,
            bg=tmpfile_vol.name,
            slices=range(0, brain_shape[2], 3),
            opacity=opacity,
            axes="x",
            figsize=figsize,
            samebox=True,
            savefig=file_figure_out,
        )