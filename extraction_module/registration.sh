module load all
module load FSL ANTS  

MOVING='/envau/work/meca/data/babofet_DB/2024_new_stuff/recons_folder/Borgne/ses07/recons_rhesus/recon_template_space/srr_template_debiased.nii.gz'
MOVING_MASK='/envau/work/meca/data/babofet_DB/2024_new_stuff/recons_folder/Borgne/ses07/recons_rhesus/recon_template_space/srr_template_mask.nii.gz'

REFERENCE='/envau/work/meca/data/babofet_DB/2024_new_stuff/atlas_fetal_rhesus_v2/Volumes/ONPRC_G122_Norm.nii.gz'
REFERENCE_MASK='/envau/work/meca/data/babofet_DB/2024_new_stuff/atlas_fetal_rhesus_v2/Segmentations/structures_dilated/ONPRC_G122_NFseg_bm.nii.gz'

OUTPUT_DIR='/envau/work/meca/data/babofet_DB/2024_new_stuff/atlas_fetal_rhesus_v2/Volumes/flirt'
mkdir -p "$OUTPUT_DIR"


# affine first
echo "Running FLIRT..."
flirt \
	-in "$MOVING" \
	-ref "$REFERENCE" \
	-out "$OUTPUT_DIR/affine.nii.gz" \
	-omat "$OUTPUT_DIR/affine.mat" \
	-dof 12 \
	-cost mutualinfo \
	-searchrx -180 180 \
	-searchry -180 180 \
	-searchrz -180 180 \
	-interp spline

# convert fsl affine to ants format
c3d_affine_tool \
    -ref ${REFERENCE} \
    -src ${MOVING} \
    "$OUTPUT_DIR/affine.mat" \
    -fsl2ras \
    -oitk "$OUTPUT_DIR/affine.txt"

# non linear with ants
ANTS_PREFIX="${OUTPUT_DIR}/ants_"
ANTS_WARPED_IMAGE="warped_IMAGE.nii.gz"

antsRegistration \
    --verbose 1 \
    --dimensionality 3 \
    --float 0 \
    --output [${ANTS_PREFIX},${ANTS_PREFIX}${ANTS_WARPED_IMAGE}] \
    --interpolation BSpline \
    --use-histogram-matching 1 \
    --winsorize-image-intensities [0.001,0.999] \
    --initial-moving-transform "$OUTPUT_DIR/affine.txt" \
    --transform SyN[0.1,3,0] \
    --metric Mattes[${REFERENCE},${MOVING},1,32] \
    --convergence [200x200x200x200x200x200,1e-6,10] \
    --shrink-factors 4x4x2x2x1x1 \
    --smoothing-sigmas 6x5x4x2x1x0 \
    --masks [${REFERENCE_MASK},${MOVING_MASK}] \


# propagate the segmentations
antsApplyTransforms \
    --dimensionality 3 \
    --input "$SMOOTHED_PARCELLATIONS" \
    --reference-image "$REFERENCE" \
    --output "$OUTPUT_DIR/warped_regionals.nii.gz" \
    --transform "$OUTPUT_DIR/ants_1Warp.nii.gz" \
    --transform "$OUTPUT_DIR/affine.txt" \
    --interpolation GenericLabel
