import os
import sys
import json
import nibabel as nib
sys.path.insert(0, os.path.abspath(os.curdir))
from tools import qc
import numpy as np
import configuration as cfg
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import fnmatch
import re
from scipy import stats


def qc_plot_table_recons(datas, subj_name, name):
    num_slices = 7
    dir_snapshots = "snapshots"

    output_dir = os.path.join(dir_snapshots, "recons", "niftymic", subj_name)
    print("Images are written in {}".format(output_dir))

    slice_percentages = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]

    for session, modes in datas.items():
        num_cols = len(modes)

        fig, axes = plt.subplots(num_slices, num_cols, figsize=(15, 3*num_slices))
        fig.suptitle(f'Fabienne {session} | {name}', fontsize=16)

        reference_slices = []

        for col, (mode, paths) in enumerate(modes.items()):
            fig.text((col + 0.5) / num_cols, 0.95, mode, ha='center', va='center', fontsize=14)
            anat_path = paths["anat"]

            anat_img = nib.load(anat_path).get_fdata()
            depth = anat_img.shape[2]

            reference_slices.append((depth // 2, depth))

            for row in range(num_slices):
                slice_idx = int(depth * slice_percentages[row])
                axes[row, col].imshow(anat_img[:, :, slice_idx], cmap="gray")
                axes[row, col].set_title(f'Coupe {slice_idx}')
                axes[row, col].axis('off')

        plt.tight_layout()
        output_file = os.path.join(output_dir, f"fabienne_{session}_{name}_table_recons.png")
        plt.savefig(output_file)
        plt.close()
        print(f"Fin de la session {session}")


def qc_recons_bis(subj_path, subject, mode, exp_param_folder=False, param=None, name="default-param"):
    dir_snapshots = "snapshots"

    mid_dir_snapshots = os.path.join(dir_snapshots, "recons", "niftymic")

    if not os.path.exists(mid_dir_snapshots):
        os.mkdir(mid_dir_snapshots)

    mid_dir_snapshots = os.path.join(mid_dir_snapshots, subject)
    if not os.path.exists(mid_dir_snapshots):
        os.mkdir(mid_dir_snapshots)

    mid_dir_snapshots = os.path.join(mid_dir_snapshots, mode)
    if not os.path.exists(mid_dir_snapshots):
        os.mkdir(mid_dir_snapshots)

    session = subj_path.split("/")[-1]

    mode_folder = f"{mode}_brainmask"
    subj_name = f"sub-{subject}_ses-{session[3:]}"

    if exp_param_folder:
        anat_path = os.path.join(subj_path, mode_folder, "exp_param", f"{subj_name}_haste_3DHR_{mode}_bm_{param}_pipeline.nii.gz")
        bm_path = os.path.join(subj_path, mode_folder, "exp_param", f"{subj_name}_haste_3DHR_{mode}_bm_{param}_pipeline_mask.nii.gz")
    else:
        anat_path = os.path.join(subj_path, mode_folder, f"{subj_name}_haste_3DHR_{mode}_bm_pipeline.nii.gz")
        bm_path = os.path.join(subj_path, mode_folder, f"{subj_name}_haste_3DHR_{mode}_bm_pipeline_mask.nii.gz")

    if not os.path.exists(anat_path) or not os.path.exists(bm_path):
        print(f"Skipping {anat_path} or {bm_path} does not exist")
    else:
        filename_out = os.path.join(mid_dir_snapshots, f"{subj_name}_{mode}_{name}_recons.png")
        qc.qc_recontructed_3DHRvolume(
            path_anat_vol=anat_path,
            path_brainmask_vol=bm_path,
            file_figure_out=filename_out
        )
        print(f"Figure saved at {filename_out}")


def qc_recons(base_path, model, mode):
    """
    Function that use the anatomic and the brainmask data to snapshot them
    The model string is used to split between niftymic and nesvor

    :param base_path: str, path to the list of the subjects
    :param model: str, nesvor or niftymic
    :return: None
    """
    dir_snapshots = "snapshots"

    mid_dir_snapshots = os.path.join(dir_snapshots, "recons")

    if not os.path.exists(mid_dir_snapshots):
        os.mkdir(mid_dir_snapshots)

    mid_dir_snapshots = os.path.join(mid_dir_snapshots, model)
    if not os.path.exists(mid_dir_snapshots):
        os.mkdir(mid_dir_snapshots)

    subject_IDs = os.listdir(base_path)

    list_subjs = ["sub-Fabienne_ses-01", "sub-Fabienne_ses-09"]

    for subject in subject_IDs:
        if subject not in list_subjs:
            continue
        if model == "niftymic":
            # from sub-SUBJECT_ses-XX to SUBJECT
            subject_dir = subject.split("_")[0].split("-")[-1]

            print(f"Snapshot for {subject}")
            path_recons = os.path.join(cfg.MESO_OUTPUT_PATH, subject, "haste", "reconstruction_niftymic")

            dir_out = os.path.join(mid_dir_snapshots, subject_dir)
            if not os.path.exists(dir_out):
                os.mkdir(dir_out)

            dir_out = os.path.join(dir_out, mode)
            if not os.path.exists(dir_out):
                os.mkdir(dir_out)

            anat_filename = subject + f"_haste_3DHR_{mode}_bm_pipeline.nii.gz"
            bm_filename = subject + f"_haste_3DHR_{mode}_bm_pipeline_mask.nii.gz"

            anat_path = os.path.join(path_recons, anat_filename)
            bm_path = os.path.join(path_recons, bm_filename)

            file_figure_out = os.path.join(dir_out, subject + f"_{mode}_recons.png")

            if not os.path.exists(anat_path):
                print(f"Skipping {anat_path} because missing")
                continue

            if not os.path.exists(bm_path):
                qc.qc_recontructed_3DHRvolume(
                    path_anat_vol=anat_path,
                    path_brainmask_vol=None,
                    file_figure_out=file_figure_out
                )
            else:
                qc.qc_recontructed_3DHRvolume(
                    path_anat_vol=anat_path,
                    path_brainmask_vol=bm_path,
                    file_figure_out=file_figure_out
                )
        elif model == "nesvor":
            # from sub-SUBJECT_ses-XX to SUBJECT
            subject_dir = subject.split("_")[0].split("-")[-1]

            path_recons = os.path.join(cfg.MESO_OUTPUT_PATH, subject, "haste", "reconstruction_nesvor")

            dir_out = os.path.join(mid_dir_snapshots, subject_dir)
            if not os.path.exists(dir_out):
                os.mkdir(dir_out)

            anat_filename = subject + "_haste_3DHR.nii.gz"

            anat_path = os.path.join(path_recons, anat_filename)

            file_figure_out = os.path.join(dir_out, subject + "_recons.png")

            if not os.path.exists(anat_path):
                print(f"Skipping {anat_path} because missing")
                continue

            print(f"Snapshot for {subject}")

            qc.qc_recontructed_3DHRvolume(
                path_anat_vol=anat_path,
                path_brainmask_vol=None,
                file_figure_out=file_figure_out
            )


def qc_rejected_slices(subj_path, subj_name, subj, mode, exp_param_folder=False, param=None, name="default-param"):
    if not exp_param_folder and param is None:
        param = ""

    if mode == "nifty":
        bm_folder = "brainmask_niftymic"
    elif mode == "manual":
        bm_folder = "manual_masks"
    elif mode == "mattia":
        bm_folder = "mattia_masks"

    output_folder = f"{mode}_brainmask"

    if exp_param_folder:
        json_file = os.path.join(subj_path, output_folder, f"exp_param/rejected_slices_{param}.json")
    else:
        json_file = os.path.join(subj_path, output_folder, f"rejected_slices.json")

    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    red_cmap = mcolors.ListedColormap(['red'])
    green_cmap = mcolors.ListedColormap(['green'])

    model = "niftymic"
    dir_snapshots = "snapshots"

    mid_dir_snapshots = os.path.join(dir_snapshots, "recons")

    # /snapshots/recons/
    if not os.path.exists(mid_dir_snapshots):
        os.mkdir(mid_dir_snapshots)

    # /snapshots/recons/niftymic
    mid_dir_snapshots = os.path.join(mid_dir_snapshots, model)
    if not os.path.exists(mid_dir_snapshots):
        os.mkdir(mid_dir_snapshots)

    # /snapshots/recons/niftymic/Fabienne
    mid_dir_snapshots = os.path.join(mid_dir_snapshots, subj_name)
    if not os.path.exists(mid_dir_snapshots):
        os.mkdir(mid_dir_snapshots)

    # /snapshots/recons/niftymic/Fabienne/manual
    dir_out = os.path.join(mid_dir_snapshots, mode)
    if not os.path.exists(dir_out):
        os.mkdir(dir_out)

    # /snapshots/recons/niftymic/Fabienne/manual/stacks
    dir_out = os.path.join(dir_out, "stacks")
    if not os.path.exists(dir_out):
        os.mkdir(dir_out)

    for stack_name, rejected_idx in data.items():
        if rejected_idx:
            stack_path = os.path.join(cfg.MESO_OUTPUT_PATH, subj, "denoising", stack_name + ".nii")
            img = nib.load(stack_path)
            img_data = img.get_fdata()

            if mode == "nifty":
                bm_path = os.path.join(cfg.MESO_OUTPUT_PATH, subj, bm_folder, stack_name + "_seg.nii.gz")
                bm = nib.load(bm_path)
            elif mode == "manual":
                try:
                    bm_path = os.path.join(cfg.MESO_OUTPUT_PATH, subj, bm_folder, stack_name + "_mask.nii.gz")
                    bm = nib.load(bm_path)
                except FileNotFoundError:
                    bm_path = os.path.join(cfg.MESO_OUTPUT_PATH, subj, bm_folder, stack_name + "_mask.nii")
                    bm = nib.load(bm_path)
                finally:
                    print(f"File not found: {bm_path}")
                    continue
            elif mode == "mattia":
                bm_path = os.path.join(cfg.MESO_OUTPUT_PATH, subj, bm_folder, stack_name + "_mask.nii.gz")
                bm = nib.load(bm_path)

            bm_data = bm.get_fdata()
            bm_data = (bm_data > 0).astype(int)

            if len(bm_data.shape) == 4:  # NiftyMIC brainmask has a 4D data: (M, M, nb_slices, 1)
                bm_data = np.squeeze(bm_data)  # (M, M, nb_slices)

            n_slices = img_data.shape[2]
            n_cols = 5
            n_rows = (n_slices + n_cols - 1) // n_cols
            fig, axes = plt.subplots(n_rows, n_cols, figsize=(22, 5*n_rows), facecolor='#121212')  # almost full black

            for i, ax in enumerate(axes.flatten()):
                if i < n_slices:
                    masked_brainmask = np.ma.masked_where(bm_data[:, :, i].T == 0, bm_data[:, :, i].T)
                    ax.imshow(img_data[:, :, i].T, cmap="gray", origin="lower")
                    if i in rejected_idx:
                        ax.imshow(masked_brainmask, alpha=0.5, cmap=red_cmap, origin="lower")
                        ax.set_title(f"Slice {i} rejected", color="white")
                    else:
                        ax.imshow(masked_brainmask, alpha=0.5, cmap=green_cmap, origin="lower")
                        ax.set_title(f"Slice {i} included", color="white")
                    plt.axis("off")
                else:
                    ax.axis("off")
            filename = os.path.join(dir_out, f"{stack_name}_{mode}_{name}.png")
            print(f"Figure saved at {filename}")
            plt.savefig(filename)
            plt.close()


def qc_plot_table_stack(base_path, list_subjs, modes):
    num_slices = 5
    num_cols = len(modes)
    red_cmap = mcolors.ListedColormap(['red'])

    for subj in list_subjs:
        subj_path = os.path.join(base_path, subj)

        anat_path = os.path.join(subj_path, "denoising")

        for stack_file in os.listdir(anat_path):
            if "HASTE" not in stack_file:
                continue

            stack_name = "_".join(stack_file.split("_")[:-1])
            fig, axes = plt.subplots(num_slices, num_cols, figsize=(18, 5 * num_slices))
            fig.suptitle(f'{subj}')
            anat_img = nib.load(os.path.join(anat_path, stack_file)).get_fdata()

            for col, mode in enumerate(modes):
                if mode == "manual":
                    bm_folder = os.path.join(subj_path, "manual_masks")
                    bm_extension = "_mask.nii.gz"
                elif mode == "nifty":
                    bm_folder = os.path.join(subj_path, "brainmask_niftymic")
                    bm_extension = "_seg.nii.gz"

                try:
                    bm_filename = stack_file.replace(".nii", bm_extension)
                    brainmask = nib.load(os.path.join(bm_folder, bm_filename))
                except FileNotFoundError:
                    bm_filename = stack_file.replace(".nii", "_mask.nii")
                    brainmask = nib.load(os.path.join(bm_folder, bm_filename))

                bm_data = brainmask.get_fdata()
                bm_data = (bm_data == 1).astype(int)

                if len(bm_data.shape) == 4:  # NiftyMIC brainmask has a 4D data: (M, M, nb_slices, 1)
                    bm_data = np.squeeze(bm_data)  # (M, M, nb_slices)

                for row in range(num_slices):
                    slice_idx = anat_img.shape[2] * row // num_slices
                    masked_brainmask = np.ma.masked_where(bm_data[:, :, slice_idx].T == 0, bm_data[:, :, slice_idx].T)

                    axes[row, col].imshow(anat_img[:, :, slice_idx], cmap="gray")
                    axes[row, col].imshow(masked_brainmask, alpha=0.5, cmap=red_cmap)
                    axes[row, col].set_title(f'{mode.upper()}')
                    axes[row, col].axis('off')

            plt.tight_layout()
            plt.savefig(f"{stack_name}.png")
            plt.close()
            print(f"Fin de la session {subj}")
            exit()


def get_file_with_pattern(path, pattern):
    files = []
    for file in os.listdir(path):
        if fnmatch.fnmatch(file, pattern):
            files.append(file)
    return files


def extract_param_name(file):
    pattern = r"bm_(.*?)_pipeline"  # extract the param name between 'bm' and '_pipeline'
    match = re.search(pattern, file)
    if match:
        return match.group(1)
    else:
        return None


def qc_intensity(subj_path, subject, mode, subj_session):
    base_path = os.path.join(subj_path, f"{mode}_brainmask")
    volumes = [nib.load(os.path.join(base_path, f"{subj_session}_haste_3DHR_{mode}_bm_pipeline.nii.gz")).get_fdata()]
    param_name = ["default"]
    exp_param_folder = os.path.join(base_path, "exp_param")
    if os.path.exists(exp_param_folder):
        files = os.listdir(os.path.join(base_path, "exp_param"))
        for file in files:
            if file.endswith("pipeline.nii.gz"):
                param_name.append(extract_param_name(file))
                volumes.append(nib.load(os.path.join(base_path, "exp_param", file)).get_fdata())

    origin_output_path = "snapshots"

    fig, axs = plt.subplots(1, 4, figsize=(24, 10), facecolor='white')
    idxs = [50, 60, 70, 80]
    for i, idx in enumerate(idxs):
        ax = axs[i]
        for j, vol in enumerate(volumes):
            # vol shape is (x, y, z).
            # x is COR, y is SAG, z is AX
            # get the intensity on the AX slice (x-y view) at indice idx along z-view
            intensity = vol[:, vol.shape[1]//2, idx]  # sagital view
            # intensity = vol[vol.shape[0]//2, :, idx]  # coronal view
            # intensity = vol[vol.shape[0]//2, idx, :]  # axial view
            ax.plot(intensity, label=f"{param_name[j]}")

        ax.set_ylabel("Intensity")
        ax.set_title(f"Intensity at slide {idx}")
        ax.grid(True)
        ax.legend()

    plt.suptitle(f"Analysis of the intensity profile for {subj_session}")
    plt.tight_layout()
    plt.savefig(os.path.join(origin_output_path, f"recons/niftymic/{subject}/{mode}", f"intensity_{subj_session}.png"))
    plt.close()


def qc_plot_table_params(subj_path, mode, subject, subj_session):
    output_filename = os.path.join(f"snapshots/recons/niftymic/{subject}/{mode}", f"comparator_{subj_session}.png")
    if os.path.exists(output_filename):
        return None

    nib_path = os.path.join(subj_path, f"{mode}_brainmask")
    vol_ref = nib.load(os.path.join(nib_path, f"{subj_session}_haste_3DHR_{mode}_bm_pipeline.nii.gz")).get_fdata()

    vols = {
        "default": vol_ref
    }
    indices = [20, 30, 40, 50, 60, 70, 80]

    if not os.path.exists(os.path.join(nib_path, "exp_param")):
        return None
    for file in os.listdir(os.path.join(nib_path, "exp_param")):
        if file.endswith("pipeline.nii.gz"):
            vol = nib.load(os.path.join(nib_path, "exp_param", file)).get_fdata()
            param = file.split("bm_")[-1].split("_pipeline")[0]
            vols[param] = vol

    fig, axes = plt.subplots(len(indices), len(vols), figsize=(3*len(vols), 2*len(indices)), facecolor='white')
    for i, idx in enumerate(indices):
        for j, (param, vol) in enumerate(vols.items()):
            ax = axes[i, j]
            axes[0, j].set_title(f"{param}", fontsize=12, fontweight='bold')
            slice_data = vol[:, :, idx]
            ax.imshow(slice_data, cmap="jet")
            ax.axis("off")

    # Ajustement de la mise en page
    plt.suptitle(subj_session)
    for i, idx in enumerate(indices):
        fig.text(0.02, 1 - (i + 0.5) / len(indices), f"Slice {idx}", va='center', ha='left', fontsize=12,
                 fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_filename)
    plt.close()


def freedman_diaconis_bins(data):
    """Calcule le nombre optimal de bins selon la règle de Freedman-Diaconis."""
    q75, q25 = np.percentile(data, [75, 25])
    iqr = q75 - q25
    n = len(data)
    bin_width = 2 * iqr / (n ** (1/3))
    return int((data.max() - data.min()) / bin_width)


def normalize_min_max(volume):
    return (volume - volume.min()) / (volume.max() - volume.min())


def plot_histo(subj_path, mode, subject, subj_session):
    nib_path = os.path.join(subj_path, f"{mode}_brainmask")
    vol_ref = nib.load(os.path.join(nib_path, f"{subj_session}_haste_3DHR_{mode}_bm_pipeline.nii.gz")).get_fdata()
    mask_ref = nib.load(os.path.join(nib_path, f"{subj_session}_haste_3DHR_{mode}_bm_pipeline_mask.nii.gz")).get_fdata()

    vol_ref_masked = vol_ref[mask_ref > 0]

    if not os.path.exists(os.path.join(nib_path, "exp_param")):
        vol1 = normalize_min_max(vol_ref_masked)
        hist_range = (vol1.min(), vol1.max())
        bins = freedman_diaconis_bins(np.concatenate([vol1]))

        hist1, bins1 = np.histogram(vol1, bins=bins, density=True, range=hist_range)
        bin_centers = (bins1[:-1] + bins1[1:]) / 2  # Centres des bins

        title = f"{subj_session} default ({mode})"
        output_filename = "_".join(title.split()).lower()
        output_filename_path = os.path.join(f"snapshots/recons/niftymic/{subject}/{mode}",
                                            f"histo_{output_filename}.png")

        plt.figure(figsize=(10, 6), facecolor='white')
        plt.plot(bin_centers, hist1, label='Default param', linestyle='-', alpha=0.7)
        plt.xlabel("Intensité")
        plt.ylabel("Densité")
        plt.legend()
        plt.grid()
        plt.tight_layout()
        plt.savefig(output_filename_path)
        plt.close()
    else:
        for file in os.listdir(os.path.join(nib_path, "exp_param")):
            if file.endswith("pipeline.nii.gz"):
                vol_dst = nib.load(os.path.join(nib_path, "exp_param", file)).get_fdata()
                mask_dst = nib.load(os.path.join(nib_path, "exp_param", file.replace(".nii.gz", "_mask.nii.gz"))).get_fdata()

                param = file.split("bm_")[-1].split("_pipeline")[0]

                title = f"{subj_session} default vs {param} ({mode})"
                output_filename = "_".join(title.split()).lower()
                output_filename_path = os.path.join(f"snapshots/recons/niftymic/{subject}/{mode}",
                                                    f"histo_{output_filename}.png")
                if os.path.exists(output_filename_path):
                    continue

                vol_dst_masked = vol_dst[mask_dst > 0]

                vol1 = normalize_min_max(vol_ref_masked)
                vol2 = normalize_min_max(vol_dst_masked)

                hist_range = (min(vol1.min(), vol2.min()), max(vol1.max(), vol2.max()))
                bins = freedman_diaconis_bins(np.concatenate([vol1, vol2]))

                hist1, bins1 = np.histogram(vol1, bins=bins, density=True, range=hist_range)
                hist2, bins2 = np.histogram(vol2, bins=bins, density=True, range=hist_range)

                bin_centers = (bins1[:-1] + bins1[1:]) / 2  # Centres des bins
                wasserstein_dist = stats.wasserstein_distance(bin_centers, bin_centers, hist1 * np.diff(bins1), hist2 * np.diff(bins2))
                # print(f"Wasserstein distance: {wasserstein_dist}")

                plt.figure(figsize=(10, 6), facecolor='white')
                plt.plot(bin_centers, hist1, label='Default param', linestyle='-', alpha=0.7)
                plt.plot(bin_centers, hist2, label=f"{param} param", linestyle='--', alpha=0.7)
                plt.title(f"{title}\nWasserstein Distance: {wasserstein_dist:.4f}\nBins: {bins}")
                plt.xlabel("Intensité")
                plt.ylabel("Densité")
                plt.legend()
                plt.grid()
                plt.tight_layout()
                plt.savefig(output_filename_path)
                plt.close()


if __name__ == "__main__":
    pass






