import pandas as pd
import streamlit as st
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment


def load_data(file):
    df_all = pd.read_excel(file, sheet_name='Backup')
    df_all_obj = pd.read_excel(file, sheet_name='Backup - objects', header=None)
    df_last = pd.read_excel(file, sheet_name='Last backup')
    df_last_obj = pd.read_excel(file, sheet_name='Last backup - objects', header=None)
    return df_all, df_all_obj, df_last, df_last_obj

def fill_and_set_columns(df):
    df[0] = df[0].ffill()
    df[1] = df[1].ffill()
    df.columns = df.iloc[0]
    return df[1:]

def convert_columns(df):
    df['Date'] = pd.to_datetime(df['Date'])
    df['Duration'] = pd.to_timedelta(df['Duration'])

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

def generate_summary(df):
    return {
        'Total Backups': len(df),
        'Successful Backups': len(df[df['Status'] == 'Success']),
        'Backups with Warnings': len(df[df['Status'] == 'Warning']),
        'Failed Backups': len(df[df['Status'] == 'Error']),
        'Machines with Failed Backups': df['Error'].sum(),
        'Average Backup Size (GB)': df['Backup Size (GB)'].mean(),
        'Average Backup Duration': df['Duration'].mean(),
        'Average Speed (GB/min)': ((df['Data Read (GB)'] + df['Transferred (GB)']) / (df['Duration'].dt.total_seconds() / 60)).mean(),
        'Average Compression Ratio': df['Compression'].mean(),
        'Average Dedupe Ratio': df['Dedupe'].mean()
    }

def add_summary_to_sheet(sheet, df, start_row, start_col):
    for r_idx, row in enumerate(dataframe_to_rows(df, index=False, header=True), start_row):
        for c_idx, value in enumerate(row, start_col):
            sheet.cell(row=r_idx, column=c_idx, value=value)

def format_headers(sheet, loc):
    sheet.merge_cells(start_row=loc[0], start_column=loc[1], end_row=loc[0], end_column=loc[2])
    cell = sheet.cell(row=loc[0], column=loc[1])
    cell.font = Font(bold=True, color="FFFFFF")
    cell.fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
    cell.alignment = Alignment(horizontal="center", vertical="center")

def format_col_titles(sheet, loc):
    for col in range(loc[1], loc[2] + 1):
        cell = sheet.cell(row=loc[0], column=col)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="A9C3E8", end_color="A9C3E8", fill_type="solid")
        cell.alignment = Alignment(horizontal="center", vertical="center")

def format_borders(sheet, start_row, end_row, start_col, end_col):
    thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
    for row in sheet.iter_rows(min_row=start_row, max_row=end_row, min_col=start_col, max_col=end_col):
        for cell in row:
            cell.border = thin_border

def auto_adjust_column_widths(sheet):
    for column_cells in sheet.columns:
        max_length = 0
        column = None
        for cell in column_cells:
            if cell.value:
                try:
                    column = cell.column_letter
                    cell_length = len(str(cell.value))
                    if cell_length > max_length:
                        max_length = cell_length
                except AttributeError:
                    continue
        if column:
            adjusted_width = max_length + 2
            sheet.column_dimensions[column].width = adjusted_width

