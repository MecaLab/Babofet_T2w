# -*- coding: utf-8 -*-
"""Global constants and data organisation

"""
import os
# REPOSITORY DATA ORGANISATION
# -----------------------------------------------------------------------------/

# LOCAL PATH
MAIN_PATH = "W:/meca/data/Fetus/datasets/Babofet"
OUTPUT_PATH = os.path.join(MAIN_PATH, "processing")

# NIOLON PATH
BASE_NIOLON_PATH = "/envau/work/meca/data/babofet_DB/2024_new_stuff"
RECONS_FOLDER = os.path.join(BASE_NIOLON_PATH, "recons_folder")
BOUNTI_NIOLON_PATH = os.path.join(BASE_NIOLON_PATH, "bounti")
SEG_INPUT_PATH_NIOLON = os.path.join(BOUNTI_NIOLON_PATH, "svrtk_BOUNTI", "input_SRR_niftymic", "haste")
SEG_OUTPUT_PATH_NIOLON = os.path.join(BOUNTI_NIOLON_PATH, "svrtk_BOUNTI", "output_BOUNTI_seg", "haste")


# MESOCENTRE PATH
BASE_PATH = "/scratch/lbaptiste/"
MESO_DATA_PATH = os.path.join(BASE_PATH, "data/dataset/babofet/subjects")
MESO_OUTPUT_PATH = os.path.join(BASE_PATH, "data/dataset/babofet/derivatives")
# DATA PATH
DATA_PATH = os.path.join(BASE_PATH, "data/recons_folder")
BOUNTI_PATH = os.path.join(BASE_PATH, "data/bounti")
ATLAS_GHOLIPOUR_PATH = os.path.join(BASE_PATH, "data/STA_atlas_hemi_split")
NNUNET_RAW_PATH = os.path.join(BASE_PATH, "data/nnUNet_raw")
# Segmentation path bounti
SEG_INPUT_PATH = os.path.join(BOUNTI_PATH, "svrtk_BOUNTI", "input_SRR_niftymic", "haste")
SEG_OUTPUT_PATH = os.path.join(BOUNTI_PATH, "svrtk_BOUNTI", "output_BOUNTI_seg", "haste")

TABLE_CSV_DATA_INFO = os.path.join("table_data", "info_table.csv")

DICOM_META_TO_EXTRACT = [
    "PatientID",
    "PatientName",
    "PatientBirthDate",
    "PatientAge",
    "PatientSex",
    "PatientSize",
    "PatientWeight",
    "StudyInstanceUID",
    "StudyDescription",
    "StudyDate",
    "StudyTime",
    "SeriesInstanceUID",
    "SeriesDescription",
    "SeriesNumber",
    "InstanceNumber",
    "Manufacturer",
    "ManufacturerModelName",
    "SoftwareVersions",
    "MagneticFieldStrength",
]


