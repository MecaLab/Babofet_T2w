# -*- coding: utf-8 -*-
"""Global constants and data organisation

"""
import os
# REPOSITORY DATA ORGANISATION
# -----------------------------------------------------------------------------/


# BIDS Path
BASE_BIDS_PATH = "/envau/work/meca/data/BaboFet_BIDS/"
SOURCEDATA_BIDS_PATH = os.path.join(BASE_BIDS_PATH, "sourcedata")
DERIVATIVES_BIDS_PATH = os.path.join(BASE_BIDS_PATH, "derivatives")


######### NIOLON PATH
BASE_NIOLON_PATH = "/envau/work/meca/data/babofet_DB/2024_new_stuff"

# OTHERS PATH
SOFTS_PATH = os.path.join(BASE_NIOLON_PATH, "softs")
RECONS_FOLDER = os.path.join(BASE_NIOLON_PATH, "recons_folder")
FETAL_RESUS_ATLAS = os.path.join(BASE_NIOLON_PATH, "atlas_fetal_rhesus")
NNUNET_PYTHON_PATH = "~/.conda/envs/nnunet/lib/python3.9/site-packages/nnunetv2/training/nnUNetTrainer/"

## BOUNTI PATH
BOUNTI_NIOLON_PATH = os.path.join(BASE_NIOLON_PATH, "bounti", "svrtk_BOUNTI")
SEG_INPUT_PATH_NIOLON = os.path.join(BOUNTI_NIOLON_PATH, "input_SRR_niftymic", "haste")
SEG_OUTPUT_PATH_NIOLON = os.path.join(BOUNTI_NIOLON_PATH, "output_BOUNTI_seg", "haste")

## NNUNET PATH
NNUNET_RAW_PATH = os.path.join(BASE_NIOLON_PATH, "nnUNet_raw")
NNUNET_RESULTS_PATH = os.path.join(BASE_NIOLON_PATH, "nnUNet_trained_models")
NNUNET_PREPROCESSED_PATH = os.path.join(BASE_NIOLON_PATH, "nnUNet_preprocessed")

## LONGISEG PATH
LONGISEG_RAW_PATH = os.path.join(BASE_NIOLON_PATH, "LongiSeg_raw")
LONGISEG_RESULTS_PATH = os.path.join(BASE_NIOLON_PATH, "LongiSeg_results")
LONGISEG_PREPROCESSED_PATH = os.path.join(BASE_NIOLON_PATH, "LongiSeg_preprocessed")

########################################################################################################################

######### MESOCENTRE PATH
BASE_PATH = "/scratch/lbaptiste/data"
CODE_PATH = "/scratch/lbaptiste/Babofet_T2w/"
MESO_DATA_PATH = os.path.join(BASE_PATH, "dataset/babofet/subjects")
MESO_OUTPUT_PATH = os.path.join(BASE_PATH, "dataset/babofet/derivatives")
# DATA PATH
DATA_PATH = os.path.join(BASE_PATH, "recons_folder")
LONGISEG_PYTHON_PATH = os.path.join(CODE_PATH, "LongiSeg")
TABLE_DATA_PATH = os.path.join(CODE_PATH, "table_data")

# nnUNet path
NNUNET_RAW_PATH_MESO = os.path.join(BASE_PATH, "nnUNet_raw")
NNUNET_RESULTS_PATH_MESO = os.path.join(BASE_PATH, "nnUNet_trained_models")
NNUNET_PREPROCESSED_PATH_MESO = os.path.join(BASE_PATH, "nnUNet_preprocessed")

# LongiSeg path
LONGISEG_RAW_PATH_MESO = os.path.join(BASE_PATH, "LongiSeg_raw")
LONGISEG_RESULTS_PATH_MESO = os.path.join(BASE_PATH, "LongiSeg_results")
LONGISEG_PREPROCESSED_PATH_MESO = os.path.join(BASE_PATH, "LongiSeg_preprocessed")

# Segmentation path bounti
BOUNTI_PATH = os.path.join(BASE_PATH, "bounti", "svrtk_BOUNTI")
SEG_INPUT_PATH = os.path.join(BOUNTI_PATH, "input_SRR_niftymic", "haste")
SEG_OUTPUT_PATH = os.path.join(BOUNTI_PATH, "output_BOUNTI_seg", "haste")

TABLE_CSV_DATA_INFO = os.path.join("table_data", "info_table.csv")