import streamlit as st
from utils.charts import *
import pandas as pd
from utils.data_processing import process_data


st.header("Statistics & Visualizations")

if 'backup_summary' not in st.session_state:
    st.warning(":material/warning: Data file not uploaded yet. Please upload your data file to set parameters.")
    if st.button(":material/arrow_back_ios: Back: Upload file", use_container_width=True):
        st.switch_page('pages/upload_file.py')
else:
    backup_summary_df = st.session_state['backup_summary']
    details_summary_df = st.session_state['details_summary']
    backup_execution_df =  st.session_state['backup_execution']
    last_backup_df = st.session_state['last_backup']
    last_backup_obj_df = st.session_state['last_backup_obj']
    backup_execution_df = st.session_state['backup_execution']

    summary_df = st.session_state['summary']
    summary_recent_df = st.session_state['summary_recent']
    largest_backups = st.session_state['largest_backups']
    smallest_backups = st.session_state['smallest_backups']
    details_df = st.session_state['details']
    merged_counts_df = st.session_state['merged_counts']

    tab_one, tab_two, tab_three = st.tabs(["BACKUP DATA OVERVIEW", "BACKUP SUMMARY", "BACKUP JOB ANALYTICS"])

    with tab_one:
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["Backup Data", "Detailed Data by Object", "Last Backup Data", "Detailed Last Backup Data", "Weekly Execution Results"])

        with tab1:
            st.markdown("#### Backup data")
            st.dataframe(backup_summary_df)
            with open("workbooks/Backup.xlsx", "rb") as file:
                st.download_button(
                    label=":material/download: Download backup data",
                    data=file,
                    file_name="Backup.xlsx",
                    mime="application/vnd.ms-excel",
                    use_container_width=True
                )

        with tab2:
            st.markdown("#### Detailed backup data by object")
            st.dataframe(details_summary_df)
            with open("workbooks/Backup - objects.xlsx", "rb") as file:
                st.download_button(
                    label=":material/download: Download detailed data by object",
                    data=file,
                    file_name="Backup - objects.xlsx",
                    mime="application/vnd.ms-excel",
                    use_container_width=True
                )

        with tab3:
            st.markdown("#### Last backup data")
            st.dataframe(last_backup_df)
            with open("workbooks/Last backup.xlsx", "rb") as file:
                st.download_button(
                    label=":material/download: Download last backup data",
                    data=file,
                    file_name="Last backup.xlsx",
                    mime="application/vnd.ms-excel",
                    use_container_width=True
                )

        with tab4:
            st.markdown("#### Detailed last backup data by object")
            st.dataframe(last_backup_obj_df)
            with open("workbooks/Last backup - objects.xlsx", "rb") as file:
                st.download_button(
                    label=":material/download: Download detailed last backup data",
                    data=file,
                    file_name="Last backup - objects.xlsx",
                    mime="application/vnd.ms-excel",
                    use_container_width=True
                )

        with tab5:
            st.markdown("#### Weekly backup job execution and results")
            st.dataframe(backup_execution_df)
            with open("workbooks/Backup execution.xlsx", "rb") as file:
                st.download_button(
                    label=":material/download: Download weekly execution data",
                    data=file,
                    file_name="Backup execution.xlsx",
                    mime="application/vnd.ms-excel",
                    use_container_width=True
                )

        st.write("... or click the button below to download all data in one Excel file.")
        with open("workbooks/Backup data overview.xlsx", "rb") as file:
            st.download_button(
                label=":material/download: Download all data",
                data=file,
                file_name="Backup data overview.xlsx",
                mime="application/vnd.ms-excel",
                use_container_width=True
            )

    with tab_two:
        col1, col2 = st.columns(2, vertical_alignment="bottom")

        with col1:
            st.markdown("#### Summary of backups")
            st.dataframe(summary_df, hide_index=True, height=393, use_container_width=True)

        with col2:
            st.markdown("#### Summary of recent backups")
            st.dataframe(summary_recent_df, hide_index=True, height=393, use_container_width=True)

        col1, col2 = st.columns([0.65, 0.35], vertical_alignment="bottom")

        with col1:
            st.markdown("#### Largest backups")
            st.dataframe(largest_backups, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("#### Smallest backups")
            st.dataframe(smallest_backups, use_container_width=True, hide_index=True)

        st.markdown("#### Machine backup summary")
        st.dataframe(details_df, use_container_width=True, hide_index=True)

        st.markdown("#### Machine backup error rate")
        st.dataframe(merged_counts_df, use_container_width=True, hide_index=True)

        with open("workbooks/Summary.xlsx", "rb") as file:
            st.download_button(
                label=":material/download: Download backup summary",
                data=file,
                file_name="Summary.xlsx",
                mime="application/vnd.ms-excel",
                use_container_width=True
            )

    with tab_three:
        backup = process_data(backup_summary_df)

        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["Backup job status", "Error rate", "Others", "Performance", "Trends", "Duration", "Gantt chart"])

        with tab1:
            status(backup)
            status_by_backup(backup)
        with tab2:
            error(backup)

            col1, col2 = st.columns(2)

            with col1:
                error_daily(backup)
            with col2:
                error_hour(backup)

        with tab3:
            size(backup)
            efficiency(backup)
            # heatmap(backup)

        with tab4:
            perfomance(backup)

        with tab5:
            daily_trends(backup)
            hour_trends(backup)

        # with tab6:
            # duration_hist(backup)
            # duration_bar(backup)
            # duration_box(backup)
        
        with tab7:
            gantt(backup)