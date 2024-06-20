# -*- coding: utf-8 -*-
"""
Created on Tu Aug 13 10:46:37 2019

@author: Guillaume Auzias

convert dicom to nifti files

"""

import os
import pydicom as dc


if __name__ == "__main__":
    DB_path = '/home/patty/Documents/babofet_DB/LoFeBa'
    table_info_common = os.path.join(DB_path, 'nifti_convert_info.csv')

    subj_files_list = os.listdir(DB_path)
    subject_IDs =[]
    for fil in subj_files_list:
        if not '.' in fil:
            subject_IDs.append(fil)

    for subject_ID in subject_IDs:
        print('processing subject '+subject_ID)
        subject_dir = os.path.join(DB_path, subject_ID)
        subject_dicom_dir = os.path.join(subject_dir, 'dicom')
        subject_nifti_dir = os.path.join(subject_dir, 'nifti')
        subject_info_file = os.path.join(subject_dir, subject_ID+'_info.txt')

        # create nifti folder
        if os.path.exists(subject_nifti_dir):
            print('--nifti folder already exists, abort!')
        else:
            os.mkdir(subject_nifti_dir)
            os.chdir(subject_nifti_dir)

            dicom_dir_list = os.listdir(subject_dicom_dir)
            for dicom_dir_l in dicom_dir_list:
                dicom_dir = os.path.join(subject_dicom_dir, dicom_dir_l)
                dicom_list = os.listdir(dicom_dir)

                for dicom_file in dicom_list:
                    # output_dir = os.path.join(subject_dir,dicom_file)
                    # os.mkdir(output_dir)
                    dicom_fullfile = os.path.join(dicom_dir, dicom_file)
                    dinifti_cmd = "dcm2niix -i y -z i -f '%p_%s' -o "+subject_nifti_dir+" "+dicom_fullfile
                    print(dinifti_cmd)
                    os.system(dinifti_cmd)

            print('--dicom to nifti conversion done')
            # write subject info to csv
            file_list = os.listdir(os.path.join(dicom_dir, dicom_file))
            d1 = dc.dcmread(os.path.join(dicom_dir, dicom_file, file_list[0]))
            txt_subj = 'StudyDate : ' + d1.StudyDate + '\n'+'Manufacturer : ' + d1.Manufacturer + '\n'+'ManufacturerModelName : ' + d1.ManufacturerModelName + '\n'
            file_subj = open(subject_info_file, 'w')
            file_subj.write(txt_subj)
            file_subj.close()

            # write subject info to common csv
            txt_common = subject_ID + ';' + d1.StudyDate + ';' + d1.Manufacturer + ';' + d1.ManufacturerModelName + '\n'

            print(txt_common)
            file_common = open(table_info_common, 'a+')
            file_common.write(txt_common)
            file_common.close()
            print('--tables updated')
