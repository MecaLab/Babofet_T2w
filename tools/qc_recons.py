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


def qc_recons_bis(base_path, subject, mode):
    exp_param_folder = True
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

    for session in os.listdir(base_path):
        session_path = os.path.join(base_path, session)

        mode_folder = f"{mode}_brainmask"
        subj_name = f"sub-{subject}_ses-{session[3:]}"

        if exp_param_folder:
            anat_path = os.path.join(session_path, mode_folder, "exp_param", f"{subj_name}_haste_3DHR_{mode}_bm_T0_pipeline.nii.gz")
            bm_path = os.path.join(session_path, mode_folder, "exp_param", f"{subj_name}_haste_3DHR_{mode}_bm_T0_pipeline_mask.nii.gz")
        else:
            anat_path = os.path.join(session_path, mode_folder, f"{subj_name}_haste_3DHR_{mode}_bm_pipeline.nii.gz")
            bm_path = os.path.join(session_path, mode_folder, f"{subj_name}_haste_3DHR_{mode}_bm_pipeline_mask.nii.gz")

        if not os.path.exists(anat_path) or not os.path.exists(bm_path):
            print(f"Skipping {anat_path} or {bm_path} does not exist")
            continue

        filename_out = os.path.join(mid_dir_snapshots, f"{subj_name}_{mode}_T0_recons.png")
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

    for subject in subject_IDs:
        if "Fabienne" not in subject:
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


def qc_rejected_slices(subj_path, subj, mode):
    if mode == "nifty":
        bm_folder = "brainmask_niftymic"
    elif mode == "manual":
        bm_folder = "manual_masks"

    output_folder = f"{mode}_brainmask"

    json_file = os.path.join(subj_path, output_folder, "rejected_slices.json")
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    red_cmap = mcolors.ListedColormap(['red'])
    green_cmap = mcolors.ListedColormap(['green'])

    model = "niftymic"
    dir_snapshots = "snapshots"
    subject_name = subj.split("-")[1].split("_")[0]

    mid_dir_snapshots = os.path.join(dir_snapshots, "recons")

    if not os.path.exists(mid_dir_snapshots):
        os.mkdir(mid_dir_snapshots)

    mid_dir_snapshots = os.path.join(mid_dir_snapshots, model)
    if not os.path.exists(mid_dir_snapshots):
        os.mkdir(mid_dir_snapshots)

    dir_out = os.path.join(mid_dir_snapshots, subject_name)
    if not os.path.exists(dir_out):
        os.mkdir(dir_out)

    dir_out = os.path.join(dir_out, "stacks")
    if not os.path.exists(dir_out):
        os.mkdir(dir_out)

    dir_out = os.path.join(dir_out, mode)
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

            bm_data = bm.get_fdata()
            bm_data = (bm_data == 1).astype(int)

            if len(bm_data.shape) == 4:  # NiftyMIC brainmask has a 4D data: (M, M, nb_slices, 1)
                bm_data = np.squeeze(bm_data)  # (M, M, nb_slices)

            n_slices = img_data.shape[2]
            n_cols = 5
            n_rows = (n_slices + n_cols - 1) // n_cols
            fig, axes = plt.subplots(n_rows, n_cols, figsize=(22, 5*n_rows), facecolor='#121212')  # almost full black

            for i, ax in enumerate(axes.flatten()):
                if i < n_slices:
                    masked_brainmask = np.ma.masked_where(bm_data[:, :, i].T == 0, bm_data[:, :, i].T)
                    ax.imshow(img_data[:, :, i].T, cmap="gray")
                    if i in rejected_idx:
                        ax.imshow(masked_brainmask, alpha=0.5, cmap=red_cmap)
                        ax.set_title(f"Slice {i} rejected", color="white")
                    else:
                        ax.imshow(masked_brainmask, alpha=0.5, cmap=green_cmap)
                        ax.set_title(f"Slice {i} included", color="white")
                    plt.axis("off")
                else:
                    ax.axis("off")
            filename = os.path.join(dir_out, f"{stack_name}.png")
            print(f"Figure saved at {filename}")
            plt.savefig(filename)
            plt.close()


if __name__ == "__main__":

    list_subjs = ["sub-Fabienne_ses-01", "sub-Fabienne_ses-05", "sub-Fabienne_ses-09"]
    mode = "nifty"  # mode of the brainmask: manual_brainmask or nifty_brainmask

    for subj in list_subjs:
        subject_name = subj.split("_")[0].split("-")[-1]
        session_nb = "".join(subj.split("_")[1].split("-"))
        subj_path = os.path.join(cfg.DATA_PATH, subject_name, session_nb)

        qc_rejected_slices(subj_path, subj, mode)

