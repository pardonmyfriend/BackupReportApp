import streamlit as st
from utils.charts import *
from utils.data_processing import process_data
from utils.df_to_excel import create_excels
from utils.backup_loader import get_last_backups
from utils.stats import stats


@st.cache_data
def get_last_backups_cached(backup_df, obj_df):
    return get_last_backups(backup_df, obj_df)


@st.cache_data
def stats_cached(backup_df, obj_df, last_backup_df, last_obj_df):
    return stats(backup_df, obj_df, last_backup_df, last_obj_df)


@st.cache_data
def process_data_cached(backup_df, obj_df, last_backup_df, last_obj_df):
    return process_data(backup_df, obj_df, last_backup_df, last_obj_df)


@st.cache_data
def create_excels_cached(backup_df, obj_df, last_backup_df, last_obj_df, execution_df, summary_df, summary_recent_df, largest_backups_df, smallest_backups_df, details_df, merged_counts_df):
    create_excels(backup_df, obj_df, last_backup_df, last_obj_df, execution_df, summary_df, summary_recent_df, largest_backups_df, smallest_backups_df, details_df, merged_counts_df)


@st.cache_data
def generate_all_charts_cached(backup, obj):
    return generate_all_charts(backup, obj)


def highlight_error(row):
    if row['Status'] == 'Error':
        return ['background-color: rgba(255, 99, 71, 0.3)'] * len(row)
    if row['Status'] == 'Warning':
        return ['background-color: rgba(255, 165, 0, 0.3)'] * len(row)
    else:
        return [''] * len(row)


st.header("Statistics & Visualizations")

if 'uploaded_backup' not in st.session_state:
    st.warning("Data file not uploaded yet. Please upload a data file to view the results.", icon=":material/warning:")
    if st.button(":material/arrow_back_ios: Back: Upload file", use_container_width=True):
        st.switch_page('my_pages/file_upload.py')
