import sys
import os
sys.path.insert(0, os.path.abspath(os.curdir))
print(sys.path)
import shutil
import subprocess
print('Python %s on %s' % (sys.version, sys.platform))
import configuration as cfg

from tools import data_organization as tdo

if __name__ == "__main__":

    input_path = cfg.MESO_PATH
    output_path = cfg.MESO_OUTPUT_PATH

    subject_IDs = os.listdir(input_path)
    subject_IDs.sort()
    print('subjects to be processed')
    print(subject_IDs)
    subject_processed_haste = list()
    subject_processed_truefisp = list()

    for subject_ID in subject_IDs:  #on parcourt tous les sujets
        subj_output_dir = os.path.join(output_path, subject_ID)
        # create output directory if it does not exist
        if not os.path.exists(subj_output_dir):
            os.mkdir(subj_output_dir)

        print('--------------' + subject_ID)

        # check nifti data present for this subject
        dir_list = os.listdir(os.path.join(input_path, subject_ID, 'scans'))
        haste_files = list()
        truefisp_files = list()
        for d in dir_list:
            d_lower = d.lower()
            if 'haste' in d_lower:
                haste_files.append(d)
            if 'trufi' in d_lower:
                truefisp_files.append(d)

        # process HASTE images if data exist
        if len(haste_files) > 0:
            haste_subj_output_dir = os.path.join(subj_output_dir, 'haste')
            bm_haste_subj_output_dir = os.path.join(haste_subj_output_dir, 'brainmask')
            # create output directories for haste if it does not exist
            if not os.path.exists(haste_subj_output_dir):
                os.mkdir(haste_subj_output_dir)
            if not os.path.exists(bm_haste_subj_output_dir):
                os.mkdir(bm_haste_subj_output_dir)
            # EXTRACTION DES MASQUES
            cmd1 = ['--input_names']
            cmd2 = [' --segment_output_names']
            already_done = list()
            for f in haste_files:
                nifti_file_name, nifti_full_path = tdo.file_name_from_path(input_path, subject_ID, f)
                s_nifti_file_name = nifti_file_name.split('.')
                bm_nifti_file_name = s_nifti_file_name[0] + '_brainmask.nii'
                bm_output_file = os.path.join(bm_haste_subj_output_dir, bm_nifti_file_name)
                if os.path.exists(bm_output_file):
                    already_done.append(True)
                else:
                    cmd1.append(nifti_full_path)
                    cmd2.append(bm_output_file)
            if sum(already_done) < len(haste_files):
                subject_processed_haste.append(subject_ID)
                #cmd = ['/home/patty/miniconda3/bin/python', '/usr/local/fetal_brain_seg/fetal_brain_seg.py']
                cmd = ['python', '/usr/local/fetal_brain_seg/fetal_brain_seg.py']
                cmd.extend(cmd1)
                cmd.extend(cmd2)  # on joint les 2 parties pour avoir la commande complete
                #print(cmd)
                #subprocess.run(cmd, shell=True)#, capture_output=True)
                cmd_os = 'cd /usr/local/fetal_brain_seg;'
                for v in cmd:
                    cmd_os += v + ' '
                print(cmd_os)
                subprocess.run(cmd_os, shell=True)
            else:
                print('-------brainmask already done for haste series')

        # process TRUEFIST images if data exist
        if len(truefisp_files) > 0:
            truefisp_subj_output_dir = os.path.join(subj_output_dir, 'truefisp')
            bm_truefisp_subj_output_dir = os.path.join(truefisp_subj_output_dir, 'brainmask')
            # create output directories for haste if it does not exist
            if not os.path.exists(truefisp_subj_output_dir):
                os.mkdir(truefisp_subj_output_dir)
            if not os.path.exists(bm_truefisp_subj_output_dir):
                os.mkdir(bm_truefisp_subj_output_dir)
            # EXTRACTION DES MASQUES
            cmd1 = ['--input_names']
            cmd2 = [' --segment_output_names']
            already_done = list()
            for f in truefisp_files:
                nifti_file_name, nifti_full_path = tdo.file_name_from_path(cfg.DATA_PATH, subject_ID, f)
                s_nifti_file_name = nifti_file_name.split('.')
                bm_nifti_file_name = s_nifti_file_name[0] + '_brainmask.nii'
                bm_output_file = os.path.join(bm_truefisp_subj_output_dir, bm_nifti_file_name)
                if os.path.exists(bm_output_file):
                    already_done.append(True)
                else:
                    cmd1.append(nifti_full_path)
                    cmd2.append(bm_output_file)
            if sum(already_done) < len(truefisp_files):
                subject_processed_truefisp.append(subject_ID)
                #cmd = ['/home/patty/miniconda3/bin/python', '/usr/local/fetal_brain_seg/fetal_brain_seg.py']
                cmd = ['python', '/usr/local/fetal_brain_seg/fetal_brain_seg.py']
                cmd.extend(cmd1)
                cmd.extend(cmd2)  # on joint les 2 parties pour avoir la commande complete
                #print(cmd)
                #subprocess.run(cmd, shell=True)#, capture_output=True)
                cmd_os = 'cd /usr/local/fetal_brain_seg;'
                for v in cmd:
                    cmd_os += v + ' '
                print(cmd_os)
                subprocess.run(cmd_os, shell=True)
            else:
                print('-------brainmask already done for truefisp series')

    print('-----------------------------------------------------------subject_processed_truefisp')
    print(subject_processed_truefisp)
    print('-----------------------------------------------------------subject_processed_haste')
    print(subject_processed_haste)

