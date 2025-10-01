import os
import sys
import ants as ants
import pandas as pd
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg

# Fonction pour calculer et afficher la similarité
def calculate_and_plot(fixed_img, warped_path):
    warped_img = ants.image_read(warped_path)
    similarity = ants.image_similarity(fixed_img, warped_img, metric_type='Correlation')

    fixed_img.plot(overlay=warped_img, title=f"Best registration. Distance: {similarity}", overlay_alpha=0.5)


def tmp_func(atlas_path):
    registration_exp_files = os.path.join(atlas_path, "Volumes/Test_registration_borgne07_only_affine")
    csv_path = os.path.join(registration_exp_files, "registration_results_repeated.csv")

    df = pd.read_csv(csv_path)

    df['day'] = df['gestational_day'].str.extract('(\d+)').astype(int)

    # 3. Grouper par gestational_day et trouver la ligne avec la meilleure distance (max)
    best_per_day = df.loc[df.groupby('gestational_day')['mean_distance'].idxmax()]

    # 4. Trouver l'atlas le plus jeune et le plus vieux avec la meilleure distance
    youngest_best = best_per_day.loc[best_per_day['day'].idxmin()]
    oldest_best = best_per_day.loc[best_per_day['day'].idxmax()]

    fixed_path = os.path.join(base_path, "recons_folder/Borgne/ses07/recons_rhesus/recon_template_space",
                              "srr_template_debiased.nii.gz")  # subject
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


def compute_registration(fixed_path, fixed_bm_path, moving_path, moving_bm_path, output_path, params):
    fixed_img = ants.image_read(fixed_path)
    fixed_bm = ants.image_read(fixed_bm_path)

    moving_img = ants.image_read(moving_path)
    moving_bm = ants.image_read(moving_bm_path)

    mytx = ants.registration(fixed=fixed_img, mask=fixed_bm, moving=moving_img, moving_mask=moving_bm, **params)


if __name__ == "__main__":
    base_path = cfg.BASE_NIOLON_PATH
    atlas_path = os.path.join(base_path, "atlas_fetal_rhesus_v2")

    # Lire les données
    data = pd.read_csv(os.path.join(atlas_path, "Volumes/flirt/metrics_results.csv"))

    plot_dir = os.path.join(atlas_path, "Volumes/flirt/plots")

    if not os.path.exists(plot_dir):
        os.makedirs(plot_dir)

    # Extraire les atlas (ex: G85, G122)
    atlases = data["Atlas"]
    mattes = data["Mattes"]
    mse = data["MSE"]
    cc = data["CC"]

    # Créer les courbes
    os.makedirs("$PLOT_DIR", exist_ok=True)

    # Courbe Mattes
    plt.figure()
    plt.plot(atlases, mattes, marker='o', label="Mattes")
    plt.title("Mattes Mutual Information par Atlas")
    plt.xlabel("Atlas")
    plt.ylabel("Valeur de Mattes")
    plt.grid(True)
    plt.savefig(os.path.join(plot_dir, "mattes_plot.png"))
    plt.close()

    # Courbe MSE
    plt.figure()
    plt.plot(atlases, mse, marker='o', color='orange', label="MSE")
    plt.title("Mean Squares Error par Atlas")
    plt.xlabel("Atlas")
    plt.ylabel("Valeur de MSE")
    plt.grid(True)
    plt.savefig(os.path.join(plot_dir, "mse_plot.png"))
    plt.close()

    # Courbe CC
    plt.figure()
    plt.plot(atlases, cc, marker='o', color='green', label="CC")
    plt.title("Correlation Coefficient par Atlas")
    plt.xlabel("Atlas")
    plt.ylabel("Valeur de CC")
    plt.grid(True)
    plt.savefig(os.path.join(plot_dir, "cc_plot.png"))
    plt.close()

    # tmp_func(atlas_path)
