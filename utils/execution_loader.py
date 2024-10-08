import re
import pandas as pd
from datetime import datetime
from utils.backup_loader import replace_months
from dateutil import parser
import streamlit as st


def merge_retry_rows(df):
    backup_columns = df.columns[4:]
    rows_to_remove = []

    for i, row in df.iterrows():
        backup_job = row['Backup Job']

        for col1 in backup_columns:
            if pd.notna(row[col1]):
                break
            else:
                for col2 in backup_columns:
                    if pd.notna(row[col2]):
                        for j in range(i - 1, -1, -1):
                            if df.loc[j, 'Backup Job'] == backup_job and pd.isna(df.loc[j, col2]):
                                df.loc[j, col2] = row[col2]
                                df.loc[j, 'Status'] = row['Status']
                                rows_to_remove.append(i)
                                break
    df = df.drop(rows_to_remove).reset_index(drop=True)
    return df


def get_backup_execution(sheet):
    backup_jobs = []
    current_job = None
    week_num = 1
    current_entry = None
    retry_num = None

    for row in sheet.iter_rows(values_only=True):
        if row[0] and "Backup job" in row[0]:
            status = row[8]
            if "Retry" in row[0]:
                match = re.search(r'Backup job: (.*?) \(Retry (\d+)\)', row[0])
                if match:
                    current_job = match.group(1)
                    retry_num = int(match.group(2))
            else:
                current_job = row[0].split("Backup job: ")[1].strip()
            current_entry = {
                'Month': None,
                'Date': None,
                'Week Number': None,
                'Day of Week': None,
                'Backup Job': current_job,
                'Status': status
            }
        elif row[0] and re.search(r"\d{1,2}:\d{2}:\d{2}", row[0]):
            date_str = replace_months(row[0].split(',')[-1].strip())

            try:
                parsed_date = parser.parse(date_str, dayfirst=True)
                current_entry['Date'] = parsed_date

                month_first_day = current_entry['Date'].replace(day=1)
                days_from_first_monday = (current_entry['Date'] - month_first_day).days + month_first_day.weekday()
                week_num = days_from_first_monday // 7 + 1

                month = current_entry['Date'].month
                current_entry['Month'] = month
                current_entry['Week Number'] = week_num
                current_entry['Day of Week'] = current_entry['Date'].strftime('%A')
                current_entry['Date'] = current_entry['Date'].date()
            except ValueError:
                continue

        elif row[3] and row[2] == "Start time" and row[3] != "End time":
            start_time = row[3]
            if retry_num is None:
                current_entry['Backup'] = start_time
            else:
                current_entry[f'Backup (Retry {retry_num})'] = start_time
                retry_num = None
            backup_jobs.append(current_entry)
            current_entry = {
                'Month': None,
                'Date': None,
                'Week Number': None,
                'Day of Week': None,
                'Backup Job': current_job,
                'Status': None
            }

    df = pd.DataFrame(backup_jobs)

    st.dataframe(df)

    df = df.dropna(subset=df.columns[:7]).reset_index(drop=True)

    st.dataframe(df)

    for row in range(len(df)):
        for col in df.columns[6:]:
            if pd.notna(df.loc[row, col]):
                date = pd.to_datetime(df.at[row, 'Date'])
                time = pd.to_datetime(df.at[row, col], format='%H:%M:%S').time()
                df.at[row, 'Start Datetime'] = datetime.combine(date, time)

    retry_columns = sorted([col for col in df.columns if re.match(r'Backup \(Retry \d+\)', col)], key=lambda x: int(re.search(r'\d+', x).group()))
    sorted_columns = ['Month', 'Week Number', 'Day of Week', 'Start Datetime', 'Backup Job', 'Backup'] + retry_columns + ['Status']

    df = df[sorted_columns]

    return df


def combine_exec(dfs):
    df_combined = pd.concat(dfs)
    df_combined.drop_duplicates(inplace=True)
    df_combined.sort_values('Start Datetime', inplace=True)
    df_combined.drop(['Start Datetime'], axis=1, inplace=True)
    df_combined.reset_index(drop=True, inplace=True)

    return df_combined