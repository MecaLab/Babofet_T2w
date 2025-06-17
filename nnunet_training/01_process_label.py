import os
import sys
import nibabel as nib
import numpy as np

sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


if __name__ == "__main__":
    subj = "Filoutte"
    base_path = os.path.join(cfg.SEG_OUTPUT_PATH_NIOLON, subj)
    for session in os.listdir(base_path):
        bounti_srr_seg_path = os.path.join(base_path, session)

        output_path = os.path.join(bounti_srr_seg_path, "reo-SVR-output-brain_rhesus-mask-brain_bounti-4.nii.gz")

        seg_img = nib.load(os.path.join(bounti_srr_seg_path, "reo-SVR-output-brain_rhesus-mask-brain_bounti-19.nii.gz"))
        seg_mask = seg_img.get_fdata()

        new_mask = np.zeros_like(seg_mask)

        csf_labels = [1, 2, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
        new_mask[np.isin(seg_mask, csf_labels)] = 1

        wm_labels = [5, 6]
        new_mask[np.isin(seg_mask, wm_labels)] = 2

        gm_labels = [3, 4]
        new_mask[np.isin(seg_mask, gm_labels)] = 3

        ventricle_labels = [7, 8, 9]
        new_mask[np.isin(seg_mask, ventricle_labels)] = 4

        new_segmentation_img = nib.Nifti1Image(new_mask, seg_img.affine, seg_img.header)
        nib.save(new_segmentation_img, output_path)
        print(f"OK for {subj} {session}")

        """
        new_mask = np.zeros_like(seg_mask)

        csf_labels = [1, 2, 18, 19]
        new_mask[np.isin(seg_mask, csf_labels)] = 1

        wm_labels = [5, 6]
        new_mask[np.isin(seg_mask, wm_labels)] = 2

        gm_labels = [3, 4]
        new_mask[np.isin(seg_mask, gm_labels)] = 3

        ventricle_labels = [7, 8, 9]
        new_mask[np.isin(seg_mask, ventricle_labels)] = 4

        thalamus_labels = [16, 17]
        new_mask[np.isin(seg_mask, thalamus_labels)] = 5

        cerebellum_labels = [10, 11, 12, 13]
        new_mask[np.isin(seg_mask, cerebellum_labels)] = 6

        basal_ganglia_labels = [14, 15]
        new_mask[np.isin(seg_mask, basal_ganglia_labels)] = 7

        # Sauvegarder le nouveau masque
        new_segmentation_img = nib.Nifti1Image(new_mask, seg_img.affine, seg_img.header)
        nib.save(new_segmentation_img, output_path)

        print(f"OK for {subj} {session}")
        """