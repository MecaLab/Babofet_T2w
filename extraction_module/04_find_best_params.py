import numpy as np
import os
import sys
import ants as ants
import pandas as pd
import itertools
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


def calculate_similarity(fixed, moving, fixed_mask, moving_mask, metric):
    if metric == "mattes":
        return ants.image_similarity(fixed, moving, fixed_mask=fixed_mask, moving_mask=moving_mask, metric_type="MattesMutualInformation")
    else:
        raise ValueError(f"Unknown metric: {metric}")


def make_filename(gd, params):
    filename_parts = []
    for k, v in params.items():
        if isinstance(v, (list, tuple)):
            v_str = "_".join(map(str, v))  # tuple/list -> chaîne avec underscores
        else:
            v_str = str(v).replace(".", "p")  # ex: 0.2 -> "0p2"
        filename_parts.append(f"{k}-{v_str}")

    return f"warped_{gd}__" + "__".join(filename_parts) + ".nii.gz"


def run_registration_grid_search_with_repeats(fixed_path, fixed_bm_path, moving_dir, moving_bm_dir, out_dir, param_grid, n_repeats=10):
    """Exécute un grid search de recalage pour chaque atlas, avec répétitions."""
    fixed_image = ants.image_read(fixed_path)
    fixed_bm = ants.image_read(fixed_bm_path)



    os.makedirs(out_dir, exist_ok=True)

    # Générer toutes les combinaisons de paramètres
    keys, values = zip(*param_grid.items())
    param_combinations = [dict(zip(keys, v)) for v in itertools.product(*values)]

    all_results = []

    for file in os.listdir(moving_dir):
        if not file.endswith(".nii.gz"):
            continue
        if "P4YR" in file:
            continue
        gd = file.split("_")[1]
        moving_file = os.path.join(moving_dir, file)
        moving_image = ants.image_read(moving_file)
        moving_bm_file = os.path.join(moving_bm_dir, f"ONPRC_{gd}_NFseg_bm.nii.gz")
        moving_bm = ants.image_read(moving_bm_file)

        print("Fixed image spacing:", fixed_image.spacing)
        print("Fixed mask spacing:", fixed_bm.spacing)
        print("Moving image spacing:", moving_image.spacing)
        print("Moving mask spacing:", moving_bm.spacing)


        print(f"\nProcessing atlas: {file} (Gestational Day: {gd})")

        for params in param_combinations:
            distances = []
            warped_paths = []
            for i in range(n_repeats):
                print(f"\tRepeat {i+1}/{n_repeats} for params: {params}")
                mytx = ants.registration(fixed=fixed_image, mask=fixed_bm, moving=moving_image, moving_mask=moving_bm, **params)
                warped_image = mytx['warpedmovout']
                distance = calculate_similarity(fixed_image, warped_image, fixed_bm, moving_bm, metric="mattes")
                distances.append(distance)

                # Sauvegarder l'image recalée pour chaque répétition
                warped_filename = make_filename(gd, params).replace(".nii.gz", f"_rep{i + 1}.nii.gz")
                warped_path = os.path.join(out_dir, warped_filename)
                ants.image_write(warped_image, warped_path)
                warped_paths.append(warped_path)

            # Calculer les statistiques pour cette combinaison de paramètres
            mean_dist = np.mean(distances)
            std_dist = np.std(distances)
            var_dist = np.var(distances)

            all_results.append({
                "gestational_day": gd,
                **params,
                "mean_distance": mean_dist,
                "std_distance": std_dist,
                "var_distance": var_dist,
                "warped_image_path": warped_paths[0] if warped_paths else None,
            })

            print(f"\tResults for {gd}:")
            print(f"\t\tMean distance: {mean_dist:.5f}, Std: {std_dist:.5f}, Var: {var_dist:.5f}")

    # Convertir en DataFrame pour analyse
    df = pd.DataFrame(all_results)

    # Sauvegarder les résultats
    out_csv_path = os.path.join(out_dir, "registration_results_repeated.csv")
    df.to_csv(out_csv_path, index=False, mode="w", encoding="utf-8")
    print(f"\nAll results saved to {out_csv_path}")
    return df


if __name__ == "__main__":
    param_grid = {
        "type_of_transform": ["Affine"],
        "aff_random_sampling_rate": [0.2, 0.5],
        "aff_shrink_factors": [(6, 4, 2, 1), (8, 6, 4, 2)],
        "aff_smoothing_sigmas": [(3, 2, 1, 0), (4, 3, 2, 1)],

    }

    keys, values = zip(*param_grid.items())
    param_combinations = [dict(zip(keys, v)) for v in itertools.product(*values)]

    all_results = []

    fixed_image = os.path.join(cfg.BASE_NIOLON_PATH, "recons_folder/Borgne/ses07/recons_rhesus/recon_template_space", "srr_template_debiased.nii.gz")
    fixed_mask = os.path.join(cfg.BASE_NIOLON_PATH, "recons_folder/Borgne/ses07/recons_rhesus/recon_template_space", "srr_template_mask.nii.gz")


    """
    # fixed_image_bis = os.path.join(cfg.BASE_NIOLON_PATH, "atlas_fetal_rhesus_v2/Volumes/Test_registration_borgne07/warped_G85__type_of_transform-SyN__aff_random_sampling_rate-0p5__aff_shrink_factors-6_4_2_1__aff_smoothing_sigmas-4_3_2_1_rep1.nii.gz")
    distance = ants.image_similarity(ants.image_read(fixed_image), ants.image_read(fixed_image_bis), metric_type="MattesMutualInformation")
    ants.image_mutual_information(ants.image_read(fixed_image), ants.image_read(fixed_image_bis))
    print(f"Distance test: {distance}")
    exit()
    """

    main_path = os.path.join(cfg.BASE_NIOLON_PATH, "atlas_fetal_rhesus_v2")

    moving_path = os.path.join(main_path, "Volumes")
    moving_bm_path = os.path.join(main_path, "Segmentations", "structures_dilated")

    out_test_path = os.path.join(moving_path, "Test_registration")
    if not os.path.exists(out_test_path):
        os.makedirs(out_test_path)

    out_csv_path = os.path.join(out_test_path, "registration_results_repeated.csv")

    if not os.path.exists(out_csv_path):
        df = run_registration_grid_search_with_repeats(fixed_image, fixed_mask, moving_path, moving_bm_path, out_test_path, param_grid, n_repeats=10)
    else:
        df = pd.read_csv(out_csv_path)

    print("\n=== Résultats globaux (moyenne ± écart-type) ===")
    for gd in df["gestational_day"].unique():
        subset = df[df["gestational_day"] == gd]
        for transform in param_grid["type_of_transform"]:
            for sampling in param_grid["aff_random_sampling_rate"]:
                row = subset[
                    (subset["type_of_transform"] == transform) & (subset["aff_random_sampling_rate"] == sampling)]
                if not row.empty:
                    print(f"GD {gd}, {transform}, sampling={sampling}:")
                    print(
                        f"\tDistance moyenne: {row['mean_distance'].values[0]:.4f} ± {row['std_distance'].values[0]:.4f}")
                    print(f"\tVariance: {row['var_distance'].values[0]:.4f}")