import pandas as pd
from datetime import datetime
    

def convert_to_gb(size):
    if size == "0 B":
        return 0.0
    number, unit = size.split()
    number = float(number.replace(',', '.'))
    unit_conversion = {
        'TB': 1024,
        'GB': 1,
        'MB': 1 / 1024,
        'KB': 1 / (1024 * 1024),
        'B': 1 / (1024 * 1024 * 1024)
    }
    return number * unit_conversion.get(unit, 0)


def apply_to_df(df, columns):
    for column in columns:
        df[f'{column} (GB)'] = df[column].apply(convert_to_gb)
        df.drop([column], axis=1, inplace=True)
    

def remove_x_and_convert(value):
    return float(value.replace('x', '').replace(',', '.'))


def convert(df):
    df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
    df['Start Time'] = pd.to_datetime(df['Start Time'], format='%H:%M:%S')
    df['End Time'] = pd.to_datetime(df['End Time'], format='%H:%M:%S').dt.time
    df['Duration'] = df['Duration'].apply(lambda row: pd.to_timedelta(row.strftime('%H:%M:%S')))


def useful_cols(df):
    df['Hour'] = pd.to_datetime(df['Start Time'], format='%H:%M:%S').dt.hour
    df['Start Datetime'] = df.apply(lambda row: datetime.combine(pd.to_datetime(row['Date']), pd.to_datetime(row['Start Time'], format='%H:%M:%S').time()), axis=1)
    df['End Datetime'] = df.apply(lambda row: datetime.combine(pd.to_datetime(row['Date']), pd.to_datetime(row['End Time'], format='%H:%M:%S').time()), axis=1)

    return df


def process_data(backup_df, obj_df, last_backup_df, last_obj_df):
    backup_copy, obj_copy, last_backup_copy, last_obj_copy = backup_df.copy(), obj_df.copy(), last_backup_df.copy(), last_obj_df.copy()

    convert(backup_copy)
    convert(obj_copy)
    convert(last_backup_copy)
    convert(last_obj_copy)

    apply_to_df(backup_copy, ['Total Size', 'Backup Size', 'Data Read', 'Transferred'])
    apply_to_df(last_backup_copy, ['Total Size', 'Backup Size', 'Data Read', 'Transferred'])
    apply_to_df(obj_copy, ['Size', 'Read', 'Transferred'])
    apply_to_df(last_obj_copy, ['Size', 'Read', 'Transferred'])

    backup_copy['Dedupe'] = backup_copy['Dedupe'].apply(remove_x_and_convert)
    backup_copy['Compression'] = backup_copy['Compression'].apply(remove_x_and_convert)
    last_backup_copy['Dedupe'] = last_backup_copy['Dedupe'].apply(remove_x_and_convert)
    last_backup_copy['Compression'] = last_backup_copy['Compression'].apply(remove_x_and_convert)

    useful_cols(backup_copy)

    return backup_copy, obj_copy, last_backup_copy, last_obj_copy