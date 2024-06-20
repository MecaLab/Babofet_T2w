import os

import subprocess

if __name__ == "__main__":
    input_DB_path = '/home/patty/Documents/babofet_DB/LoFeBa'
    output_DB_path = '/home/patty/Documents/babofet_DB/processing'

    recon_approach = 'ebner'#'Kuklisova'#'ebner'

    # Recuperation images pour nifty
    subject_IDs = os.listdir(input_DB_path)
    subject_IDs.sort()
    print('subjects to be processed')
    print(subject_IDs)
    for subject_ID in subject_IDs: #on parcourt tous les sujets
        subj_output_dir = os.path.join(output_DB_path, subject_ID)

        print('--------------'+subject_ID)
        # check nifti data present for this subject
        dir_list = os.listdir(os.path.join(input_DB_path, subject_ID, 'nifti','anat'))
        haste_files = list()
        truefisp_files = list()
        for d in dir_list:
            d_lower = d.lower()
            if '.nii' in d_lower:
                if 'haste' in d_lower:
                    if 'run-1' in d_lower:
                        haste_files.append(d)
                if 'trufi' in d_lower:
                    truefisp_files.append(d)

        # process HASTE images if data exist
        if len(haste_files)>0:
            print('---- haste')
            haste_subj_output_dir = os.path.join(subj_output_dir, 'haste')
            bm_haste_subj_output_dir = os.path.join(haste_subj_output_dir, 'brainmask')
            # create output directories for haste if it does not exist
            recons_haste_subj_output_dir = os.path.join(haste_subj_output_dir, 'reconstruction_'+recon_approach)
            if not os.path.exists(recons_haste_subj_output_dir):
                os.mkdir(recons_haste_subj_output_dir)
            recons_haste_subj_output = os.path.join(recons_haste_subj_output_dir, subject_ID+'_haste_3DHR.nii')
            if os.path.exists(recons_haste_subj_output):
                print('-------reconstruction already done for haste series')
            else:
                # retrieve anat and brainmask images
                anat_img = list()
                bm_img = list()
                for f in haste_files:
                    nifti_file_name = os.path.join(input_DB_path, subject_ID, 'nifti', 'anat', f)
                    s_nifti_file_name = f.split('.')
                    bm_nifti_file_name = s_nifti_file_name[0] + '_brainmask.nii'
                    bm_output_file = os.path.join(bm_haste_subj_output_dir, bm_nifti_file_name)
                    anat_img.append(nifti_file_name)
                    bm_img.append(bm_output_file)
                # prepare the command line
                if recon_approach=='ebner':
                    # RECONSTRUCTION EBNER
                    recons_haste_subj_output = os.path.join(recons_haste_subj_output_dir,
                                                            subject_ID + '_haste_3DHR.nii.gz')
                    motion_subfolder = os.path.join(recons_haste_subj_output_dir, 'motion_correction')
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
                    cmd_os+=' --subfolder-motion-correction '+motion_subfolder
                    cmd_os+=' --use-masks-srr 1'
                    # run the command line
                    print(cmd_os)
                    subprocess.run(cmd_os, shell=True)
                else:
                    # RECONSTRUCTION Kuklisova
                    orders = [[0,1,2], [1,2,0], [2,0,1]]
                    for ind, order in enumerate(orders):
                        recons_haste_subj_output_subdir = os.path.join(recons_haste_subj_output_dir, 'slice_order_'+str(ind))
                        os.mkdir(recons_haste_subj_output_subdir)
                        recons_haste_subj_output = os.path.join(recons_haste_subj_output_subdir,
                                                            subject_ID + '_haste_3DHR.nii.gz')
                        cmd_os = 'cd '+recons_haste_subj_output_subdir+'; /home/patty/Documents/irtk-simple/build/bin/reconstruction '+recons_haste_subj_output
                        cmd_os += ' '+str(len(truefisp_files))+' '
                        for v in order:
                            print(v)
                            cmd_os+=anat_img[v]+' '
                        # cmd_os+=' -mask '
                        # for v in bm_img:
                        #     cmd_os+=v+' '
                        cmd_os+=' -mask '+bm_img[order[0]]
                        cmd_os+=' -resolution 0.5 '
                        cmd_os+=' -global_bias_correction -debug'
                        # run the command line
                        print(cmd_os)
                        subprocess.run(cmd_os, shell=True)


        # process TRUFISP images if data exist
        if len(truefisp_files)>0:
            print('---- truefisp')
            haste_subj_output_dir = os.path.join(subj_output_dir, 'truefisp')
            bm_haste_subj_output_dir = os.path.join(haste_subj_output_dir, 'brainmask')
            # create output directories for haste if it does not exist
            recons_haste_subj_output_dir = os.path.join(haste_subj_output_dir, 'reconstruction_'+recon_approach)
            if not os.path.exists(recons_haste_subj_output_dir):
                os.mkdir(recons_haste_subj_output_dir)
            if os.path.exists(recons_haste_subj_output):
                print('-------reconstruction already done for truefisp series')
            else:
                # retrieve anat and brainmask images
                anat_img = list()
                bm_img = list()
                for f in truefisp_files:
                    nifti_file_name = os.path.join(input_DB_path, subject_ID, 'nifti', 'anat', f)
                    s_nifti_file_name = f.split('.')
                    bm_nifti_file_name = s_nifti_file_name[0] + '_brainmask.nii'
                    bm_output_file = os.path.join(bm_haste_subj_output_dir, bm_nifti_file_name)
                    anat_img.append(nifti_file_name)
                    bm_img.append(bm_output_file)
                # prepare the command line
                if recon_approach=='ebner':
                    # RECONSTRUCTION EBNER
                    recons_haste_subj_output = os.path.join(recons_haste_subj_output_dir,
                                                            subject_ID + '_truefisp_3DHR.nii.gz')
                    motion_subfolder = os.path.join(recons_haste_subj_output_dir, 'motion_correction')
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
                    cmd_os+=' --subfolder-motion-correction '+motion_subfolder
                    cmd_os+=' --use-masks-srr 1'
                    # run the command line
                    print(cmd_os)
                    subprocess.run(cmd_os, shell=True)
                else:
                    # RECONSTRUCTION Kuklisova
                    orders = [[0,1,2], [1,2,0], [2,0,1]]
                    for ind, order in enumerate(orders):
                        recons_haste_subj_output_subdir = os.path.join(recons_haste_subj_output_dir, 'slice_order_'+str(ind))
                        os.mkdir(recons_haste_subj_output_subdir)
                        recons_haste_subj_output = os.path.join(recons_haste_subj_output_subdir,
                                                            subject_ID + '_truefisp_3DHR.nii.gz')
                        cmd_os = 'cd '+recons_haste_subj_output_subdir+'; /home/patty/Documents/irtk-simple/build/bin/reconstruction '+recons_haste_subj_output
                        cmd_os += ' '+str(len(truefisp_files))+' '
                        for v in order:
                            print(v)
                            cmd_os+=anat_img[v]+' '
                        # cmd_os+=' -mask '
                        # for v in bm_img:
                        #     cmd_os+=v+' '
                        cmd_os+=' -mask '+bm_img[order[0]]
                        cmd_os+=' -resolution 0.5 '
                        cmd_os+=' -global_bias_correction -debug'
                        # run the command line
                        print(cmd_os)
                        subprocess.run(cmd_os, shell=True)

