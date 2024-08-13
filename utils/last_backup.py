import pandas as pd


def get_last_backups(backups, backups_obj):
    backup_jobs = []
    backup_job_obj = {}
    last_backup = backups.iloc[0:0]
    last_backup_obj = backups_obj.iloc[0:0]

    for i in range(len(backups)):
        current_job = backups.loc[i, 'Backup Job']

        if current_job not in backup_jobs:
            backup_jobs.append(current_job)
            last_backup = pd.concat([last_backup, backups.iloc[[i]]], ignore_index=True)

    for i in range(len(backups_obj)):
        current_job = backups_obj.loc[i, 'Backup Job']
        current_obj = backups_obj.loc[i, 'Object']

        if current_job not in backup_job_obj:
            backup_job_obj[current_job] = []

        if current_obj not in backup_job_obj[current_job]:
            backup_job_obj[current_job].append(current_obj)
            last_backup_obj = pd.concat([last_backup_obj, backups_obj.iloc[[i]]], ignore_index=True)

    return last_backup, last_backup_obj