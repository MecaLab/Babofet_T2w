import sys; print('Python %s on %s' % (sys.version, sys.platform))
sys.path.extend(['/home/patty/Documents/babofet', '/home/patty/Documents/marsFet'])

import os
import subprocess
from tools import data_organization as tdo


if __name__ == "__main__":
    # chemin vers le repertoire contenant les images HASTE et TRUEFISP
    input_DB_path = '/home/patty/Documents/babofet_DB/nifti_from_Xnat'
    # chemin vers le répertoire qui contiendra les bonnes images avec un masque precis
    output_DB_path = '/home/patty/Documents/babofet_DB/processing'

    recon_approach = 'ebner'#'Kuklisova'#'ebner'#

    # Recuperation images pour nifty
    subject_IDs = os.listdir(input_DB_path)
    subject_IDs.sort()
    subject_IDs.reverse()
    print('subjects to be processed')
    print(subject_IDs)
    subjects_failed = list()
    all_subject_processing_status = list()
    for subject_ID in subject_IDs: #on parcourt tous les sujets
        subject_processing_status = [subject_ID]
        subj_output_dir = os.path.join(output_DB_path, subject_ID)

        print('--------------'+subject_ID)
        # check nifti data present for this subject
        dir_list = os.listdir(os.path.join(input_DB_path, subject_ID, 'scans'))
        haste_files = list()
        truefisp_files = list()
        for d in dir_list:
            d_lower = d.lower()
            if 'haste' in d_lower:
                haste_files.append(d)
            if 'truefisp' in d_lower:
                truefisp_files.append(d)

        # process HASTE images if data exist
        if len(haste_files) > 0:
            print('---- haste')
            haste_subj_output_dir = os.path.join(subj_output_dir, 'haste')
            bm_haste_subj_output_dir = os.path.join(haste_subj_output_dir, 'brainmask')
            # create output directories for haste if it does not exist
            recons_haste_subj_output_dir = os.path.join(haste_subj_output_dir, 'reconstruction_'+recon_approach)
            if not os.path.exists(recons_haste_subj_output_dir):
                os.mkdir(recons_haste_subj_output_dir)
            # recons_haste_subj_output = os.path.join(recons_haste_subj_output_dir, subject_ID+'_haste_3DHR.nii')
            # if os.path.exists(recons_haste_subj_output):
            #     print('-------reconstruction already done for haste series')
            # else:
            # retrieve anat and brainmask images
            anat_img = list()
            bm_img = list()
            for f in haste_files:
                nifti_file_name, nifti_full_path = tdo.file_name_from_path(input_DB_path, subject_ID, f)
                s_nifti_file_name = nifti_file_name.split('.')
                bm_nifti_file_name = s_nifti_file_name[0]+'_brainmask.nii'
                bm_output_file = os.path.join(bm_haste_subj_output_dir, bm_nifti_file_name)
                if os.path.exists(nifti_full_path) and os.path.exists(bm_output_file):
                    anat_img.append(nifti_full_path)
                    bm_img.append(bm_output_file)
            subject_processing_status.append(str(len(bm_img)) + '_haste_images_with_bm')

            if len(bm_img) > 2:
                # prepare the command line
                if recon_approach=='ebner':
                    # RECONSTRUCTION EBNER
                    recons_haste_subj_output = os.path.join(recons_haste_subj_output_dir,
                                                            subject_ID + '_haste_3DHR.nii.gz')
                    motion_subfolder = os.path.join(recons_haste_subj_output_dir, 'motion_correction')
                    if os.path.exists(recons_haste_subj_output):
                        print('-------ebner reconstruction already done for haste series')
                    else:
                        if not os.path.exists(motion_subfolder):
                            os.mkdir(motion_subfolder)
                        cmd_os = 'niftymic_reconstruct_volume --filenames '
                        for v in anat_img:
                            cmd_os+=v+' '
                        cmd_os+=' --filenames-masks '
                        for v in bm_img:
                            cmd_os+=v+' '

                        cmd_os+=' --output '+recons_haste_subj_output
                        cmd_os+=' --alpha 0.01 --threshold-first 0.6 --threshold 0.7 --intensity-correction 1 --bias-field-correction 1 --isotropic-resolution 0.5'
                        cmd_os+=' --dilation-radius 5'
                        cmd_os+=' --subfolder-motion-correction '+motion_subfolder
                        cmd_os+=' --use-masks-srr 1'
                        # run the command line
                        print(cmd_os)
                        try:
                            re = subprocess.run(cmd_os, shell=True)
                            re.check_returncode()
                            subject_processing_status.append('haste_Ebner_recon_OK')
                        except:
                            print(subject_ID+'_haste_ebner failed')
                            subject_processing_status.append('haste_Ebner_recon_failed')
                            subjects_failed.append(subject_ID+'_haste_ebner')
                else:
                    # RECONSTRUCTION Kuklisova
                    ordered = list(range(len(bm_img)))
                    orders = [ordered, list(reversed(ordered))]
                    for ind, order in enumerate(orders):
                        recons_haste_subj_output_subdir = os.path.join(recons_haste_subj_output_dir, 'slice_order_'+str(ind))
                        if not os.path.exists(recons_haste_subj_output_subdir):
                            os.mkdir(recons_haste_subj_output_subdir)
                        recons_haste_subj_output = os.path.join(recons_haste_subj_output_subdir,
                                                            subject_ID + '_haste_3DHR.nii.gz')
                        if os.path.exists(recons_haste_subj_output):
                            print('-------kuklisova reconstruction already done for haste series')
                        else:
                            cmd_os = 'cd '+recons_haste_subj_output_subdir+'; /home/patty/Documents/irtk-simple/build/bin/reconstruction '+recons_haste_subj_output
                            cmd_os += ' '+str(len(bm_img))+' '
                            print(bm_img)
                            print(anat_img)
                            for v in order:
                                print(v)
                                cmd_os+=anat_img[v]+' '
                            # cmd_os+=' -mask '
                            # for v in bm_img:
                            #     cmd_os+=v+' '
                            cmd_os+='-mask '+bm_img[order[0]]
                            cmd_os+=' -resolution 0.5 '
                            cmd_os+=' -global_bias_correction -debug'
                            # run the command line
                            print(cmd_os)
                            try:
                                re = subprocess.run(cmd_os, shell=True)
                                re.check_returncode()
                                subject_processing_status.append('haste_kuklisova_recon_slice_order_'+str(ind)+'_OK')
                            except:
                                print(subject_ID+'_haste_kulisova failed')
                                subjects_failed.append(subject_ID+'_haste_kulisova')
                                subject_processing_status.append('haste_kuklisova_recon_slice_order_'+str(ind)+'_failed')

        # process TRUFISP images if data exist
        if len(truefisp_files) > 0:
            print('---- truefisp')
            haste_subj_output_dir = os.path.join(subj_output_dir, 'truefisp')
            bm_haste_subj_output_dir = os.path.join(haste_subj_output_dir, 'brainmask')
            # create output directories for haste if it does not exist
            recons_haste_subj_output_dir = os.path.join(haste_subj_output_dir, 'reconstruction_'+recon_approach)
            if not os.path.exists(recons_haste_subj_output_dir):
                os.mkdir(recons_haste_subj_output_dir)
            # recons_haste_subj_output = os.path.join(recons_haste_subj_output_dir, subject_ID+'_truefisp_3DHR.nii')
            # if os.path.exists(recons_haste_subj_output):
            #     print('-------reconstruction already done for truefisp series')
            # else:
            # retrieve anat and brainmask images
            anat_img = list()
            bm_img = list()
            for f in truefisp_files:
                nifti_file_name, nifti_full_path = tdo.file_name_from_path(input_DB_path, subject_ID, f)
                s_nifti_file_name = nifti_file_name.split('.')
                bm_nifti_file_name = s_nifti_file_name[0]+'_brainmask.nii'
                bm_output_file = os.path.join(bm_haste_subj_output_dir, bm_nifti_file_name)
                if os.path.exists(nifti_full_path) and os.path.exists(bm_output_file):
                    anat_img.append(nifti_full_path)
                    bm_img.append(bm_output_file)
            subject_processing_status.append(str(len(bm_img)) + '_truefisp_images_with_bm')

            if len(bm_img) > 2:
                # prepare the command line
                if recon_approach=='ebner':
                    # RECONSTRUCTION EBNER
                    recons_haste_subj_output = os.path.join(recons_haste_subj_output_dir,
                                                            subject_ID + '_truefisp_3DHR.nii.gz')
                    motion_subfolder = os.path.join(recons_haste_subj_output_dir, 'motion_correction')
                    if os.path.exists(recons_haste_subj_output):
                        print('-------ebner reconstruction already done for truefisp series')
                    else:
                        if not os.path.exists(motion_subfolder):
                            os.mkdir(motion_subfolder)
                        cmd_os = 'niftymic_reconstruct_volume --filenames '
                        for v in anat_img:
                            cmd_os+=v+' '
                        cmd_os+=' --filenames-masks '
                        for v in bm_img:
                            cmd_os+=v+' '

                        cmd_os+=' --output '+recons_haste_subj_output
                        cmd_os+=' --alpha 0.01 --threshold-first 0.6 --threshold 0.7 --intensity-correction 1 --bias-field-correction 1 --isotropic-resolution 0.5'
                        cmd_os+=' --dilation-radius 5'
                        cmd_os+=' --subfolder-motion-correction '+motion_subfolder
                        cmd_os+=' --use-masks-srr 1'
                        # run the command line
                        print(cmd_os)
                        try:
                            re = subprocess.run(cmd_os, shell=True)
                            re.check_returncode()
                            subject_processing_status.append('truefisp_Ebner_recon_OK')
                        except:
                            print(subject_ID+'_truefisp_ebner failed')
                            subject_processing_status.append('truefisp_Ebner_recon_failed')
                            subjects_failed.append(subject_ID+'_truefisp_ebner')
                else:
                    # RECONSTRUCTION Kuklisova
                    ordered = list(range(len(bm_img)))
                    orders = [ordered, list(reversed(ordered))]
                    for ind, order in enumerate(orders):
                        recons_haste_subj_output_subdir = os.path.join(recons_haste_subj_output_dir, 'slice_order_'+str(ind))
                        if not os.path.exists(recons_haste_subj_output_subdir):
                            os.mkdir(recons_haste_subj_output_subdir)
                        recons_haste_subj_output = os.path.join(recons_haste_subj_output_subdir,
                                                            subject_ID + '_truefisp_3DHR.nii.gz')
                        if os.path.exists(recons_haste_subj_output):
                            print('-------kuklisova reconstruction already done for haste series')
                        else:
                            cmd_os = 'cd '+recons_haste_subj_output_subdir+'; /home/patty/Documents/irtk-simple/build/bin/reconstruction '+recons_haste_subj_output
                            cmd_os += ' '+str(len(bm_img))+' '
                            for v in order:
                                print(v)
                                cmd_os+=anat_img[v]+' '
                            # cmd_os+=' -mask '
                            # for v in bm_img:
                            #     cmd_os+=v+' '
                            cmd_os+='-mask '+bm_img[order[0]]
                            cmd_os+=' -resolution 0.5 '
                            cmd_os+=' -global_bias_correction -debug'
                            # run the command line
                            print(cmd_os)
                            try:
                                re = subprocess.run(cmd_os, shell=True)
                                re.check_returncode()
                                subject_processing_status.append('truefisp_kuklisova_recon_slice_order_'+str(ind)+'_OK')
                            except:
                                print(subject_ID+'_truefisp_kulisova failed')
                                subject_processing_status.append('truefisp_kuklisova_recon_slice_order_'+str(ind)+'_failed')
                                subjects_failed.append(subject_ID+'_haste_truefisp')
        print(subject_processing_status)
        all_subject_processing_status.append(subject_processing_status)
    print(str(len(subjects_failed))+' subjects failed')
    print(subjects_failed)
    print('================ subjects processing status  =====================')
    print(all_subject_processing_status)

