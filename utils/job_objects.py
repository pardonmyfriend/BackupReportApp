def get_job_objects(backups, backups_obj):
    backup_jobs = []
    backup_job_obj = {}

    for i in range(len(backups)):
        current_job = backups.loc[i, 'Backup Job']

        if current_job not in backup_jobs:
            backup_jobs.append(current_job)

    for i in range(len(backups_obj)):
        current_job = backups_obj.loc[i, 'Backup Job']
        current_obj = backups_obj.loc[i, 'Object']

        if current_job not in backup_job_obj:
            backup_job_obj[current_job] = []

        if current_obj not in backup_job_obj[current_job]:
            backup_job_obj[current_job].append(current_obj)

    return backup_job_obj