"""
# paths for MESOCENTRE
# DATA_PATH = "/scratch/gauzias/data/datasets"
# CODE_PATH = "/scratch/gauzias/code_gui/dHCP_fetal"
# paths for ENVAU
DATA_PATH = "/envau/work/meca/data/Fetus/datasets"
CODE_PATH = "/hpc/meca/softs/dev/auzias/pyhon/fet-processing"



# --------------- INPUT DATA FILES---------------------------------------------#
MarsFet_DATA_PATH = os.path.join(DATA_PATH, "MarsFet")
MarsFet_RAWDATA_PATH = os.path.join(MarsFet_DATA_PATH, "rawdata")
MarsFet_DERIVATIE_PATH = os.path.join(MarsFet_DATA_PATH, "derivatives")
MarsFet_PHENOTYPE_TABLE = os.path.join(CODE_PATH, "data", "tables", "marsfet_latest_participants.csv")

# ----------------- OUTPUT DATA FILES------------------------------------------#
MarsFet_HASTE_SUB_SESS_PICKL = os.path.join(CODE_PATH, "MarsFet_HASTE_sub_sess.pkl")
MarsFet_HASTE_NORMATIVE_SUB_SESS_PICKL = os.path.join(CODE_PATH, "MarsFet_HASTE_normative_study_sub_sess.pkl")
MarsFet_TRUFISP_SUB_SESS_PICKL = os.path.join(CODE_PATH, "MarsFet_TRUFISP_sub_sess.pkl")
MarsFet_SEQ_COMPARISON_SUB_SESS_PICKL = os.path.join(CODE_PATH, "MarsFet_COMP_sub_sess.pkl")
MarsFet_OUPUT_PATH = os.path.join(MarsFet_DATA_PATH, "output")
MarsFet_SRR_NESVOR_PATH = os.path.join(MarsFet_DERIVATIE_PATH, "srr_reconstruction", "latest_nesvor")
MarsFet_OUPUT_NNUNET_SEGMENTATION_PATH = os.path.join(MarsFet_DERIVATIE_PATH, "segmentation", "latest_seg")
MarsFet_HASTE_OUPUT_NNUNET_SEGMENTATION_TABLE = os.path.join(CODE_PATH, "data", "tables", "marsFet_HASTE_lastest_volumes_nnUNet.csv")
MarsFet_HASTE_OUPUT_NNUNET_SEGMENTATION_SNAPSHOTS = os.path.join(MarsFet_OUPUT_PATH, "snapshots_nnUNet", "haste")

MarsFet_TRUFISP_OUPUT_NNUNET_SEGMENTATION_TABLE = os.path.join(CODE_PATH, "data", "tables", "marsFet_TRUFISP_lastest_volumes_nnUNet.csv")
MarsFet_TRUFISP_OUPUT_NNUNET_SEGMENTATION_SNAPSHOTS = os.path.join(MarsFet_OUPUT_PATH, "snapshots_nnUNet", "trufisp")

MarsFet_HASTE_OUPUT_BOUNTI_INPUT_PATH = os.path.join(MarsFet_OUPUT_PATH, "svrtk_BOUNTI", "input_SRR_nesvor", "haste")
MarsFet_HASTE_OUPUT_BOUNTI_OUTPUT_PATH = os.path.join(MarsFet_OUPUT_PATH, "svrtk_BOUNTI", "output_BOUNTI_seg", "haste")
MarsFet_HASTE_OUPUT_BOUNTI_SEGMENTATION_TABLE = os.path.join(CODE_PATH, "data", "tables", "marsFet_HASTE_lastest_volumes_BOUNTI.csv")
MarsFet_HASTE_OUPUT_BOUNTI_SEGMENTATION_SNAPSHOTS = os.path.join(MarsFet_OUPUT_PATH, "svrtk_BOUNTI", "segmentation_snapshots", "haste")

MarsFet_TRUFISP_OUPUT_BOUNTI_INPUT_PATH = os.path.join(MarsFet_OUPUT_PATH, "svrtk_BOUNTI", "input_SRR_nesvor", "trufisp")
MarsFet_TRUFISP_OUPUT_BOUNTI_OUTPUT_PATH = os.path.join(MarsFet_OUPUT_PATH, "svrtk_BOUNTI", "output_BOUNTI_seg", "trufisp")
MarsFet_TRUFISP_OUPUT_BOUNTI_SEGMENTATION_TABLE = os.path.join(CODE_PATH, "data", "tables", "marsFet_TRUFISP_lastest_volumes_BOUNTI.csv")
MarsFet_TRUFISP_OUPUT_BOUNTI_SEGMENTATION_SNAPSHOTS = os.path.join(MarsFet_OUPUT_PATH, "svrtk_BOUNTI", "segmentation_snapshots", "trufisp")


# ----------------------------- NOMENCLATURE ------------------------------------------#
# WHOLE BRAIN DRAWEM9 NOMENCLATURE
DHCP_NOMENCLATURE = {
    0: "volume_background",
    1: "volume_CSF",
    2: "volume_cGM",
    3: "volume_WM",
    4: "volume_background-brain",
    5: "volume_VENTRICLES",
    6: "volume_CEREBELLUM",
    7: "volume_dGM",
    8: "volume_BRAINSTEM",
    9: "volume_HIPPOCAMPI",
}
# WHOLE BRAIN BOUNTI NOMENCLATURE
BOUNTI_NOMENCLATURE = {
    1: "eCSF_L",
    2: "eCSF_R",
    3: "Cortical_GM_L",
    4: "Cortical_GM_R",
    5: "Fetal_WM_L",
    6: "Fetal_WM_R",
    7: "Lateral_Ventricle_L",
    8: "Lateral_Ventricle_R",
    9: "Cavum_septum_pellucidum",
    10: "Brainstem",
    11: "Cerebellum_L",
    12: "Cerebellum_R",
    13: "Cerebellar_Vermis",
    14: "Basal_Ganglia_L",
    15: "Basal_Ganglia_R",
    16: "Thalamus_L",
    17: "Thalamus_R" ,
    18: "Third_Ventricle",
    19: "Fourth Ventricle",
    20: "Corpus_Callosum"
}
"""