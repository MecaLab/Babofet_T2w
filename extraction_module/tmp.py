import os
import sys
import ants as ants
import pandas as pd
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg

# Fonction pour calculer et afficher la similarité
def calculate_and_plot(fixed_img, warped_path):
    warped_img = ants.image_read(warped_path)
    similarity = ants.image_similarity(fixed_img, warped_img, metric_type='MattesMutualInformation')

    fixed_img.plot(overlay=warped_img, title=f"Best registration. Distance: {similarity}", overlay_alpha=0.5)

if __name__ == "__main__":
    base_path = cfg.BASE_NIOLON_PATH
    atlas_path = os.path.join(base_path, "atlas_fetal_rhesus_v2")
    registration_exp_files = os.path.join(atlas_path, "Volumes/Test_registration_borgne07_only_affine")
    csv_path = os.path.join(registration_exp_files, "registration_results_repeated.csv")

    df = pd.read_csv(csv_path)

    df['day'] = df['gestational_day'].str.extract('(\d+)').astype(int)

    # 3. Grouper par gestational_day et trouver la ligne avec la meilleure distance (max)
    best_per_day = df.loc[df.groupby('gestational_day')['mean_distance'].idxmin()]

    # 4. Trouver l'atlas le plus jeune et le plus vieux avec la meilleure distance
    youngest_best = best_per_day.loc[best_per_day['day'].idxmin()]
    oldest_best = best_per_day.loc[best_per_day['day'].idxmax()]

    fixed_path = os.path.join(base_path, "recons_folder/Borgne/ses07/recons_rhesus/recon_template_space", "srr_template_debiased.nii.gz") # subject
    fixed_img = ants.image_read(fixed_path)

    print("Atlas le plus jeune avec la meilleure distance :")
    print(youngest_best[['gestational_day', 'mean_distance', 'warped_image_path']])
    filename = os.path.basename(youngest_best["warped_image_path"])
    calculate_and_plot(fixed_img, os.path.join(registration_exp_files, filename))

    # 8. Pour l'atlas le plus vieux
    print("\nAtlas le plus vieux avec la meilleure distance :")
    print(oldest_best[['gestational_day', 'mean_distance', 'warped_image_path']])
    filename = os.path.basename(oldest_best["warped_image_path"])
    calculate_and_plot(fixed_img, os.path.join(registration_exp_files, filename))

