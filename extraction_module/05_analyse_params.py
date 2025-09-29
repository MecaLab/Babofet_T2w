import os
import sys
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

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

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

    print("\n=== Overall Best Parameters ===")
    find_best_params(df)

    make_plots(df)


