import configuration as cfg


subjects = ["Fabienne", "Aziza", "Formule"]
sessions = ["01", "05", "08", "09"]

stacks_base_path = cfg.MESO_OUTPUT_PATH
recons_base_path = cfg.DATA_PATH

for subject in subjects:
    for session in sessions:
        subj_session = f"sub-{subject}_ses-{session[3:]}"
        print(subj_session)