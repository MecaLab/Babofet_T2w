import os
import sys
import nibabel as nib
import numpy as np

sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


if __name__ == "__main__":
    subj = sys.argv[1]

    base_path = os.path.join(cfg.SEG_OUTPUT_PATH_NIOLON, subj)
    for session in os.listdir(base_path):
        print(f"Processing session: {session}")
        bounti_srr_seg_path = os.path.join(base_path, session)

        output_path = os.path.join(bounti_srr_seg_path, "reo-SVR-output-brain_rhesus-mask-brain_bounti-4.nii.gz")

        if os.path.exists(output_path):
            print(f"\tFile already exists for session {session}, skipping...")
            continue

        seg_img = nib.load(os.path.join(bounti_srr_seg_path, "reo-SVR-output-brain_rhesus-mask-brain_bounti-19.nii.gz"))
        seg_mask = seg_img.get_fdata()

        new_mask = np.zeros_like(seg_mask)

        csf_labels = [1, 2]
        new_mask[np.isin(seg_mask, csf_labels)] = 1

        wm_labels = [5, 6, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
        new_mask[np.isin(seg_mask, wm_labels)] = 2

        gm_labels = [3, 4]
        new_mask[np.isin(seg_mask, gm_labels)] = 3

        ventricle_labels = [7, 8, 9]
        new_mask[np.isin(seg_mask, ventricle_labels)] = 4

        new_segmentation_img = nib.Nifti1Image(new_mask, seg_img.affine, seg_img.header)
        nib.save(new_segmentation_img, output_path)
        print("\tDone")