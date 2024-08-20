import streamlit as st
from openpyxl import load_workbook
import locale
from utils.backup_loader import report_summary, get_last_backups, get_job_objects, combine
from utils.execution_loader import get_backup_execution, merge_retry_rows, combine_exec
from utils.df_to_excel import create_excels


locale.setlocale(locale.LC_TIME, "pl_PL")

st.header("Upload file")

files = st.file_uploader("Choose Excel file with Veeam report", type=["xlsx"], accept_multiple_files=True)
if files:
    with st.spinner("Uploading..."):
        backup_list = []
        obj_list = []
        execution_list = []
        for file in files:
            workbook = load_workbook(file)
            worksheet = workbook['Arkusz1']
            backup, obj = report_summary(worksheet)
            backup_list.append(backup)
            obj_list.append(obj)
            execution_list.append(get_backup_execution(worksheet))

        backup_df = combine(backup_list)
        obj_df = combine(obj_list)
        execution_df = merge_retry_rows(combine_exec(execution_list))
        last_backup_df, last_obj_df = get_last_backups(backup_df, obj_df)
        job_obj = get_job_objects(backup_df, obj_df)

        st.session_state['backup'] = backup_df
        st.session_state['obj'] = obj_df
        st.session_state['last_backup'] = last_backup_df
        st.session_state['last_obj'] = last_obj_df
        st.session_state['job_obj'] = job_obj
        st.session_state['min_date'] = backup_df.loc[0, 'Date']
        st.session_state['max_date'] = backup_df.iloc[-1]['Date']
        st.session_state['execution'] = execution_df

        create_excels(backup_df, obj_df, last_backup_df, last_obj_df, execution_df)
    st.success(":material/task_alt: File successfully loaded! Review the data below.")

    tab1, tab2 = st.tabs(['Backup data', 'Detailed backup data by object'])
    tab1.dataframe(backup_df)
    tab2.dataframe(obj_df)

    if st.button(f'Next step: Adjust parameters :material/arrow_forward_ios:' , use_container_width=True):
        st.switch_page("pages/params.py")
else:
    if 'backup' in st.session_state:
        st.success(":material/task_alt: You've already loaded your file! Review the data below.")
        backup_df = st.session_state['backup']
        obj_df = st.session_state['obj']

        tab1, tab2 = st.tabs(['Backup data', 'Detailed backup data by object'])
        tab1.dataframe(backup_df)
        tab2.dataframe(obj_df)

        if st.button(f'Next step: Adjust parameters :material/arrow_forward_ios:' , use_container_width=True):
            st.switch_page("pages/params.py")