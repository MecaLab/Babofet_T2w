import os
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg

main_path = os.path.join(cfg.BASE_NIOLON_PATH, "bounti", "svrtk_BOUNTI")

vol_3d_path = os.path.join(main_path, "input_SRR_niftymic", "haste")
seg_3d_path = os.path.join(main_path, "output_BOUNTI_seg", "haste")

dst_path = os.path.join(cfg.BASE_NIOLON_PATH, "francois_data")

if not os.path.exists(dst_path):
    os.makedirs(dst_path)

for subject in os.listdir(vol_3d_path):
    vol_subject_path = os.path.join(vol_3d_path, subject)
    seg_subject_path = os.path.join(seg_3d_path, subject)

    vol_dst_subject_path = os.path.join(dst_path, subject)
    if not os.path.exists(vol_dst_subject_path):
        os.makedirs(vol_dst_subject_path)

    for session in os.listdir(vol_subject_path):
        vol_file = "reo-SVR-output-brain_rhesus.nii.gz"
        seg_file = "reo-SVR-output-brain_rhesus-mask-bet-1.nii"

        vol_dst_full_path = os.path.join(vol_dst_subject_path, session)
        if not os.path.exists(vol_dst_full_path):
            os.makedirs(vol_dst_full_path)

        vol_src = os.path.join(vol_subject_path, session, vol_file)
        seg_src = os.path.join(seg_subject_path, session, seg_file)

        vol_dst = os.path.join(vol_dst_full_path, vol_file)
        seg_dst = os.path.join(vol_dst_full_path, seg_file)

        os.system("cp " + vol_src + " " + vol_dst)
        os.system("cp " + seg_src + " " + seg_dst)

        exit()