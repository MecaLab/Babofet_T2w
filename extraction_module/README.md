# Fetal Brain Surface Extraction Pipeline

This module provides a comprehensive pipeline for extracting cortical surfaces from fetal brain MRI segmentations. It processes atlas data, registers it to individual subjects, splits the brain into hemispheres, and finally generates surface meshes (`.surf.gii` files) for both the left and right white matter.

## Overview

The pipeline is organized into three sequential scripts, each performing a critical step in the surface extraction process:

1.  **Mask Creation**: `01_create_mask.py`
2.  **Hemisphere Splitting**: `02_hemi_split.py`
3.  **Surface Extraction**: `03_extract_surf.py`

---

## Pipeline Scripts

### 1. Create Masks (`01_create_mask.py`)

This initial script prepares a set of necessary masks from a fetal rhesus macaque atlas. These masks are essential for the subsequent registration and hemisphere splitting steps.

-   **Functionality**:
    -   For each timepoint in the atlas, it generates several masks:
        -   **Brain Mask**: A binary mask of the entire brain.
        -   **Hemisphere Mask**: A mask where each hemisphere (left/right) is assigned a unique label (1 or 2). This is determined by finding the mid-sagittal plane.
        -   **Cerebellum & Brainstem Masks**: Binary masks for the cerebellum and brainstem structures.
    -   It then **dilates** the cerebellum and brainstem masks using `fslmaths` to create a safety margin.
    -   Finally, it combines the hemisphere, dilated cerebellum, and dilated brainstem masks into a single "structures" file (`..._structures_dilated.nii.gz`). In this file:
        -   Right Hemisphere = 1
        -   Left Hemisphere = 2
        -   Brainstem = 3
        -   Cerebellum = 4
-   **Output**: A set of prepared atlas masks for each timepoint, stored in `derivatives/intermediate/surf-slam/structures_dilated/`.

### 2. Split Hemispheres (`02_hemi_split.py`)

This is the core script of the pipeline. It takes the segmentation of an individual subject and accurately splits it into left and right hemispheres, also identifying the cerebellum and brainstem.

-   **Functionality**:
    1.  **Find Best Atlas**: It first determines the best-matching atlas timepoint for the subject's T2w image by performing an initial affine registration (`flirt`) and comparing the cross-correlation (`fslcc`).
    2.  **Multi-Step Registration**: It then performs a robust registration of the chosen atlas "structures" mask (created in Step 1) to the subject's brain. This involves:
        -   Converting the FSL `.mat` transform to an ANTs-compatible `.txt` transform using `c3d_affine_tool`.
        -   Running a non-linear SyN registration with `antsRegistration` for high precision, guided by the brain masks of both the subject and the atlas.
    3.  **Apply Transformations**: The final transformation is applied to the atlas "structures" mask to warp it perfectly into the subject's space.
    4.  **Combine and Split**: The warped structures mask is combined with the subject's own tissue segmentation (from the `longiseg` module). This allows for the final assignment of labels:
        -   Right/Left CSF (1, 5)
        -   Right/Left White Matter (2, 6)
        -   Right/Left Gray Matter (3, 7)
        -   Brainstem (9)
        -   Cerebellum (10)
-   **Output**: A final, hemisphere-split segmentation for each subject session, saved as `..._hemi.nii.gz` in `derivatives/intermediate/surf-slam/Seg_Hemi/`.

### 3. Extract Surfaces (`03_extract_surf.py`)

This final script takes the hemisphere-split segmentations and generates the 3D surface meshes.

-   **Functionality**:
    -   It iterates through the output of the previous step.
    -   For each hemisphere (left and right), it extracts the white matter surface (labels 2 and 6).
    -   It offers two modes of operation via a command-line argument:
        -   `viz`: A quick extraction using `generate_mesh.py` for visualization purposes. It performs minimal smoothing.
        -   `full`: A full, high-quality extraction using a Singularity container (`surf_proc_v0.0.2a.sif`), intended for final results.
-   **Usage**:
    ```bash
    python 03_extract_surf.py <mode>
    ```
    -   `<mode>`: Either `viz` or `full`.
-   **Output**: Cortical surface files in GIfTI format (`.surf.gii`) for each hemisphere, saved in `derivatives/surf-slam/`.
