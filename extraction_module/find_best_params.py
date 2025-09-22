import numpy as np
import os
import sys
import ants as ants
import itertools
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


def ants_register(fixed, moving_atlas_file, moving_atlas_mask_file=None):
    # load atlas volume
    moving_atlas = ants.image_read(moving_atlas_file)
    # fixed.plot(overlay=moving_atlas, title='Before Registration', overlay_alpha = 0.5)
    # comute registration
    moving_atlas_mask = ants.image_read(moving_atlas_mask_file)
    mytx = ants.registration(fixed=fixed, moving=moving_atlas, mask=moving_atlas_mask,
                             type_of_transform="Affine", aff_random_sampling_rate=0.5)  # 'SyN' or Affine


    gd = os.path.basename(moving_atlas_file).split("_")[1]
    ants.image_write(mytx['warpedmovout'], os.path.join(cfg.BASE_NIOLON_PATH, f"tmp_affine_{gd}.nii.gz"))
    # fwdtransforms: Transforms to move from moving to fixed image.
    # invtransforms: Transforms to move from fixed to moving image.
    # fwdtransform = mytx['fwdtransforms']
    warped_atlas = mytx['warpedmovout']
    # compute MI to find the closest atlas
    # wraped_mi = ants.image_mutual_information(fixed, warped_atlas)
    wraped_mi = ants.image_similarity(fixed, warped_atlas, metric_type="MattesMutualInformation")  # MattesMutualInformation, MeanSquares, CC, Demons
    return wraped_mi


def calculate_similarity(fixed, moving, metric):
    if metric == "mattes":
        return ants.image_similarity(fixed, moving, metric_type="MattesMutualInformation")
    else:
        raise ValueError(f"Unknown metric: {metric}")


if __name__ == "__main__":
    param_grid = {
        "type_of_transform": ["Affine", "SyN"],
        "aff_random_sampling_rate": [0.2, 0.5, 0.8],
        "aff_shrink_factors": [(8, 6, 4, 2)],
        "aff_smoothing_sigmas": [(4, 3, 2, 1)],

    }

    keys, values = zip(*param_grid.items())
    param_combinations = [dict(zip(keys, v)) for v in itertools.product(*values)]

    fixed_image = ants.image_read(os.path.join(cfg.BASE_NIOLON_PATH, "recons_folder/Borgne/ses07/recons_rhesus/recon_template_space", "srr_template_debiased.nii.gz"))

    moving_path = os.path.join(cfg.BASE_NIOLON_PATH, "atlas_fetal_rhesus_v2/Volumes/")

    out_test_path = os.path.join(moving_path, "Test_registration")
    if not os.path.exists(out_test_path):
        os.makedirs(out_test_path)

    for file in os.listdir(moving_path):
        if "P4YR" in file:
            continue

        print(f"Processing file: {file}")
        gd = file.split("_")[1]
        moving_file = os.path.join(moving_path, file)

        results = []
        for params in param_combinations:
            print(f"Testing parameters: {params}")
            moving_image = ants.image_read(moving_file)
            mytx = ants.registration(fixed=fixed_image, moving=moving_image, **params)
            warped_image = mytx['warpedmovout']
            similarity = calculate_similarity(fixed_image, warped_image, metric="mattes")
            print(f"\tSimilarity: {similarity}")

            results.append({
                **params,
                "similarity": similarity,
                "warped_image_path": f"warped_{params['type_of_transform']}_{params['metric']}_{params['number_of_iterations'][0]}.nii.gz"
            })

            ants.image_write(warped_image, os.path.join(out_test_path, f"warped_{gd}.nii.gz"))

            exit()

        for res in sorted(results, key=lambda x: x["similarity"], reverse=True):
            print(res)