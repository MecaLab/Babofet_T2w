import os
import sys
import subprocess
import numpy as np
import tempfile
from scipy.ndimage import distance_transform_cdt as cdt
from skimage.measure import marching_cubes
from skimage.measure import label as compute_cc
from skimage.filters import gaussian
import trimesh
import nibabel as nib
sys.path.insert(0, os.path.abspath(os.curdir))
import tools.tca as utca
import configuration as cfg

LUT_FILE = os.path.join(os.path.dirname(__file__), 'tools/critical186LUT.raw.gz')  # used in seg2surf()

def fix_mesh(path_mesh, path_mesh_fixed):
    """Improve quality of a triangular mesh using PyMesh fix_mesh.py script
    This function is a wrapper of the singularity execution of the pymesh
    fix_mesh.py script. This script will increase mesh quality by iteratively
        + correcting for obtuses triangles
        + Homogenise the surface of triangles (equilateral triangle)
        + Homogenise the length of edges
        + Homogenise the valence of vertices (closer to 6)
    This mesh fixing step is crucial for further processing of the mesh e.g.
    smoothing and registration

    Parameters
    ----------
    path_mesh: str
            Path of the raw triangular mesh to improve (should have .obj
            extension)
    path_mesh_fixed: str
            Path of the fixed triangular mesh (should have .obj
            extension)
    path_container: str
            Absolute path of the pymesh singularity container

    Returns
    -------
    status:
          Execution status of the mesh fixing process
    """
    print(f"Correcting {path_mesh}")
    cmd = ["fix_mesh.py",
        "--detail",
        "high",
        path_mesh,
        path_mesh_fixed,
    ]
    status = subprocess.run(cmd)

    return status

def concatenate_labels_in_mask(seg_array, concatenated_labels):
    """Generate a hemisphere white matter the segmentation mask
    by concatenating the labels provided in concatenated_labels

    Parameters
    ----------
    seg_array: numpy array
            numpy array corresponding to the data from the nifti volume
             corresponding typically to whole brain tissue segmentation
    Returns
    binary_mask: numpy array
    -------
    """
    binary_mask = np.zeros_like(seg_array, dtype=np.uint16)
    # concatenate brain tissues within WM
    for label in concatenated_labels:
        binary_mask[seg_array == label] = 1

    return binary_mask

def seg2surf(seg, sigma=0.5, alpha=16, level=0.55):
    """Extract a topologically spherical surface from a binary mask

    Parameters
    -----------
    seg: ndarray,
        binary volume to mesh
    sigma: float,
        standard deviation of gaussian blurring
    alpha: float,
        threshold for obtaining boundary of topology correction
    level: float,
        extracted surface level for Marching Cubes

    Returns
    -------
    mesh: trimesh.Trimesh,
        Raw topologically spherical triangular mesh

    Notes
    -----
    This function is a slightly modified version of the seg2surf function
    from the tca module of the CortexODE python package

    """

    # initialize topology correction
    topo_correct = utca.topology(LUT_FILE)
    # ------ connected components checking ------
    cc, nc = compute_cc(seg, connectivity=2, return_num=True)
    cc_id = 1 + np.argmax(
        np.array([np.count_nonzero(cc == i) for i in range(1, nc + 1)])
    )
    seg = (cc == cc_id).astype(np.float64)

    # ------ generate signed distance function ------
    sdf = -cdt(seg) + cdt(1 - seg)
    sdf = sdf.astype(float)
    sdf = gaussian(sdf, sigma=sigma)

    # ------ topology correction ------
    sdf_topo = topo_correct.apply(sdf, threshold=alpha)

    # ------ marching cubes ------
    v_mc, f_mc, _, _ = marching_cubes(
        -sdf_topo, level=-level, method="lewiner", allow_degenerate=False
    )
    # ------ generate mesh and perform minimal processing  -------
    # i.e. merging close vertices, degenerated faces and having consistent face
    # orientation
    mesh = trimesh.Trimesh(vertices=v_mc, faces=f_mc, process=True, validate=True)
    # ------ check the number of connex components and keep the largest -----
    if not mesh.is_watertight:
        components = mesh.split(only_watertight=False)
        if len(components) > 1:
            max_faces = -1
            largest_component = None
            for comp in components:
                n_faces = len(comp.faces)
                if n_faces > max_faces:
                    max_faces = n_faces
                    largest_component = comp
            mesh = largest_component

    return mesh

def write_gii_mesh(mesh, gifti_file):
    """Create a mesh object from two arrays

    """
    coord = mesh.vertices
    triangles = mesh.faces
    carray = nib.gifti.GiftiDataArray(
        coord.astype(
            np.float32),
        "NIFTI_INTENT_POINTSET")
    tarray = nib.gifti.GiftiDataArray(
        triangles.astype(np.float32), "NIFTI_INTENT_TRIANGLE"
    )
    img = nib.gifti.GiftiImage(darrays=[carray, tarray])
    # , meta=mesh.metadata)

    nib.save(img, gifti_file)

