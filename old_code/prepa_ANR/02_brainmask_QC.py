import os

import matplotlib.pyplot as plt
import nibabel as nb
from skimage import morphology as smo

from tools import data_organization as tdo
from tools import illustration as til


def dilate_brainmask(bm_f, dilation_steps):
    # TODO: dilate in 2D slice by slice
    image = nb.load(bm_f)
    img = nb.funcs.squeeze_image(image)
    dilated_bm = img.get_data()
    for step in range(dilation_steps):
        dilated_bm = smo.binary_dilation(dilated_bm)

    return dilated_bm


if __name__ == "__main__":
    # chemin vers le repertoire contenant les images HASTE et TRUEFISP
    input_DB_path = '/home/patty/Documents/babofet_DB/nifti_from_Xnat'
    # chemin vers le répertoire qui contiendra les bonnes images avec un masque precis
    output_DB_path = '/home/patty/Documents/babofet_DB/processing'
    dilation_steps = 4
    show_fig = True
    # Recuperation images pour nifty
    subject_IDs = os.listdir(input_DB_path)
    subject_IDs.sort()
    subject_IDs.reverse()
    print('subjects to be processed')
    print(subject_IDs)
    subjects_failed = list()
    for subject_ID in subject_IDs[:2]: #on parcourt tous les sujets
        subj_output_dir = os.path.join(output_DB_path, subject_ID)

        print('--------------'+subject_ID)
        # check nifti data present for this subject
        dir_list = os.listdir(os.path.join(input_DB_path, subject_ID, 'scans'))
        haste_files = list()
        truefisp_files = list()
        for d in dir_list:
            d_lower = d.lower()
            if 'haste' in d_lower:
                haste_files.append(d)
            if 'truefisp' in d_lower:
                truefisp_files.append(d)

        # process HASTE images if data exist
        if len(haste_files)>0:
            print('---- haste')
            haste_subj_output_dir = os.path.join(subj_output_dir, 'haste')
            bm_haste_subj_output_dir = os.path.join(haste_subj_output_dir, 'brainmask')
            # retrieve brainmask images
            anat_img = list()
            bm_img = list()
            for f in haste_files:
                nifti_file_name, nifti_full_path = tdo.file_name_from_path(input_DB_path, subject_ID, f)
                s_nifti_file_name = nifti_file_name.split('.')
                bm_nifti_file_name = s_nifti_file_name[0]+'_brainmask.nii'
                bm_output_file = os.path.join(bm_haste_subj_output_dir, bm_nifti_file_name)
                if os.path.exists(nifti_full_path) and os.path.exists(bm_output_file):
                    bm_img.append(bm_output_file)
                    anat_img.append(nifti_full_path)
            for bm_f, anat_f in zip(bm_img, anat_img):
                dilated_bm = dilate_brainmask(bm_f, dilation_steps)
                image = nb.load(bm_f)
                fig_im = dilated_bm+image.dataobj
                im_slice = til.make_vol_slices_fig(fig_im)
                anat_f_image = nb.load(anat_f)
                anat_f_slice = til.make_vol_slices_fig(anat_f_image.dataobj)

                fig, ax = plt.subplots(1, 1)  # facecolor='black')
                ax.imshow(anat_f_slice, cmap=plt.cm.gray)
                ax.imshow(im_slice, cmap=plt.cm.jet, alpha=.5)  # , extent=(0, 1000, 10, 1000))
                ax.set_axis_off()

                #plt.savefig(output_fig, bbox_inches='tight', dpi=300)
                if show_fig:
                    plt.show()