import streamlit as st
from openpyxl import load_workbook
import locale
from utils.data_loader import report_summary
from utils.last_backup import get_last_backups
from utils.job_objects import get_job_objects
from utils.backup_execution import get_backup_execution
from utils.df_to_excel import create_excels


locale.setlocale(locale.LC_TIME, 'pl_PL.UTF-8')

st.header("Upload file")

if 'backup_summary' in st.session_state:
    st.success(":material/task_alt: You've already loaded your file! Review the data below.")
    backup_summary_df = st.session_state['backup_summary']
    details_summary_df = st.session_state['details_summary']

    tab1, tab2 = st.tabs(['Backup data', 'Detailed backup data by object'])
    tab1.dataframe(backup_summary_df)
    tab2.dataframe(details_summary_df)

    if st.button(f'Next step: Adjust parameters :material/arrow_forward_ios:' , use_container_width=True):
        st.switch_page("pages/params.py")
else:
    uploaded_file = st.file_uploader("Choose Excel file with Veeam report", type=["xlsx"])
    if uploaded_file is not None:
        with st.spinner("Uploading..."):
            workbook = load_workbook(uploaded_file)
            worksheet = workbook['Arkusz1']
            backup_summary_df, details_summary_df = report_summary(worksheet)
            last_backup_df, last_backup_obj_df = get_last_backups(backup_summary_df, details_summary_df)
            job_obj = get_job_objects(backup_summary_df, details_summary_df)
            backup_execution_df = get_backup_execution(worksheet)

            st.session_state['backup_summary'] = backup_summary_df
            st.session_state['details_summary'] = details_summary_df
            st.session_state['last_backup'] = last_backup_df
            st.session_state['last_backup_obj'] = last_backup_obj_df
            st.session_state['job_obj'] = job_obj
            st.session_state['min_date'] = backup_summary_df.loc[0, 'Date']
            st.session_state['max_date'] = backup_summary_df.iloc[-1]['Date']
            st.session_state['backup_execution'] = backup_execution_df

            create_excels(backup_summary_df, details_summary_df, last_backup_df, last_backup_obj_df, backup_execution_df)
        st.success(":material/task_alt: File successfully loaded! Review the data below.")

        tab1, tab2 = st.tabs(['Backup data', 'Detailed backup data by object'])
        tab1.dataframe(backup_summary_df)
        tab2.dataframe(details_summary_df)

        if st.button(f'Next step: Adjust parameters :material/arrow_forward_ios:' , use_container_width=True):
            st.switch_page("pages/params.py")