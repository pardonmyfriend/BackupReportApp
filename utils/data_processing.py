import pandas as pd
from datetime import datetime
import streamlit as st


def convert_to_gb(size):
    if size == "0 B":
        return 0.0
    number, unit = size.split()
    number = float(number.replace(',', '.'))
    if unit == 'TB':
        return number * 1024
    elif unit == 'MB':
        return number / 1024
    elif unit == 'KB':
        return number / (1024 * 1024)
    elif unit == 'B':
        return number / (1024 * 1024 * 1024)
    elif unit == 'GB':
        return number
    else:
        return None
    

def remove_x_and_convert(value):
    return float(value.replace('x', '').replace(',', '.'))


def convert_to_datetime(df):
    df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
    df['Start Time'] = pd.to_datetime(df['Start Time'], format='%H:%M:%S')
    df['End Time'] = pd.to_datetime(df['End Time'], format='%H:%M:%S').dt.time
    df['Duration'] = df['Duration'].apply(lambda x: x.strftime('%H:%M:%S'))
    df['Duration'] = pd.to_timedelta(df['Duration'])


def useful_cols(df):
    df['Hour'] = pd.to_datetime(df['Start Time'], format='%H:%M:%S').dt.hour
    df['Start Datetime'] = df.apply(lambda row: datetime.combine(pd.to_datetime(row['Date']), pd.to_datetime(row['Start Time'], format='%H:%M:%S').time()), axis=1)
    df['End Datetime'] = df.apply(lambda row: datetime.combine(pd.to_datetime(row['Date']), pd.to_datetime(row['End Time'], format='%H:%M:%S').time()), axis=1)


def process_data(df_origin):
    df = df_origin.copy()
    df['Total Size (GB)'] = df['Total Size'].apply(convert_to_gb)
    df['Backup Size (GB)'] = df['Backup Size'].apply(convert_to_gb)
    df['Data Read (GB)'] = df['Data Read'].apply(convert_to_gb)
    df['Transferred (GB)'] = df['Transferred'].apply(convert_to_gb)

    df['Dedupe'] = df['Dedupe'].apply(remove_x_and_convert)
    df['Compression'] = df['Compression'].apply(remove_x_and_convert)

    convert_to_datetime(df)

    useful_cols(df)

    return df