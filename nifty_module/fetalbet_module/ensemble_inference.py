import sys
import os
import subprocess
import numpy as np
import nibabel as nib
import shutil
import uuid
import argparse
from scipy.ndimage import label, binary_closing, generate_binary_structure
from skimage.measure import regionprops
from pathlib import Path
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


# Paths to models
model_paths = [
    'weights/AttUNet_finetuned_fold_0_best.pth',
    'weights/AttUNet_finetuned_fold_1_best.pth',
    'weights/AttUNet_finetuned_fold_2_best.pth',
    'weights/AttUNet_finetuned_fold_3_best.pth',
    'weights/AttUNet_finetuned_fold_4_best.pth',
]

def run_majority_voting_pipeline(image_path, output_folder):
    image_path = Path(image_path)
    image_filename = image_path.name
    temp_dir = Path(f"tmp_{uuid.uuid4().hex}")
    temp_dir.mkdir(parents=True)

    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    inference_script_path = os.path.join(current_script_dir, "inference.py")

    print("Running inference with each model...")
    for model in model_paths:
        fold_name = model.split("/")[-2]
        pred_dir = temp_dir / f"pred_{fold_name}"
        pred_dir.mkdir(parents=True, exist_ok=True)

        subprocess.run([
            'python', inference_script_path,
            '--saved_model_path', os.path.join(cfg.SOFTS_PATH, model),
            '--input_path', str(image_path),
            '--output_path', str(pred_dir)
        ])

    print("Combining predictions with majority voting...")
    preds = []
    for model in model_paths:
        fold_name = model.split("/")[-2]
        pred_path = temp_dir / f"pred_{fold_name}" / image_filename.replace('.nii.gz', '_predicted_mask.nii.gz')
        pred_img = nib.load(pred_path)
        preds.append(pred_img.get_fdata())

    preds = np.stack(preds, axis=0)
    majority_vote = (np.sum(preds, axis=0) >= (len(model_paths) // 2 + 1)).astype(np.uint8)

    structure = generate_binary_structure(3, 2)
    closed = binary_closing(majority_vote, structure=structure).astype(np.uint8)

    labeled_array, num_features = label(closed)
    if num_features > 0:
        regions = regionprops(labeled_array)
        largest_region = max(regions, key=lambda r: r.area)
        largest_component = (labeled_array == largest_region.label).astype(np.uint8)
    else:
        largest_component = closed

    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)
    output_path = output_folder / image_filename.replace('.nii.gz', '_mask.nii.gz')

    final_img = nib.Nifti1Image(largest_component, affine=pred_img.affine, header=pred_img.header)
    nib.save(final_img, output_path)

    print(f"Final mask saved to: {output_path}")

    shutil.rmtree(temp_dir)
    print("Temporary files cleaned up.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run ensemble segmentation on a single image using multiple models.")
    parser.add_argument("--image_path", type=str, required=True, help="Path to the input NIfTI image.")
    parser.add_argument("--output_folder", type=str, required=True, help="Directory to save the final segmentation mask.")

    args = parser.parse_args()
    run_majority_voting_pipeline(args.image_path, args.output_folder)
