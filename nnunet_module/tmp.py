import os
import nibabel as nib
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg

"""
This script updates a mask based on conditions from two input masks.
It replaces the label in mask1 with a new label where both masks meet specific conditions.

Might be useful for merging segmentation masks or updating labels based on certain criteria after manual correction.
"""



def update_mask_cond(mask1, mask2, label_in_mask1, label_in_mask2, new_label):
    updated_mask = mask1.copy()
    indices = (mask1 == label_in_mask1) & (mask2 == label_in_mask2)
    updated_mask[indices] = new_label
    return updated_mask

# Exemple d'utilisation
mask1 = nib.load(os.path.join(cfg.SEG_OUTPUT_PATH_NIOLON, "Fabienne/ses04", "reo-SVR-output-brain_rhesus-mask-brain_bounti-4.nii.gz"))
mask2 = nib.load(os.path.join(cfg.SEG_OUTPUT_PATH_NIOLON, "Fabienne/ses04", "tmp_reo-SVR-output-brain_rhesus-mask-brain_bounti-4.nii.gz"))

mask1_data = mask1.get_fdata()
mask2_data = mask2.get_fdata()

label_in_mask1 = 1
label_in_mask2 = 4
new_label = 4  # le label à appliquer dans mask1

updated_mask_data = update_mask_cond(mask1_data, mask2_data, label_in_mask1, label_in_mask2, new_label)

updated_mask_img = nib.Nifti1Image(updated_mask_data, mask1.affine, mask1.header)

# Sauvegarder le masque mis à jour dans un nouveau fichier
nib.save(updated_mask_img, os.path.join(cfg.SEG_OUTPUT_PATH_NIOLON, "Fabienne/ses04", "merged_reo-SVR-output-brain_rhesus-mask-brain_bounti-4.nii.gz"))