import os
import sys
import ants as ants
import pandas as pd
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg

# Fonction pour calculer et afficher la similarité
def calculate_and_plot(fixed_img, warped_path):
    warped_img = ants.image_read(warped_path)
    similarity = ants.similarity(fixed_img, warped_img, metric='MattesMutualInformation')[0]
    print(f"Similarité (Mattes Mutual Information) : {similarity}")
    fixed_img.plot(title="Image Fixed")
    warped_img.plot(title="Image Warped")

if __name__ == "__main__":
    base_path = cfg.BASE_NIOLON_PATH
    atlas_path = os.path.join(base_path, "atlas_fetal_rhesus_v2")
    registration_exp_files = os.path.join(atlas_path, "Volumes/Test_registration_borgne07_only_affine")
    csv_path = os.path.join(registration_exp_files, "registration_results_repeated.csv")

    df = pd.read_csv(csv_path)

    # Grouper par gestational_day et trouver la ligne avec la meilleure distance (max)
    best_per_day = df.loc[df.groupby('gestational_day')['mean_distance'].idxmax()]

    # Trouver l'atlas le plus jeune et le plus vieux avec la meilleure distance
    youngest_best = best_per_day.loc[best_per_day['gestational_day'].str.extract('(\\d+)').astype(int).idxmin()]
    oldest_best = best_per_day.loc[best_per_day['gestational_day'].str.extract('(\\d+)').astype(int).idxmax()]

    print(youngest_best["warped_image_path"][0])
    exit()


    # Charger l'image fixed (remplace par ton chemin)
    fixed_path = os.path.join(base_path, "recons_folder/Borgne/ses07/recons_rhesus/recon_template_space",
                              "srr_template_debiased.nii.gz")  # subject
    fixed_img = ants.image_read(fixed_path)

    # Pour l'atlas le plus jeune
    print("Atlas le plus jeune avec la meilleure distance :")
    print(youngest_best[['gestational_day', 'mean_distance', 'warped_image_path']])
    calculate_and_plot(fixed_img, youngest_best['warped_image_path'])

    # Pour l'atlas le plus vieux
    print("\nAtlas le plus vieux avec la meilleure distance :")
    print(oldest_best[['gestational_day', 'mean_distance', 'warped_image_path']])
    calculate_and_plot(fixed_img, oldest_best['warped_image_path'])