def mesh_extraction(
    path_seg_vol,
    labels_concat,
    path_mesh,
    refinment=1,
    nb_smoothing_iter=10,
    smoothing_step=0.1,
):
    """Generate a topologically spherical and uniform triangular mesh from a
    binary mask volume

    Parameters
    ----------
    lut_file: str
            path of the critical LUT required by the topology correction algo
    path_binary_mask: str
            Path of a binary volume defining the object to mesh
    path_mesh: str
            Path of the triangular mesh generated from the volume
    path_container: str
            Path
    nb_smoothing_iter: int
    smoothing_step: float

    Returns
    -------

    """

    if labels_concat is not None:
        concatenated_labels = [int(item) for item in labels_concat.split(',')]
    else:

        concatenated_labels=[]

    print("labels from seg_vol to concatenate : ", concatenated_labels)

    seg_vol_nifti = nib.load(path_seg_vol)
    mask = concatenate_labels_in_mask(seg_vol_nifti.get_fdata(), concatenated_labels)
    affine = seg_vol_nifti.affine
    mask = mask.astype(bool)
    print("mesh extraction")
    # topologically correct raw triangular mesh
    mesh = seg2surf(mask)
    # apply the affine transfo from the header of seg_vol
    # this is essential to preserve the real dimensions of the surface!
    mesh.apply_transform(affine)
    if refinment==0: # if refinment is disabled
        fixed_mesh = mesh
    else:# if refinment is enabled
        with tempfile.NamedTemporaryFile(suffix="_raw.obj") as temp_raw:
            with tempfile.NamedTemporaryFile(suffix="_fixed.obj") as temp_fixed:
                # export mesh into .obj format
                mesh.export(temp_raw.name)
                print("mesh sampling refinment")
                fix_mesh(temp_raw.name, temp_fixed.name)
                # topologically correct and merely uniform triangular mesh
                fixed_mesh = trimesh.load(temp_fixed.name, force="mesh")
    print("mesh smoothing")
    smoothed_mesh = trimesh.smoothing.filter_laplacian(
        fixed_mesh,
        lamb=smoothing_step,
        iterations=nb_smoothing_iter,
        implicit_time_integration=False,
        volume_constraint=False
    )

    if path_mesh.endswith(".gii"):
        print("Export output mesh as gifti")
        write_gii_mesh(smoothed_mesh, path_mesh)
    else:
        print("Using trimesh function to export")
        smoothed_mesh.export(path_mesh)



if __name__ == "__main__":
    base_path = os.path.join(cfg.BASE_NIOLON_PATH, "atlas_fetal_rhesus_v2")
    src_path = os.path.join(base_path, "Seg_Hemi")
    dst_path = os.path.join(base_path, "Surf_Hemi")

    labels_map = {
        "right": 2,  # WM right
        "left": 6,  # WM left
    }

    suffix = "_tmp"

    if not os.path.exists(dst_path):
        os.makedirs(dst_path)

    for subject in os.listdir(src_path):
        subject_src_path = os.path.join(src_path, subject)
        subject_dst_path = os.path.join(dst_path, subject)

        if not os.path.exists(subject_dst_path):
            os.makedirs(subject_dst_path)

        print(f"Processing subject: {subject}")

        for session in os.listdir(subject_src_path):
            session_file = f"{subject}_{session}_hemi{suffix}.nii.gz"
            if not os.path.exists(os.path.join(subject_src_path, session, session_file)):
                continue
            print(f"\tSession file: {session_file}")

            for label_name, label_val in labels_map.items():
                print(f"\t\tProcessing {label_name}")
                output_file = session_file.replace(f"_hemi{suffix}.nii.gz", f"{suffix}.{label_name}.white.gii")

                if os.path.exists(os.path.join(subject_dst_path, output_file)):
                    print(f"\t\t\tOutput file {output_file} already exists. Skipping.")
                    continue

                # BASE_NIOLON_PATH

                input_full_path = os.path.join(cfg.BASE_NIOLON_PATH, f"Seg_Hemi/{subject}/{session}/{session_file}")
                output_full_path = os.path.join(cfg.BASE_NIOLON_PATH, f"Surf_Hemi/{subject}/{output_file}")

                """
                input_full_path = f"/home/atlas_fetal_rhesus_v2/Seg_Hemi/{subject}/{session}/{session_file}"
                output_full_path = f"/home/atlas_fetal_rhesus_v2/Surf_Hemi/{subject}/{output_file}"

                subprocess.run([
                    "singularity", "run", "-B", f"{base_path}:/home/atlas_fetal_rhesus_v2", "surf_proc_v0.0.2a.sif",
                    "generate_mesh", "-s", input_full_path, "-l", str(label_val), "-m", output_full_path
                ], check=True)
                """

                # --- APPEL DIRECT À LA FONCTION ---
                try:
                    mesh_extraction(
                        path_seg_vol=input_full_path,
                        labels_concat=str(label_val),
                        path_mesh=output_full_path,
                        refinment=0,
                        nb_smoothing_iter=10,  # Valeur par défaut
                        smoothing_step=0.1  # Valeur par défaut
                    )
                    print(f"\t\t\tSuccessfully generated: {output_file}")
                except Exception as e:
                    print(f"\t\t\tError processing {label_name}: {e}")

                exit()