else:
    if 'selected_date_range' not in st.session_state or 'selected_job_obj' not in st.session_state:
        st.warning("Parameters not adjusted yet. Please adjust the parameters to view the results.", icon=":material/warning:")
        if st.button(":material/arrow_back_ios: Back: Adjust parameters", use_container_width=True):
            st.switch_page('my_pages/params.py')
    else:
        with st.spinner("Loading..."):
            backup_df = st.session_state['backup']
            obj_df = st.session_state['obj']
            execution_df =  st.session_state['execution']
            selected_job_obj = st.session_state['selected_job_obj']

            last_backup_df, last_obj_df = get_last_backups_cached(st.session_state['uploaded_backup'], st.session_state['uploaded_obj'])

            last_obj_df = last_obj_df[last_obj_df.apply(lambda row: row['Object'] in selected_job_obj.get(row['Backup Job'], []), axis=1)]
            unique_pairs = last_obj_df[['Date', 'Backup Job']].drop_duplicates()
            last_backup_df = last_backup_df[last_backup_df.set_index(['Date', 'Backup Job']).index.isin(unique_pairs.set_index(['Date', 'Backup Job']).index)]

            backup, obj, last_backup, last_obj = process_data_cached(backup_df, obj_df, last_backup_df, last_obj_df)

            summary_df, summary_recent_df, largest_backups_df, smallest_backups_df, details_df, merged_counts_df = stats_cached(backup, obj, last_backup, last_obj)

            create_excels_cached(backup_df, obj_df, last_backup_df, last_obj_df, execution_df, summary_df, summary_recent_df, largest_backups_df, smallest_backups_df, details_df, merged_counts_df)

            charts = generate_all_charts_cached(backup, obj)

        tab_one, tab_two, tab_three, tab_four = st.tabs(["BACKUP DATA OVERVIEW", "BACKUP SUMMARY", "BACKUP ANALYTICS BY JOB", "BACKUP ANALYTICS BY OBJECT"])

        with tab_one:
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["Backup Data", "Backup Data by Object", "Last Backup Data", "Last Backup Data by Object", "Weekly Execution Results"])

            with tab1:
                st.markdown("#### Backup data")
                st.dataframe(backup_df.astype(str), use_container_width=True)
                with open("workbooks/Backup.xlsx", "rb") as file:
                    st.download_button(
                        label=":material/download: Download backup data",
                        data=file,
                        file_name="Backup.xlsx",
                        mime="application/vnd.ms-excel",
                        use_container_width=True
                    )

            with tab2:
                st.markdown("#### Backup data by object")
                st.dataframe(obj_df.astype(str), use_container_width=True)
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
                styled_df = last_backup_df.astype(str).style.apply(highlight_error, axis=1)
                st.dataframe(styled_df, use_container_width=True)
                with open("workbooks/Last backup.xlsx", "rb") as file:
                    st.download_button(
                        label=":material/download: Download last backup data",
                        data=file,
                        file_name="Last backup.xlsx",
                        mime="application/vnd.ms-excel",
                        use_container_width=True
                    )

            with tab4:
                st.markdown("#### Last backup data by object")
                styled_df = last_obj_df.astype(str).style.apply(highlight_error, axis=1)
                st.dataframe(styled_df, use_container_width=True)
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
                styled_df = execution_df.fillna("").astype(str).style.apply(highlight_error, axis=1)
                st.dataframe(styled_df, use_container_width=True)
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
                st.dataframe(summary_df.astype(str), hide_index=True, height=393, use_container_width=True)

            with col2:
                st.markdown("#### Summary of recent backups")
                st.dataframe(summary_recent_df.astype(str), hide_index=True, height=393, use_container_width=True)

            col1, col2 = st.columns(2, vertical_alignment="bottom")

            with col1:
                st.markdown("#### Largest backups")
                st.dataframe(largest_backups_df, use_container_width=True, hide_index=True)
            
            with col2:
                st.markdown("#### Smallest backups")
                st.dataframe(smallest_backups_df, use_container_width=True, hide_index=True)

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
            tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs(["Status", "Error rate", "Total size", "Backup size", "Duration", "Speed", "Performance", "Reduction efficiency", "Gantt chart"])

            with tab1:
                st.plotly_chart(charts['status'], use_container_width=True)
                st.plotly_chart(charts['status_by_backup'], use_container_width=True)
                
            with tab2:
                st.plotly_chart(charts['error'], use_container_width=True)

                col1, col2 = st.columns(2)

                with col1:
                    st.plotly_chart(charts['error_daily'], use_container_width=True)
                with col2:
                    st.plotly_chart(charts['error_hour'], use_container_width=True)

            with tab3:
                st.plotly_chart(charts['avg_total'], use_container_width=True)
                st.plotly_chart(charts['size'], use_container_width=True)

                col1, col2 = st.columns(2)

                with col1:
                    st.plotly_chart(charts['total_daily_trends'], use_container_width=True)
                with col2:
                    st.plotly_chart(charts['total_hourly_trends'], use_container_width=True)

            with tab4:
                st.plotly_chart(charts['avg_backup'], use_container_width=True)
                st.plotly_chart(charts['heatmap'], use_container_width=True)

                col1, col2 = st.columns(2)

                with col1:
                    st.plotly_chart(charts['backup_daily_trends'], use_container_width=True)
                with col2:
                    st.plotly_chart(charts['backup_hourly_trends'], use_container_width=True)

            with tab5:
                st.plotly_chart(charts['avg_duration'], use_container_width=True)

                col1, col2 = st.columns(2)

                with col1:
                    st.plotly_chart(charts['duration_daily_trends'], use_container_width=True)
                with col2:
                    st.plotly_chart(charts['duration_hourly_trends'], use_container_width=True)

                st.plotly_chart(charts['duration_hist'], use_container_width=True)
                st.plotly_chart(charts['duration_box'], use_container_width=True)

            with tab6:
                st.plotly_chart(charts['avg_speed'], use_container_width=True)
                st.plotly_chart(charts['backup_speed'], use_container_width=True)
                st.plotly_chart(charts['speed_hist'], use_container_width=True)
                st.plotly_chart(charts['speed_box'], use_container_width=True)
                st.plotly_chart(charts['speed_heatmap'], use_container_width=True)

            with tab7:
                for fig in charts['performance']:
                    st.plotly_chart(fig, use_container_width=True)

            with tab8:
                st.plotly_chart(charts['dedupe_efficiency'], use_container_width=True)
                st.plotly_chart(charts['compression_efficiency'], use_container_width=True)

            with tab9:
                st.plotly_chart(charts['gantt'], use_container_width=True)

        with tab_four:
            tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["Status", "Error rate", "Total size", "Duration", "Speed", "Performance", "Reduction efficiency"])

            with tab1:
                st.plotly_chart(charts['status_obj'], use_container_width=True)
                st.plotly_chart(charts['status_by_obj'], use_container_width=True)

            with tab2:
                st.plotly_chart(charts['error_obj'], use_container_width=True)

            with tab3:
                st.plotly_chart(charts['avg_total_obj'], use_container_width=True)
                st.plotly_chart(charts['size_obj'], use_container_width=True)

            with tab4:
                st.plotly_chart(charts['avg_duration_obj'], use_container_width=True)
                st.plotly_chart(charts['duration_hist_obj'], use_container_width=True)
                st.plotly_chart(charts['duration_box_obj'], use_container_width=True)

            with tab5:
                st.plotly_chart(charts['avg_speed_obj'], use_container_width=True)
                st.plotly_chart(charts['backup_speed_obj'], use_container_width=True)
                st.plotly_chart(charts['speed_hist_obj'], use_container_width=True)
                st.plotly_chart(charts['speed_box_obj'], use_container_width=True)

            with tab6:
                for fig in charts['perfomance_obj']:
                    st.plotly_chart(fig, use_container_width=True)

            with tab7:
                st.plotly_chart(charts['efficiency_obj'], use_container_width=True)