from tools import qc


if __name__ == "__main__":
    dir_snapshots = "/envau/work/meca/data/Fetus/datasets/dhcp_neonatal/output/svrtk_BOUNTI/segmentation_snapshots"
    file_type = "_desc-restore_T2w.nii.gz"


    file_figure_out = os.path.join(dir_snapshots, subject + "_" + session + "_bounti_seg.png")

    qc.qc_brainmask(path_anat_vol, path_brainmask_vol, file_figure_out)