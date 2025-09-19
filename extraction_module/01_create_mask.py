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
        output_file
    ], check=True)


def overlay_structure(base_path, structure_path, output_path, structure_label):
    """Superpose une structure avec un label donné, en écrasant si nécessaire."""
    base_img = nib.load(base_path)
    structure_img = nib.load(structure_path)
    base_data = base_img.get_fdata()
    structure_data = structure_img.get_fdata()

    # On affecte le label de la structure partout où elle est présente
    new_data = np.where(structure_data == 1, structure_label, base_data)

    nib.save(nib.Nifti1Image(new_data, base_img.affine), output_path)


if __name__ == "__main__":
    seg_folder = os.path.join(cfg.BASE_NIOLON_PATH, "atlas_fetal_rhesus")

    # seg_folder = os.path.join(atlas_folder, "Segmentations")

    atlas_timepoints = [85, 110, 135]  # [85, 97, 110, 122, 135, 147, 155]
    label_cerebellum = 7
    label_tronc = 8

    structure_dir = os.path.join(seg_folder, "structures_dilated")

    if not os.path.exists(structure_dir):
        os.makedirs(structure_dir)

    for ts in atlas_timepoints:

        print(f"Processing timepoint: {ts}")

        """sample_seg_input = os.path.join(seg_folder, f"ONPRC_G{ts}_NFseg.nii.gz")
        sample_seg_hemi = os.path.join(structure_dir, f"ONPRC_G{ts}_NFseg_hemi.nii.gz")

        sample_seg_cervelet = os.path.join(structure_dir, f"ONPRC_G{ts}_NFseg_cervelet.nii.gz")
        sample_seg_tronc = os.path.join(structure_dir, f"ONPRC_G{ts}_NFseg_tronc.nii.gz")

        sample_seg_cervelet_dilated = os.path.join(structure_dir, f"ONPRC_G{ts}_NFseg_cervelet_dilated.nii.gz")
        sample_seg_tronc_dilated = os.path.join(structure_dir, f"ONPRC_G{ts}_NFseg_tronc_dilated.nii.gz")"""

        sample_seg_input = os.path.join(seg_folder, "Template_G{ts}_T2W.nii.gz")
        sample_seg_hemi = os.path.join(structure_dir, f"Template_G{ts}_hemi.nii.gz")

        sample_seg_cervelet = os.path.join(structure_dir, f"Template_G{ts}_cervelet.nii.gz")
        sample_seg_tronc = os.path.join(structure_dir, f"Template_G{ts}_tronc.nii.gz")

        sample_seg_cervelet_dilated = os.path.join(structure_dir, f"Template_G{ts}_cervelet_dilated.nii.gz")
        sample_seg_tronc_dilated = os.path.join(structure_dir, f"Template_G{ts}_tronc_dilated.nii.gz")

        should_del_files = [
            sample_seg_hemi,
            sample_seg_cervelet, sample_seg_tronc,
            sample_seg_cervelet_dilated, sample_seg_tronc_dilated
        ]

        # Charger l'image
        img = nib.load(sample_seg_input)
        data = img.get_fdata()
        affine = img.affine
        header = img.header

        print("\tCreating hemisphere mask...")
        if not os.path.exists(sample_seg_hemi):
            # Convert world coordinates to voxel indices
            coords = np.array(np.nonzero(data > 0)).T
            xyz = nib.affines.apply_affine(affine, coords)

            # Determine mid-sagittal plane
            x_coords = xyz[:, 0]
            mid_x = 0.5 * (x_coords.min() + x_coords.max())

            # Create hemisphere mask
            mask_new = np.zeros_like(data, dtype=np.uint8)

            for (i, j, k), x in zip(coords, x_coords):
                if x < mid_x:
                    mask_new[i, j, k] = 2  # gauche
                else:
                    mask_new[i, j, k] = 1  # droite

            nib.save(nib.Nifti1Image(mask_new, affine, header), sample_seg_hemi)

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

        overlay_structure(sample_seg_hemi, sample_seg_tronc_dilated, tmp_step, structure_label=3)
        final_output = os.path.join(structure_dir, f"ONPRC_G{ts}_NFseg_structures_dilated.nii.gz")
        overlay_structure(tmp_step, sample_seg_cervelet_dilated, final_output, structure_label=4)

        should_del_files.append(tmp_step)

        print("\tCleaning up temporary files...")
        for f in should_del_files:
            if os.path.exists(f):
                os.remove(f)