"""
old version when the nifti files are not organized in the 'scans' directory

    subject_IDs = os.listdir(input_DB_path)
    subject_IDs.sort()
    print('subjects to be processed')
    print(subject_IDs)
    for subject_ID in subject_IDs: #on parcourt tous les sujets
        subj_output_dir = os.path.join(output_DB_path, subject_ID)
        # create output directory if it does not exist
        if not os.path.exists(subj_output_dir):
            os.mkdir(subj_output_dir)

        print('--------------'+subject_ID)
        # check nifti data present for this subject
        dir_list = os.listdir(os.path.join(input_DB_path, subject_ID))
        haste_files = list()
        truefisp_files = list()
        for d in dir_list:
            subdir_list = os.listdir(os.path.join(input_DB_path, subject_ID, d, 'NIFTI'))
            for s_d in subdir_list:
                s_d_lower = s_d.lower()
                if '.nii' in s_d_lower:
                    if 'haste' in s_d_lower:
                        haste_files.append(os.path.join(input_DB_path, subject_ID, d, 'NIFTI', s_d))
                    if 'trufi' in s_d_lower:
                        truefisp_files.append(os.path.join(input_DB_path, subject_ID, d, 'NIFTI',s_d))

        # process HASTE images if data exist
        if len(haste_files)>0:
            haste_subj_output_dir = os.path.join(subj_output_dir, 'haste')
            bm_haste_subj_output_dir = os.path.join(haste_subj_output_dir, 'brainmask')
            # create output directories for haste if it does not exist
            if not os.path.exists(haste_subj_output_dir):
                os.mkdir(haste_subj_output_dir)
            if not os.path.exists(bm_haste_subj_output_dir):
                os.mkdir(bm_haste_subj_output_dir)
            # EXTRACTION DES MASQUES
            cmd1 = ['--input_names']
            cmd2 = [' --segment_output_names']
            already_done = list()
            for f in haste_files:
                nifti_file_name = os.path.join(input_DB_path, subject_ID, 'nifti','anat', f)
                s_nifti_file_name = f.split('.')
                bm_nifti_file_name = s_nifti_file_name[0]+'_brainmask.nii'
                bm_output_file = os.path.join(bm_haste_subj_output_dir, bm_nifti_file_name)
                if os.path.exists(bm_output_file):
                    already_done.append(True)
                else:
                    cmd1.append(nifti_file_name)
                    cmd2.append(bm_output_file)
            if sum(already_done)<len(haste_files):
                #cmd = ['/home/patty/miniconda3/bin/python', '/usr/local/fetal_brain_seg/fetal_brain_seg.py']
                cmd = ['python', '/usr/local/fetal_brain_seg/fetal_brain_seg.py']
                cmd.extend(cmd1)
                cmd.extend(cmd2)  # on joint les 2 parties pour avoir la commande complete
                #print(cmd)
                #subprocess.run(cmd, shell=True)#, capture_output=True)
                cmd_os = 'cd /usr/local/fetal_brain_seg;'
                for v in cmd:
                    cmd_os+=v+' '
                print(cmd_os)
                subprocess.run(cmd_os, shell=True)
            else:
                print('-------brainmask already done for haste series')

        # process TRUEFIST images if data exist
        if len(truefisp_files)>0:
            truefisp_subj_output_dir = os.path.join(subj_output_dir, 'truefisp')
            bm_truefisp_subj_output_dir = os.path.join(truefisp_subj_output_dir, 'brainmask')
            # create output directories for haste if it does not exist
            if not os.path.exists(truefisp_subj_output_dir):
                os.mkdir(truefisp_subj_output_dir)
            if not os.path.exists(bm_truefisp_subj_output_dir):
                os.mkdir(bm_truefisp_subj_output_dir)
            # EXTRACTION DES MASQUES
            cmd1 = ['--input_names']
            cmd2 = [' --segment_output_names']
            already_done = list()
            for f in truefisp_files:
                nifti_file_name = os.path.join(input_DB_path, subject_ID, 'nifti','anat', f)
                s_nifti_file_name = f.split('.')
                bm_nifti_file_name = s_nifti_file_name[0]+'_brainmask.nii'
                bm_output_file = os.path.join(bm_truefisp_subj_output_dir, bm_nifti_file_name)
                if os.path.exists(bm_output_file):
                    already_done.append(True)
                else:
                    cmd1.append(nifti_file_name)
                    cmd2.append(bm_output_file)
            if sum(already_done)<len(truefisp_files):
                #cmd = ['/home/patty/miniconda3/bin/python', '/usr/local/fetal_brain_seg/fetal_brain_seg.py']
                cmd = ['python', '/usr/local/fetal_brain_seg/fetal_brain_seg.py']
                cmd.extend(cmd1)
                cmd.extend(cmd2)  # on joint les 2 parties pour avoir la commande complete
                #print(cmd)
                #subprocess.run(cmd, shell=True)#, capture_output=True)
                cmd_os = 'cd /usr/local/fetal_brain_seg;'
                for v in cmd:
                    cmd_os+=v+' '
                print(cmd_os)
                subprocess.run(cmd_os, shell=True)
            else:
                print('-------brainmask already done for truefisp series')
"""
