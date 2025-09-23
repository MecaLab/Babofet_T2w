import numpy as np
import os
import sys
import ants as ants
import pandas as pd
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg



if __name__ == "__main__":

    csv_path = os.path.join(cfg.BASE_NIOLON_PATH, "atlas_fetal_rhesus_v2/Volumes/Test_registration", "registration_results_repeated.csv")

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

    best_min_std = df.loc[df["std_distance"].idxmin()]
    print(f"Overall Best Parameters (Min Std Dev): Gestational Day = {best_min_std['gestational_day']}, "
          f"Transform = {best_min_std['type_of_transform']}, Sampling Rate = {best_min_std['aff_random_sampling_rate']}, "
          f"Mean Distance = {best_min_std['mean_distance']:.5f}, Var Distance = {best_min_std['var_distance']:.5f}, "
          f"Std Distance = {best_min_std['std_distance']:.5f}\n")

    best_min_mean = df.loc[df["mean_distance"].idxmin()]
    print(f"Overall Best Parameters (Min Mean Distance): Gestational Day = {best_min_mean['gestational_day']}, "
          f"Transform = {best_min_mean['type_of_transform']}, Sampling Rate = {best_min_mean['aff_random_sampling_rate']}, "
          f"Mean Distance = {best_min_mean['mean_distance']:.5f}, Var Distance = {best_min_mean['var_distance']:.5f}, "
          f"Std Distance = {best_min_mean['std_distance']:.5f}\n")

    best_min_var = df.loc[df["var_distance"].idxmin()]
    print(f"Overall Best Parameters (Min Variance): Gestational Day = {best_min_var['gestational_day']}, "
          f"Transform = {best_min_var['type_of_transform']}, Sampling Rate = {best_min_var['aff_random_sampling_rate']}, "
          f"Mean Distance = {best_min_var['mean_distance']:.5f}, Var Distance = {best_min_var['var_distance']:.5f}, "
          f"Std Distance = {best_min_var['std_distance']:.5f}\n")

    