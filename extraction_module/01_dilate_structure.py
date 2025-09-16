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

        import os
        import nibabel as nib
        import numpy as np


        def split_hemispheres(sample_seg_input, sample_seg_hemi):
            # Charger l'image
            img = nib.load(sample_seg_input)
            data = img.get_fdata()
            affine = img.affine
            header = img.header

            # Trouver l'axe gauche-droite (LR) avec aff2axcodes
            axcodes = nib.aff2axcodes(affine)
            print(f"Orientation de l'image: {axcodes}")

            try:
                lr_axis = axcodes.index('L') if 'L' in axcodes else axcodes.index('R')
            except ValueError:
                raise RuntimeError("Impossible d'identifier l'axe gauche-droite dans l'image.")

            # Trouver le plan médian
            midline = data.shape[lr_axis] // 2
            coords = np.arange(data.shape[lr_axis])

            # Créer masque
            mask_new = np.zeros_like(data, dtype=np.uint8)
            print("\tComputing hemisphere mask...")

            if not os.path.exists(sample_seg_hemi):
                if 'L' in axcodes[lr_axis]:
                    # Axe orienté vers la gauche
                    slicer = [None, None, None]
                    slicer[lr_axis] = coords < midline
                    mask_new[(data > 0) & np.broadcast_to(slicer[lr_axis][:, None, None], data.shape)] = 1  # Left
                    slicer[lr_axis] = coords >= midline
                    mask_new[(data > 0) & np.broadcast_to(slicer[lr_axis][:, None, None], data.shape)] = 2  # Right
                else:
                    # Axe orienté vers la droite
                    slicer = [None, None, None]
                    slicer[lr_axis] = coords < midline
                    mask_new[(data > 0) & np.broadcast_to(slicer[lr_axis][:, None, None], data.shape)] = 2  # Right
                    slicer[lr_axis] = coords >= midline
                    mask_new[(data > 0) & np.broadcast_to(slicer[lr_axis][:, None, None], data.shape)] = 1  # Left

                # Sauvegarde
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

        # subprocess.run(["rm", tmp_step], check=True)

        print("End of processing for this timepoint.")
        break



