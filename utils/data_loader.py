import streamlit as st
import pandas as pd
from datetime import datetime
import re


MONTHS_MAP = {
    'stycznia': 'styczeń',
    'lutego': 'luty',
    'marca': 'marzec',
    'kwietnia': 'kwiecień',
    'maja': 'maj',
    'czerwca': 'czerwiec',
    'lipca': 'lipiec',
    'sierpnia': 'sierpień',
    'września': 'wrzesień',
    'października': 'październik',
    'listopada': 'listopad',
    'grudnia': 'grudzień'
}


def replace_months(date_str):
    for key, value in MONTHS_MAP.items():
        date_str = date_str.replace(key, value)
    return date_str


def report_summary(sheet):
    backup_entry_template = {
        'Date': None,
        'Backup Job': None,
        'Status': None,
        'Success': None,
        'Warning': None,
        'Error': None,
        'Start Time': None,
        'End Time': None,
        'Duration': None,
        'Total Size': None,
        'Backup Size': None,
        'Data Read': None,
        'Dedupe': None,
        'Transferred': None,
        'Compression': None
    }

    details_entry_template = {
        'Date': None,
        'Backup Job': None,
        'Object': None,
        'Status': None,
        'Start Time': None,
        'End Time': None,
        'Duration': None,
        'Size': None,
        'Read': None,
        'Transferred': None
    }

    backup_jobs_list = []
    details_list = []
    details_section = False

    for row in sheet.iter_rows(values_only=True):
        if row[0] and "Veeam Backup & Replication" in row[0]:
            break
        elif row[0] and "Backup job" in row[0]:
            details_section = False
            backup_entry = backup_entry_template.copy()
            if "Retry" in row[0]:
                match = re.search(r'Backup job: (.*?) \(Retry \d+\)', row[0])
                if match:
                    backup_entry['Backup Job'] = match.group(1)
            else:
                backup_entry['Backup Job'] = row[0].split("Backup job: ")[1].strip()
            backup_entry['Status'] = row[8]
        elif row[0] in ["Success", "Warning", "Error"] and not details_section:
            backup_entry[row[0]] = row[1]
            backup_entry.update({
                'Start Time': row[3] if row[0] == "Success" else backup_entry['Start Time'],
                'Total Size': row[5] if row[0] == "Success" else backup_entry['Total Size'],
                'Backup Size': row[7] if row[0] == "Success" else backup_entry['Backup Size'],
                'End Time': row[3] if row[0] == "Warning" else backup_entry['End Time'],
                'Data Read': row[5] if row[0] == "Warning" else backup_entry['Data Read'],
                'Dedupe': row[7] if row[0] == "Warning" else backup_entry['Dedupe'],
                'Duration': row[3] if row[0] == "Error" else backup_entry['Duration'],
                'Transferred': row[5] if row[0] == "Error" else backup_entry['Transferred'],
                'Compression': row[7] if row[0] == "Error" else backup_entry['Compression'],
            })
        elif row[0] and re.search(r"\d{1,2}:\d{2}:\d{2}", row[0]):
            date_str = replace_months(row[0].split(',')[-1].strip())
            backup_entry['Date'] = datetime.strptime(date_str, '%d %B %Y %H:%M:%S').date()
            backup_jobs_list.append(backup_entry)
        elif row[0] and row[0] == "Details":
            details_section = True
        elif row[0] and details_section and row[0] != 'Name':
            details_entry = details_entry_template.copy()
            details_entry.update({
                'Date': backup_entry['Date'],
                'Backup Job': backup_entry['Backup Job'],
                'Object': row[0],
                'Status': row[1],
                'Start Time': row[2],
                'End Time': row[3],
                'Size': row[4],
                'Read': row[5],
                'Transferred': row[6],
                'Duration': row[7]
            })
            details_list.append(details_entry)

    backup_summary, details_summary = pd.DataFrame(backup_jobs_list), pd.DataFrame(details_list)

    backup_summary.sort_values('Date', inplace=True)
    backup_summary.reset_index(drop=True, inplace=True)
    details_summary.sort_values('Date', inplace=True)
    details_summary.reset_index(drop=True, inplace=True)
    return backup_summary, details_summary
