#!/bin/bash
#SBATCH -J surf_slam_pipelin
#SBATCH -p batch
#SBATCH -w niolon13
#SBATCH --mem-per-cpu=48G
#SBATCH --time=48:00:00
#SBATCH -N 1
#SBATCH -o logs/surf_slam_pipeline_%j.out
#SBATCH -e logs/surf_slam_pipeline_%j.err

set -e

# Check for arguments
if [ "$#" -ne 2 ]; then
    echo "Error: Missing arguments."
    echo "Usage: sbatch $0 <subject_id> <extraction_mode>"
    echo "Example: sbatch $0 sub-Borgne full"
    exit 1
fi

SUBJECT=$1
EXTRACTION_MODE=$2

echo "Starting Surface Extraction pipeline for subject: ${SUBJECT} with mode: ${EXTRACTION_MODE}"

module purge
module load all
module load FSL
module load ANTS
module load singularity

# Step 1: Mask Creation
echo "Step 1: Running 01_create_mask.py"
python extraction_module/01_create_mask.py
echo "Step 1 completed."
echo "------------------------------------------------------------------------------"

# Step 2: Hemisphere Splitting and Registration
echo "Step 2: Running 02_hemi_split.py for ${SUBJECT}"
python extraction_module/02_hemi_split.py --subject "${SUBJECT}"
echo "Step 2 completed."
echo "------------------------------------------------------------------------------"

# Step 3: Surface Extraction
# Note: The script automatically iterates over all subjects found in the input folder.
echo "Step 3: Running 03_extract_surf.py with mode ${EXTRACTION_MODE}"
python extraction_module/03_extract_surf.py --mode "${EXTRACTION_MODE}"
echo "Step 3 completed."
echo "------------------------------------------------------------------------------"

echo "Pipeline finished completely."