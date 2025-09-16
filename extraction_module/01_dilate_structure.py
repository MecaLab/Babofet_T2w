import os
import nibabel as nib
import numpy as np
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg
import subprocess


def dilate_with_fsl(input_file, output_file):
    """Dilate le masque de 2 voxels avec FSL."""
    subprocess.run([
        "fslmaths", input_file,
        "-kernel", "sphere", "2",
        "-dilD",
        output_file
    ], check=True)


if __name__ == "__main__":
    atlas_folder = os.path.join(cfg.BASE_NIOLON_PATH, "atlas_fetal_rhesus_v2")

    seg_folder = os.path.join(atlas_folder, "Segmentations")

    atlas_timepoints = [85, 97, 110, 122, 135, 147, 155]
    label_cerebellum = 7
    label_tronc = 8

    structure_dir = os.path.join(seg_folder, "structures_dilated")

    if not os.path.exists(structure_dir):
        os.makedirs(structure_dir)

    for ts in atlas_timepoints:

        sample_seg_input = os.path.join(seg_folder, f"ONPRC_G{ts}_NFseg.nii.gz")
        sample_seg_hemi = os.path.join(structure_dir, f"ONPRC_G{ts}_NFseg_hemi.nii.gz")

        sample_seg_cervelet = os.path.join(structure_dir, f"ONPRC_G{ts}_NFseg_cervelet.nii.gz")
        sample_seg_tronc = os.path.join(structure_dir, f"ONPRC_G{ts}_NFseg_tronc.nii.gz")

        img = nib.load(sample_seg_input)
        data = img.get_fdata()
        affine = img.affine
        header = img.header

        midline = data.shape[0] // 2
        coords = np.arange(data.shape[0])[:, None, None]

        mask_new = np.zeros_like(data, dtype=np.uint8)

        mask_new[(data > 0) & (mask_new == 0) & (coords < midline)] = 1

        # Hémisphère droit (hors cervelet)
        mask_new[(data > 0) & (mask_new == 0) & (coords >= midline)] = 2

        nib.save(nib.Nifti1Image(mask_new, affine), sample_seg_hemi)

        # Create binary masks for cerebellum and brainstem
        mask_cerebellum = (data == label_cerebellum).astype(np.int16)
        mask_tronc = (data == label_tronc).astype(np.int16)

        # Save temporary binary masks
        nib.save(nib.Nifti1Image(mask_cerebellum, affine, header), sample_seg_cervelet)
        nib.save(nib.Nifti1Image(mask_tronc, affine, header), sample_seg_tronc)

        # Dilate the masks using FSL
        sample_seg_cervelet_dilated = os.path.join(structure_dir, f"ONPRC_G{ts}_NFseg_cervelet_dilated.nii.gz")
        sample_seg_tronc_dilated = os.path.join(structure_dir, f"ONPRC_G{ts}_NFseg_tronc_dilated.nii.gz")

        dilate_with_fsl(sample_seg_cervelet, sample_seg_cervelet_dilated)
        dilate_with_fsl(sample_seg_tronc, sample_seg_tronc_dilated)

        print("Fin")
        break



