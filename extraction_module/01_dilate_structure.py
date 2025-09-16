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
        "-dilM",
        "-dilM",
        output_file
    ], check=True)


def load_and_combine(base_mask_path, to_add_path, output_path):
    """Charge deux masques et combine en priorisant le premier."""
    base = nib.load(base_mask_path)
    to_add = nib.load(to_add_path)
    # On s'assure que les valeurs du tronc/cervelet ne remplacent pas les hémisphères
    new_data = base.get_fdata() + to_add.get_fdata()
    nib.save(nib.Nifti1Image(new_data, base.affine), output_path)


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

        print(f"Processing timepoint: {ts}")

        sample_seg_input = os.path.join(seg_folder, f"ONPRC_G{ts}_NFseg.nii.gz")
        sample_seg_hemi = os.path.join(structure_dir, f"ONPRC_G{ts}_NFseg_hemi.nii.gz")

        sample_seg_cervelet = os.path.join(structure_dir, f"ONPRC_G{ts}_NFseg_cervelet.nii.gz")
        sample_seg_tronc = os.path.join(structure_dir, f"ONPRC_G{ts}_NFseg_tronc.nii.gz")

        sample_seg_cervelet_dilated = os.path.join(structure_dir, f"ONPRC_G{ts}_NFseg_cervelet_dilated.nii.gz")
        sample_seg_tronc_dilated = os.path.join(structure_dir, f"ONPRC_G{ts}_NFseg_tronc_dilated.nii.gz")

        img = nib.load(sample_seg_input)
        data = img.get_fdata()
        affine = img.affine
        header = img.header

        midline = data.shape[0] // 2
        coords = np.arange(data.shape[0])[:, None, None]

        mask_new = np.zeros_like(data, dtype=np.uint8)

        print("\tComputing hemisphere mask...")

        if not os.path.exists(sample_seg_hemi):
            mask_new[(data > 0) & (mask_new == 0) & (coords < midline)] = 1  # Left hemisphere
            mask_new[(data > 0) & (mask_new == 0) & (coords >= midline)] = 2  # Right hemisphere

            nib.save(nib.Nifti1Image(mask_new, affine), sample_seg_hemi)

        # Create binary masks for cerebellum and brainstem

        print("\tCreating binary masks for cerebellum and brainstem...")

        if not os.path.exists(sample_seg_cervelet):
            mask_cerebellum = (data == label_cerebellum).astype(np.int16)
            mask_tronc = (data == label_tronc).astype(np.int16)

            # Save temporary binary masks
            nib.save(nib.Nifti1Image(mask_cerebellum, affine, header), sample_seg_cervelet)
            nib.save(nib.Nifti1Image(mask_tronc, affine, header), sample_seg_tronc)

        # Dilate the masks using FSL
        print("\tDilating masks using FSL...")

        if not os.path.exists(sample_seg_cervelet_dilated):

            dilate_with_fsl(sample_seg_cervelet, sample_seg_cervelet_dilated)
            dilate_with_fsl(sample_seg_tronc, sample_seg_tronc_dilated)

        # Combine dilated masks into a single structure file
        print("\tCombining dilated masks into a single structure file...")
        tmp_step = os.path.join(structure_dir, f"ONPRC_G{ts}_NFseg_structures_tmp.nii.gz")

        load_and_combine(sample_seg_hemi, sample_seg_tronc_dilated, tmp_step)
        final_output = os.path.join(structure_dir, f"ONPRC_G{ts}_NFseg_structures_dilated.nii.gz")
        load_and_combine(tmp_step, sample_seg_cervelet_dilated, final_output)

        subprocess.run(["rm", tmp_step], check=True)

        print("End of processing for this timepoint.")
        break



