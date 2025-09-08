import os
import nibabel as nib
import numpy as np
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


if __name__ == "__main__":

    atlas_folder = os.path.join(cfg.BASE_NIOLON_PATH, "atlas_fetal_rhesus_v2")

    seg_folder = os.path.join(atlas_folder, "Segmentations")

    sample_seg = os.path.join(seg_folder, "ONPRC_G110_NFseg.nii.gz")

    atlas_nii = nib.load(sample_seg)
    atlas = atlas_nii.get_fdata()
    affine = atlas_nii.affine

    labels_cerebellum = [7]

    midline = atlas.shape[0] // 2
    coords = np.arange(atlas.shape[0])[:, None, None]

    mask_new = np.zeros_like(atlas, dtype=np.uint8)

    # Cervelet
    mask_new[np.isin(atlas, labels_cerebellum)] = 3

    # Hémisphère gauche (hors cervelet)
    mask_new[(atlas > 0) & (mask_new == 0) & (coords < midline)] = 1

    # Hémisphère droit (hors cervelet)
    mask_new[(atlas > 0) & (mask_new == 0) & (coords >= midline)] = 2

    out_nii = nib.Nifti1Image(mask_new, affine)
    nib.save(seg_folder, "tmp.nii.gz")


