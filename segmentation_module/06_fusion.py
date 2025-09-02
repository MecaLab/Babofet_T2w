import os
import numpy as np
import nibabel as nib
import sys
import SimpleITK as sitk
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


def compute_entropy(probabilities):
    eps = 1e-10  # Small constant to avoid log(0)
    probs = probabilities + eps
    log_probs = np.log(probs)
    entropy = -np.sum(probs * log_probs, axis=0)
    return entropy


def fusion_labels(path_1, path_2, output_path, method):
    output_path = os.path.join(output_path, method)
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    for file_1, file_2 in zip(os.listdir(path_1), os.listdir(path_2)):
        if file_1.endswith(".nii.gz") and file_2.endswith(".nii.gz"):
            print(f"Processing files: {file_1} and {file_2}")

            subject_name = file_1.split(".")[0]

            prob1 = np.load(os.path.join(path_1, file_1.replace(".nii.gz", ".npz")))["probabilities"]
            prob2 = np.load(os.path.join(path_2, file_2.replace(".nii.gz", ".npz")))["probabilities"]

            if method == "max_prob":
                label1 = np.argmax(prob1, axis=0)
                label2 = np.argmax(prob2, axis=0)

                final_labels = np.zeros_like(label1)

                same_mask = label1 == label2
                final_labels[same_mask] = label1[same_mask]

                diff_mask = ~same_mask

                coords = np.indices(label1.shape)
                d, h, w = coords[0], coords[1], coords[2]

                prob1_max = prob1[label1, d, h, w]
                prob2_max = prob2[label2, d, h, w]

                mask_model1 = (prob1_max > prob2_max) & diff_mask
                mask_model2 = (~mask_model1) & diff_mask

                final_labels[mask_model1] = label1[mask_model1]
                final_labels[mask_model2] = label2[mask_model2]
            elif method == "mean_prob":
                mean_prob = (prob1 + prob2) / 2
                final_labels = np.argmax(mean_prob, axis=0)
            elif method == "entropy":
                entropy_1 = compute_entropy(prob1)
                entropy_2 = compute_entropy(prob2)

                weights_1 = 1 / (entropy_1 + 1e-10)  # Avoid division by zero
                weights_2 = 1 / (entropy_2 + 1e-10)

                weights_sum = weights_1 + weights_2 + 1e-10  # Avoid division by zero
                weights_1 /= weights_sum
                weights_2 /= weights_sum

                combined_probs = weights_1[np.newaxis, ...] * prob1 + weights_2[np.newaxis, ...] * prob2
                final_labels = np.argmax(combined_probs, axis=0)
            else:
                raise ValueError("Fusion method not recognized")

            mask1 = nib.load(os.path.join(path_1, file_1))

            final_labels_t = np.transpose(final_labels, (2, 1, 0))  # (X, Y, Z)

            fusion_nifti = nib.Nifti1Image(final_labels_t.astype(np.uint8), affine=mask1.affine, header=mask1.header)

            nib.save(fusion_nifti, os.path.join(output_path, f"fusion_labels_{subject_name}_{method}.nii.gz"))


def apply_staple(path_1, path_2, path_3, output_path, labels):
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    for file_1, file_2, file_3 in zip(os.listdir(path_1), os.listdir(path_2), os.listdir(path_3)):
        if file_1.endswith(".nii.gz") and file_2.endswith(".nii.gz") and file_3.endswith(".nii.gz"):
            print(f"Processing files: {file_1} | {file_2} | {file_3}")

            subject_name = file_1.split(".")[0]

            seg_path = [
                os.path.join(path_1, file_1),
                os.path.join(path_2, file_2),
                os.path.join(path_3, file_3),
            ]

            segmentations = [sitk.ReadImage(path) for path in seg_path]

            staple_outputs = []

            for label in labels:
                # Créer des masques binaires 0/1 pour chaque segmentation pour la classe "label"
                binary_segmentations = [(seg == label) for seg in segmentations]

                prob_map = sitk.STAPLE(binary_segmentations)
                binary_mask = sitk.BinaryThreshold(prob_map, lowerThreshold=0.7, upperThreshold=1.0, insideValue=label,
                                                   outsideValue=0)

                staple_outputs.append(sitk.GetArrayFromImage(binary_mask))

            # Combiner les masques pour chaque classe (on prend le label max par voxel)
            combined_array = np.maximum.reduce(staple_outputs)
            combined_image = sitk.GetImageFromArray(combined_array)
            combined_image.CopyInformation(segmentations[0])

            sitk.WriteImage(combined_image, os.path.join(output_path, f"{subject_name}_staple.nii.gz"))


# TODO: refont code


if __name__ == "__main__":

    method = sys.argv[1]
    model_type = sys.argv[2]
    dataset_id_1 = sys.argv[3]
    dataset_id_2 = sys.argv[4]

    output_path = os.path.join(cfg.CODE_PATH, f"snapshots/{model_type}/fusion_labels")

    path_1 = os.path.join(cfg.CODE_PATH, f"snapshots/{model_type}/pred_dataset_{dataset_id_1}")
    path_2 = os.path.join(cfg.CODE_PATH, f"snapshots/{model_type}/pred_dataset_{dataset_id_2}")

    if method != "staple":
        fusion_labels(path_1, path_2, output_path, method)
    else:
        dataset_id_3 = sys.argv[5]
        path_3 = os.path.join(cfg.CODE_PATH, f"snapshots/{model_type}/pred_dataset_{dataset_id_3}")
        output_path = os.path.join(output_path, "staple")

        apply_staple(path_1, path_2, path_3, output_path, labels=[1, 2, 3, 4])









