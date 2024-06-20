import sys; print('Python %s on %s' % (sys.version, sys.platform))
#sys.path.extend(['/home/patty/Documents/babofet', '/home/patty/Documents/marsFet'])
sys.path.extend(['/hpc/meca/softs/dev/auzias/pyhon/babofet', '/hpc/meca/softs/dev/auzias/pyhon/marsFet'])

import os
import shutil
import subprocess

from tools import data_organization as tdo

if __name__ == "__main__":
    # chemin vers le repertoire contenant les images HASTE et TRUEFISP
    #input_DB_path = '/home/patty/Documents/babofet_DB/nifti_from_Xnat'
    input_DB_path = '/envau/work/meca/data/babofet_DB/nifti_from_Xnat'
    # chemin vers le répertoire qui contiendra les bonnes images avec un masque precis
    #output_DB_path = '/home/patty/Documents/babofet_DB/processing'
    output_DB_path = '/hpc/meca/users/auzias/babofet_DB_proc'

#    table_check = os.path.join('/home/patty/Documents', 'subjects_with_mask.csv')  #table qui indiquera le nombre d'images HASTE et TRUEFISP correctes avec masque precis

#    txt_common = 'subject_ID; haste_file_nb;truefisp_file_nb' + '\n' #chaine qui constituera la table table_check
    subject_IDs = os.listdir(input_DB_path)
    subject_IDs.sort()
    print('subjects to be processed')
    print(subject_IDs)
    subject_processed_haste = list()
    subject_processed_truefisp = list()

    for subject_ID in subject_IDs: #on parcourt tous les sujets
        subj_output_dir = os.path.join(output_DB_path, subject_ID)
        # create output directory if it does not exist
        if not os.path.exists(subj_output_dir):
            os.mkdir(subj_output_dir)

        print('--------------'+subject_ID)
        # check nifti data present for this subject
        dir_list = os.listdir(os.path.join(input_DB_path, subject_ID, 'scans'))
        haste_files = list()
        truefisp_files = list()
        for d in dir_list:
            d_lower = d.lower()
            if 'haste' in d_lower:
                haste_files.append(d)
            if 'trufi' in d_lower:
                truefisp_files.append(d)

        # process HASTE images if data exist
        if len(haste_files)>0:
            haste_subj_output_dir = os.path.join(subj_output_dir, 'haste')
            bm_haste_subj_output_dir = os.path.join(haste_subj_output_dir, 'denoising')
            # create output directories for haste if it does not exist
            if not os.path.exists(haste_subj_output_dir):
                os.mkdir(haste_subj_output_dir)
            if not os.path.exists(bm_haste_subj_output_dir):
                os.mkdir(bm_haste_subj_output_dir)
            # DENOISING
            already_done = list()
            for f in haste_files:
                nifti_file_name, nifti_full_path = tdo.file_name_from_path(input_DB_path, subject_ID, f)
                s_nifti_file_name = nifti_file_name.split('.')
                bm_nifti_file_name = s_nifti_file_name[0]+'_denoised.nii'
                bm_output_file = os.path.join(bm_haste_subj_output_dir, bm_nifti_file_name)
                if os.path.exists(bm_output_file):
                    already_done.append(bm_output_file)
                    print('-------denoised already done for haste series')
                else:
                    cmd = ['/hpc/soft/ANTS/antsbin/bin/DenoiseImage', '-i']
                    cmd.append(nifti_full_path)
                    cmd.append('-o')
                    cmd.append(bm_output_file)
                    print(cmd)
                    subprocess.run(cmd)#, shell=True)
                    subject_processed_haste.append(bm_output_file)


        # process TRUEFIST images if data exist
        if len(truefisp_files)>0:
            truefisp_subj_output_dir = os.path.join(subj_output_dir, 'truefisp')
            bm_truefisp_subj_output_dir = os.path.join(truefisp_subj_output_dir, 'denoising')
            # create output directories for haste if it does not exist
            if not os.path.exists(truefisp_subj_output_dir):
                os.mkdir(truefisp_subj_output_dir)
            if not os.path.exists(bm_truefisp_subj_output_dir):
                os.mkdir(bm_truefisp_subj_output_dir)
            # DENOISING
            already_done = list()
            for f in truefisp_files:
                nifti_file_name, nifti_full_path = tdo.file_name_from_path(input_DB_path, subject_ID, f)
                s_nifti_file_name = nifti_file_name.split('.')
                bm_nifti_file_name = s_nifti_file_name[0]+'_denoised.nii'
                bm_output_file = os.path.join(bm_truefisp_subj_output_dir, bm_nifti_file_name)
                if os.path.exists(bm_output_file):
                    already_done.append(bm_output_file)
                    print('-------denoised already done for truefisp series')
                else:
                    cmd = ['/hpc/soft/ANTS/antsbin/bin/DenoiseImage', '-i']
                    cmd.append(nifti_full_path)
                    cmd.append('-o')
                    cmd.append(bm_output_file)
                    print(cmd)
                    subprocess.run(cmd)#, shell=True)
                    subject_processed_truefisp.append(bm_output_file)

    print('-----------------------------------------------------------subject_processed_truefisp')
    print(subject_processed_truefisp)
    print('-----------------------------------------------------------subject_processed_haste')
    print(subject_processed_haste)

