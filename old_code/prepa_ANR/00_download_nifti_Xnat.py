import xnat
import datetime

# import shutil
import os

####### connect session
session = xnat.connect('http://xnat.int.univ-amu.fr:8080', user='coulon.o')

if __name__ == "__main__":
    nifti_data_path = '/home/patty/Documents/babofet_DB/nifti_from_Xnat'
    ###### project
    project_name = "LoFeBa"
    proj_data = session.projects[project_name]

    print(proj_data.description)

    ####### access data
    for key_sub, val_sub in proj_data.subjects.items():
        subject = val_sub.label
        print('---------------------'+subject)
        for key_exp, val_exp in val_sub.experiments.items():
            if os.path.exists(os.path.join(nifti_data_path, val_exp.label)):
                print('--session data already downloaded, skip')
            else:
                for key_scan, val_scan in val_exp.scans.items():
                    # https://xnat.readthedocs.io/en/latest/xsd.html#xnat.classes.ImageScanData
                    res_keys = [val.label.lower() for val in val_scan.resources.values()]

                    # print(res_keys)
                    if "nifti" in res_keys:
                        lower_descript = val_scan.series_description.lower()
                        if "loca" not in lower_descript:
                            print("**** Downloading NIFTI for scan {} for expe {}".format(val_scan.series_description, val_exp.label))
                            val_scan.resources["NIFTI"].download_dir(nifti_data_path)

                    # if not "DICOM" in res_keys:
                    #     print("DICOM resource not found for scan {} , skipping".format(
                    #         val_scan.series_description))
                    #     continue
                    #
                    # if not "NIFTI" in res_keys:
                    #     print("NIFTI resource not found for scan {} , skipping".format(
                    #         val_scan.series_description))
                    #     continue
                    #
                    # if val_scan.resources["DICOM"].file_count < 10:
                    #     # print("Not enough slices in scan {} ({} < 10), skipping".format(
                    #     # val_scan.series_description,
                    #     # val_scan.resources["DICOM"].file_count))
                    #     continue
                    #
                    # if val_scan.parameters.voxel_res.z is None:
                    #     continue
                    #
                    # if val_scan.parameters.voxel_res.z > 3.0:
                    #     # print("Resolution in z dimension is to high for scan {} ({} >  3.0), skipping".format(
                    #     # val_scan.series_description,
                    #     # val_scan.parameters.voxel_res.z))
                    #     continue
                    #
                    # ## if non has been skippped, we downlad the corresponding NIFTI
                    # print(
                    #     "**** Downloading NIFTI for scan {} for expe {}".format(val_scan.series_description, val_exp.label))
                    # val_scan.resources["NIFTI"].download_dir(nifti_data_path)
