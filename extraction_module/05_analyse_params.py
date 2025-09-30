import os
import sys
import re
import ants as ants
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg


def find_best_params(df, colums=None):
    if colums is None:
        colums = ["mean_distance", "std_distance", "var_distance"]
    for col in colums:
        best_data = df.loc[df[col].idxmin()]
        print(f"Best Parameters for {col}: Gestational Day = {best_data['gestational_day']}, "
              f"Transform = {best_data['type_of_transform']}, Sampling Rate = {best_data['aff_random_sampling_rate']}, "
              f"aff_smoothing_sigmas = {best_data['aff_smoothing_sigmas']}, aff_shrink_factors = {best_data['aff_shrink_factors']}, "
              f"Mean Distance = {best_data['mean_distance']:.5f}, Var Distance = {best_data['var_distance']:.5f}, "
                f"Std Distance = {best_data['std_distance']:.5f}")

def make_plots(df):
    df["aff_smoothing_sigmas_str"] = df["aff_smoothing_sigmas"].apply(lambda x: str(x))
    df["aff_shrink_factors_str"] = df["aff_shrink_factors"].apply(lambda x: str(x))

    fig, axes = plt.subplots(1, 3, figsize=(22, 12))

    # Plot mean_distance
    sns.boxplot(data=df, x='aff_random_sampling_rate', y='mean_distance', hue='gestational_day', ax=axes[0])
    axes[0].set_title('Mean Distance by Sampling Rate and Gestational Day')
    axes[0].set_ylabel('Mean Distance')

    # Plot std_distance
    sns.boxplot(data=df, x='aff_random_sampling_rate', y='std_distance', hue='gestational_day', ax=axes[1])
    axes[1].set_title('Std Distance by Sampling Rate and Gestational Day')
    axes[1].set_ylabel('Std Distance')

    # Plot var_distance
    sns.boxplot(data=df, x='aff_random_sampling_rate', y='var_distance', hue='gestational_day', ax=axes[2])
    axes[2].set_title('Var Distance by Sampling Rate and Gestational Day')
    axes[2].set_ylabel('Var Distance')

    plt.tight_layout()

    plt.savefig("registration_results_boxplots.png")

def get_best_exp(df):
    index_max = df["mean_distance"].idxmin()
    ligne_max = df.loc[index_max]

    print(ligne_max)
    return ligne_max

def transform_filename(original):
    # (Ton code de transformation ici)
    s = original.replace('warped_', '')
    s = re.sub(r'__type_of_transform-', '_', s)
    s = re.sub(r'__aff_random_sampling_rate-0p2', '_02', s)
    s = re.sub(r'__aff_shrink_factors-([\d_]+)', lambda m: '_' + m.group(1).replace('_', '-'), s)
    s = re.sub(r'__aff_smoothing_sigmas-([\d_]+)', lambda m: '_' + m.group(1).replace('_', '-'), s)
    s = re.sub(r'_aff_shrink_factors', '', s)
    s = re.sub(r'_aff_smoothing_sigmas', '', s)
    s = re.sub(r'_aff_random_sampling_rate', '', s)
    s = re.sub(r'_rep\d+\.nii(\.gz)?$', '', s)
    return s

def plot_registration(fixed_image, moving_path, atlas_volumes_path):
    output_dir = os.path.join(atlas_volumes_path, "registration_plots")
    os.makedirs(output_dir, exist_ok=True)
    for file in os.listdir(moving_path):
        if file.endswith(".nii.gz"):
            if "rep10" in file:
                name = transform_filename(file)
                output_path = os.path.join(output_dir, f"{name}.png")
                moving_image = ants.image_read(os.path.join(moving_path, file))
                fixed_image.plot(overlay=moving_image, title=name, overlay_alpha=0.5, filename=output_path, axis=2)