def backup_stats():
    df_all, df_all_obj, df_last, df_last_obj = load_data('workbooks/Backup data overview.xlsx')

    df_all_obj = fill_and_set_columns(df_all_obj)
    df_last_obj = fill_and_set_columns(df_last_obj)

    convert_columns(df_all)
    convert_columns(df_all_obj)
    convert_columns(df_last)
    convert_columns(df_last_obj)

    apply_to_df(df_all, ['Total Size', 'Backup Size', 'Data Read', 'Transferred'])
    apply_to_df(df_last, ['Total Size', 'Backup Size', 'Data Read', 'Transferred'])
    apply_to_df(df_all_obj, ['Size', 'Read', 'Transferred'])
    apply_to_df(df_last_obj, ['Size', 'Read', 'Transferred'])

    df_all['Dedupe'] = df_all['Dedupe'].apply(remove_x_and_convert)
    df_all['Compression'] = df_all['Compression'].apply(remove_x_and_convert)
    df_last['Dedupe'] = df_last['Dedupe'].apply(remove_x_and_convert)
    df_last['Compression'] = df_last['Compression'].apply(remove_x_and_convert)

    general_summary = generate_summary(df_all)
    summary_df = pd.DataFrame(list(general_summary.items()), columns=['Metric', 'Value'])

    general_summary_for_recent_backups = generate_summary(df_last)
    summary_recent_df = pd.DataFrame(list(general_summary_for_recent_backups.items()), columns=['Metric', 'Value'])

    df_grouped = df_last_obj.groupby('Object').first().reset_index()
    obj_count = df_all_obj.groupby('Object').size().reset_index(name='Count')

    df_sorted = df_grouped.sort_values(by='Object').reset_index(drop=True)
    obj_count_sorted = obj_count.sort_values(by='Object').reset_index(drop=True)

    details = {
        'Machine': df_sorted['Object'],
        'Last Backup Status': df_sorted['Status'],
        'Total Backups': obj_count_sorted['Count'],
        'Last Backup Date': df_sorted['Date']
    }

    df_details = pd.DataFrame(details)

    total_counts = df_all_obj.groupby('Object').size().reset_index(name='Backup Count')
    error_counts = df_all_obj[df_all_obj['Status'] == 'Error'].groupby('Object').size().reset_index(name='Error Count')
    merged_counts = pd.merge(total_counts, error_counts, on='Object', how='left')
    merged_counts['Error Count'] = merged_counts['Error Count'].fillna(0)
    merged_counts['Error Rate'] = merged_counts['Error Count'] / merged_counts['Backup Count']
    merged_counts.rename(columns={'Object': 'Machine'}, inplace=True)
    merged_counts = merged_counts[['Machine', 'Error Rate']].sort_values(by='Error Rate', ascending=False)

    largest_backups = df_all.nlargest(3, 'Backup Size (GB)')[['Backup Job', 'Backup Size (GB)']]
    df_no_error = df_all[df_all['Status'] != 'Error']
    smallest_backups = df_no_error.nsmallest(3, 'Backup Size (GB)')[['Backup Job', 'Backup Size (GB)']]

    wb = load_workbook('workbooks/Backup data overview.xlsx')
    if 'Summary' in wb.sheetnames:
        std = wb['Summary']
        wb.remove(std)
    ws = wb.create_sheet(title='Summary')

    ws['A1'] = "General Summary of Backups"
    add_summary_to_sheet(ws, summary_df, 2, 1)
    ws['D1'] = "General Summary of Recent Backups"
    add_summary_to_sheet(ws, summary_recent_df, 2, 4)
    ws[f'A{len(summary_df) + 4}'] = "Largest Backups"
    add_summary_to_sheet(ws, largest_backups, len(summary_df) + 5, 1)
    ws[f'D{len(summary_df) + 4}'] = "Smallest Backups"
    add_summary_to_sheet(ws, smallest_backups, len(summary_df) + 5, 4)
    ws[f'A{len(summary_df) + len(largest_backups) + 7}'] = "Machine Backup Summary"
    add_summary_to_sheet(ws, df_details, len(summary_df) + len(largest_backups) + 8, 1)
    ws[f'A{len(summary_df) + len(largest_backups) + len(df_details) + 10}'] = "Machine Backup Error Rate"
    add_summary_to_sheet(ws, merged_counts, len(summary_df) + len(largest_backups) + len(df_details) + 11, 1)

    st.session_state['summary'] = summary_df
    st.session_state['summary_recent'] = summary_recent_df
    st.session_state['largest_backups'] = largest_backups
    st.session_state['smallest_backups'] = smallest_backups
    st.session_state['details'] = df_details
    st.session_state['merged_counts'] = merged_counts

    header_locs = [[1, 1, 2], [1, 4, 5], [14, 1, 2], [14, 4, 5], [20, 1, 4], [len(df_details) + 23, 1, 2]]
    col_locs = [[2, 1, 2], [2, 4, 5], [15, 1, 2], [15, 4, 5], [21, 1, 4], [len(df_details) + 24, 1, 2]]
    border_locs = [
        (1, 12, 1, 2), (1, 12, 4, 5),
        (14, 18, 1, 2), (14, 18, 4, 5),
        (20, len(df_details) + 21, 1, 4),
        (len(df_details) + 23, 2 * len(df_details) + 24, 1, 2)
    ]

    for loc in header_locs:
        format_headers(ws, loc)
    for loc in col_locs:
        format_col_titles(ws, loc)
    for loc in border_locs:
        format_borders(ws, *loc)

    auto_adjust_column_widths(ws)

    wb.save('workbooks/Backup data overview.xlsx')
