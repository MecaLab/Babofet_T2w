import os
import sys
import ants as ants
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Backend non-interactif
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
    base_path_registration = os.path.join(atlas_path, "Volumes/flirt")

    for session in os.listdir(base_path_registration):
        session_path = os.path.join(base_path_registration, session)
        if os.path.isdir(session_path):
            data = pd.read_csv(os.path.join(session_path, "metrics_results.csv"))
            plot_dir = os.path.join(session_path, "plots")
            if not os.path.exists(plot_dir):
                os.makedirs(plot_dir)

            atlases = data["Atlas"]
            mattes = data["Mattes"]
            mse = data["MSE"]
            cc = data["CC"]
            fslcc = data["FSLCC"]

            # Trouver les atlas avec les plus petites valeurs
            min_mattes_atlas = atlases[mattes.idxmin()]
            min_mattes_value = mattes.min()
            min_mse_atlas = atlases[mse.idxmin()]
            min_mse_value = mse.min()
            min_cc_atlas = atlases[cc.idxmin()]
            min_cc_value = cc.min()
            max_fslcc_atlas = atlases[fslcc.idxmax()]  # Plus grande valeur de FSLCC
            max_fslcc_value = fslcc.max()

            # Afficher les résultats dans la console
            print(f"Session: {session}")
            print(f"\tMattes min: {min_mattes_atlas} ({min_mattes_value:.3f})")
            print(f"\tMSE min: {min_mse_atlas} ({min_mse_value:.3f})")
            print(f"\tCC min: {min_cc_atlas} ({min_cc_value:.3f})")

            # Créer une figure avec 3 sous-graphiques
            fig, axes = plt.subplots(1, 4, figsize=(24, 5))

            # Mattes
            axes[0].plot(atlases, mattes, marker='o', label="Mattes")
            axes[0].set_title("Mattes Mutual Information par Atlas")
            axes[0].set_xlabel("Atlas")
            axes[0].set_ylabel("Valeur de Mattes")
            axes[0].grid(True)

            # MSE
            axes[1].plot(atlases, mse, marker='o', color='orange', label="MSE")
            axes[1].set_title("Mean Squares Error par Atlas")
            axes[1].set_xlabel("Atlas")
            axes[1].set_ylabel("Valeur de MSE")
            axes[1].grid(True)

            # CC
            axes[2].plot(atlases, cc, marker='o', color='green', label="CC")
            axes[2].set_title("Correlation Coefficient par Atlas")
            axes[2].set_xlabel("Atlas")
            axes[2].set_ylabel("Valeur de CC")
            axes[2].grid(True)

            axes[3].plot(atlases, fslcc, marker='o', color='red')
            axes[3].set_title("FSLCC par Atlas")
            axes[3].set_xlabel("Atlas")
            axes[3].set_ylabel("Valeur de FSLCC")
            axes[3].grid(True)

            plt.tight_layout()
            plt.savefig(os.path.join(plot_dir, "combined_metrics_plot.png"))
            plt.close()