def compute_best_registration(best_row, fixed_path, moving_path, output_path):
    # Charger les images
    fixed_image = ants.image_read(fixed_path)
    moving_image = ants.image_read(moving_path)

    # Extraire et convertir les paramètres
    aff_shrink_factors = eval(best_row['aff_shrink_factors'])
    aff_smoothing_sigmas = eval(best_row['aff_smoothing_sigmas'])

    # Lancer le recalage
    registration = ants.registration(
        fixed=fixed_image,
        moving=moving_image,
        type_of_transform=best_row['type_of_transform'],
        random_sampling_rate=best_row['aff_random_sampling_rate'],
        shrink_factors=aff_shrink_factors,
        smoothing_sigmas=aff_smoothing_sigmas,
    )

    # Sauvegarder l'image recalée
    warped_image = registration['warpedmovout']
    ants.image_write(warped_image, output_path)
    print(f"Recalage terminé. Image sauvegardée à {output_path}")



if __name__ == "__main__":

    base_path = cfg.BASE_NIOLON_PATH
    atlas_path = os.path.join(base_path, "atlas_fetal_rhesus_v2")
    atlas_volumes_path = os.path.join(atlas_path, "Volumes")
    registration_exp_files = os.path.join(atlas_volumes_path, "Test_registration_borgne07_only_affine")
    csv_path = os.path.join(registration_exp_files, "registration_results_repeated.csv")

    if not os.path.exists(csv_path):
        print(f"CSV file not found at {csv_path}")
        exit(1)

    df = pd.read_csv(csv_path)

    gds = df["gestational_day"].unique()
    for gd in gds:
        df_gd = df[df["gestational_day"] == gd]
        mean_of_means = df_gd["mean_distance"].mean()
        std_of_means = df_gd["mean_distance"].std()
        print(f"Gestational Day {gd}: Mean of Means = {mean_of_means:.5f}, Std of Means = {std_of_means:.5f}")

        best_row = df_gd.loc[df_gd["mean_distance"].idxmin()]
        print(f"\tBest Parameters: Transform = {best_row['type_of_transform']}, "
              f"Sampling Rate = {best_row['aff_random_sampling_rate']}, Mean Distance = {best_row['mean_distance']:.5f}, "
              f"Var Distance = {best_row['var_distance']:.5f}, Std Distance = {best_row['std_distance']:.5f}\n")

    print("\n=== Overall Best Parameters ===")
    find_best_params(df)

    # make_plots(df)

    best_row = get_best_exp(df)

    ga = best_row['gestational_day']

    print(f"\n=== Computing Best Registration for Gestational Day {ga} ===")

    fixed_path = os.path.join(base_path, "recons_folder/Borgne/ses07/recons_rhesus/recon_template_space", "srr_template_debiased.nii.gz") # subject
    moving_path = os.path.join(atlas_path, "Volumes", f"ONPRC_{ga}_Norm.nii.gz")  # template
    moving_bm_path = os.path.join(atlas_path, "Segmentations", "structures_dilated", f"ONPRC_{ga}_NFseg_bm.nii.gz")
    output_path = os.path.join(atlas_path, "Volumes", f"ONPRC_{ga}_Norm_best_registered.nii.gz")

    compute_best_registration(best_row, fixed_path, moving_path, output_path)

    fixed_image = ants.image_read(fixed_path)
    best_moving_image = ants.image_read(output_path)

    distance = ants.image_similarity(fixed_image, best_moving_image, metric_type="MattesMutualInformation")

    aff_shrink_factors = eval(best_row['aff_shrink_factors'])
    aff_smoothing_sigmas = eval(best_row['aff_smoothing_sigmas'])
    type_of_transform = best_row['type_of_transform'],
    random_sampling_rate = best_row['aff_random_sampling_rate']

    print(f"Best registration parameters: Transform = {type_of_transform}, Sampling Rate = {random_sampling_rate}, "
          f"aff_shrink_factors = {aff_shrink_factors}, aff_smoothing_sigmas = {aff_smoothing_sigmas}")

    fixed_image.plot(overlay=best_moving_image, title=f"Best registration. Distance: {distance}", overlay_alpha=0.5, axis=2)

    plot_registration(ants.image_read(fixed_path), registration_exp_files, registration_exp_files)