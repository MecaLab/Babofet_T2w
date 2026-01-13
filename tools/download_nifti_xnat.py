import xnat
import os
import sys
sys.path.insert(0, os.path.abspath(os.curdir))
import configuration as cfg

####### connect session
# http://xnat.intlocal.univ-amu.fr:8080/
session = xnat.connect('http://xnat.intlocal.univ-amu.fr:8080/', user='BaptBat')

print("Connected to XNAT server: ", session)

if __name__ == "__main__":
    nifti_data_path = "data_xnat"
    if not os.path.exists(nifti_data_path):
        os.makedirs(nifti_data_path)
    project_name = "LoFeBa"
    proj_data = session.projects[project_name]

    for key_sub, val_sub in proj_data.subjects.items():
        subject = val_sub.label  # sub-Fabienne
        print('---------------------'+subject)
        for key_exp, val_exp in val_sub.experiments.items():
            if os.path.exists(os.path.join(nifti_data_path, val_exp.label)):
                print(f'--{val_exp.label} data already downloaded, skip')
                continue
            if any(name in val_exp.label for name in ["Fabienne", "Formule", "Forme", "Aziza", "Borgne", "Olive", "Hacienda", "Gorgone", "Filoutte"]):
                print(f"--avoiding {val_exp.label} experiment")
                continue
            print(f'----Downloading {val_exp.label}')
            for key_scan, val_scan in val_exp.scans.items():
                res_keys = [val.label.lower() for val in val_scan.resources.values()]
                if "nifti" in res_keys:
                    lower_descript = val_scan.series_description.lower()
                    if "loca" not in lower_descript:
                        val_scan.resources["NIFTI"].download_dir(nifti_data_path)
