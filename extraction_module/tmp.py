import os
import sys
import ants as ants
import pandas as pd
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg

# Fonction pour calculer et afficher la similarité
def calculate_and_plot(fixed_img, warped_path):
    warped_img = ants.image_read(warped_path)
    similarity = ants.similarity(fixed_img, warped_img, metric='MattesMutualInformation')
    print(f"Similarité (Mattes Mutual Information) : {similarity}")
    fixed_img.plot(title="Image Fixed")
    warped_img.plot(title="Image Warped")

if __name__ == "__main__":
    base_path = cfg.BASE_NIOLON_PATH
    atlas_path = os.path.join(base_path, "atlas_fetal_rhesus_v2")
    registration_exp_files = os.path.join(atlas_path, "Volumes/Test_registration_borgne07_only_affine")
    csv_path = os.path.join(registration_exp_files, "registration_results_repeated.csv")

    df = pd.read_csv(csv_path)

    gds = [85, 155]
    for gd in gds:
        df_gd = df[df["gestational_day"] == gd]
        best_data = df_gd.loc[df_gd["mean_distance"].idxmax()]

        print(best_data)


