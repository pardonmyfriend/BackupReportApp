import streamlit as st
from utils.params_tools import *
from datetime import timedelta, date
import calendar


st.header("Parameters")

if 'uploaded_backup' not in st.session_state:
    st.warning("Data file not uploaded yet. Please upload a data file to adjust the parameters.", icon=":material/warning:")
    if st.button(":material/arrow_back_ios: Back: Upload file", use_container_width=True):
        st.switch_page('my_pages/file_upload.py')
else:
    if 'params_reset' in st.session_state and st.session_state['params_reset']:
        del st.session_state['params_reset']
        del st.session_state['params_just_saved']
        del st.session_state['selected_date_range']
        del st.session_state['selected_job_obj']

        st.info("Paremeters has been reset. You can now adjust the parameters again.", icon=":material/info:")

    if 'selected_date_range' in st.session_state and 'selected_job_obj' in st.session_state:
        if 'params_just_saved' in st.session_state and st.session_state['params_just_saved']:
            st.success("Parameters successfully saved! Proceed to view the results.", icon=":material/task_alt:")

        if 'params_just_saved' in st.session_state and not st.session_state['params_just_saved']:
            st.info("You've already adjusted parameters. Proceed to view the results.", icon=":material/info:")

        st.session_state['params_just_saved'] = False

        selected_date_range = st.session_state['selected_date_range']
        job_obj = st.session_state['selected_job_obj']

        with st.expander("Selected date range"):
            st.write(f"{selected_date_range[0].strftime("%d.%m")} - {selected_date_range[1].strftime("%d.%m")}")

        with st.expander("Selected backup jobs and VMs"):
            for job in job_obj:
                machines = job_obj[job]
                st.write(f"* **{job}**: {', '.join(machines)}")

        if st.button(f'Reset params', use_container_width=True):
            st.session_state['params_reset'] = True
            st.rerun()
        
        if st.button(f'Next step: View results :material/arrow_forward_ios:' , use_container_width=True, type='primary'):
            st.switch_page("my_pages/dashboard.py")
    else:
        execution_df = st.session_state['uploaded_execution']

        year = st.session_state['year']
        min_date = st.session_state['min_date']
        max_date = st.session_state['max_date']

        st.markdown("#### Date selection")
        option = st.radio("Select the date selection method", ["Date range", "Month and week", "Day range in month", "Predefined date ranges"])

        if option == "Date range":
            selected_date_range = st.date_input(
                "Select the date range for analysis",
                (min_date, max_date),
                min_date,
                max_date,
                format="DD.MM.YYYY"
                )
            
        elif option == "Month and week":
            month_week = get_month_week(execution_df)

            c1, c2 = st.columns(2)

            selected_month = c1.selectbox(
                "Select month", 
                month_week.keys(), 
                format_func=lambda x: calendar.month_name[x])

            selected_week = c2.selectbox(
                "Select week", 
                month_week[selected_month], 
                format_func=lambda x: f"Week {x}: {get_week_dates(year, selected_month, x)[0].strftime('%d.%m')} - {get_week_dates(year, selected_month, x)[1].strftime('%d.%m')}"
                )
                
            selected_date_range = get_week_dates(year, selected_month, selected_week)

        elif option == "Day range in month":
            months = get_month_week(execution_df).keys()

            c1, c2, c3 = st.columns(3)

            selected_month = c1.selectbox("Select month", months, format_func=lambda x: calendar.month_name[x])

            min_day, max_day = get_days_for_month(year, selected_month, min_date, max_date)

            start_day = c2.number_input("Start day", min_day, max_day, min_day)
            end_day = c3.number_input("End day", start_day, max_day, max_day)

            selected_date_range = (date(year, selected_month, start_day), date(year, selected_month, end_day))
        
        elif option == "Predefined date ranges":
            year = st.session_state['year']
            month_week = get_month_week(execution_df)
            month_week_tuples = [(key, element) for key, values in month_week.items() for element in values]

            c1, c2 = st.columns([3, 1], vertical_alignment="bottom")

            predefined_option = c1.selectbox("Quick select a date range", ["Last week", "Last 2 weeks", "Last 3 weeks", "Last 4 weeks", "Last month"])

            if predefined_option == "Last week":
                last_week = month_week_tuples[-1]
                selected_date_range = get_week_dates(year, last_week[0], last_week[1])
                
            elif predefined_option == "Last 2 weeks":
                last_2_weeks = month_week_tuples[-2:]
                end_date = get_week_dates(year, last_2_weeks[1][0], last_2_weeks[1][1])
                start_date = end_date[0] - timedelta(days=7)
                end_date = end_date[1]
                selected_date_range = (start_date, end_date)

            elif predefined_option == "Last 3 weeks":
                last_3_weeks = month_week_tuples[-3:]
                end_date = get_week_dates(year, last_3_weeks[2][0], last_3_weeks[2][1])
                start_date = end_date[0] - timedelta(days=14)
                end_date = end_date[1]
                selected_date_range = (start_date, end_date)
            
            elif predefined_option == "Last 4 weeks":
                last_4_weeks = month_week_tuples[-4:]
                end_date = get_week_dates(year, last_4_weeks[3][0], last_4_weeks[3][1])
                start_date = end_date[0] - timedelta(days=21)
                end_date = end_date[1]
                selected_date_range = (start_date, end_date)
            
            elif predefined_option == "Last month":
                last_month = list(month_week.items())[-1]
                start_date = get_week_dates(year, last_month[0], last_month[1][0])[0]
                end_date = get_week_dates(year, last_month[0], last_month[1][-1])[1]
                selected_date_range = (start_date, end_date)

            c2.write(f"{selected_date_range[0].strftime("%d.%m")} - {selected_date_range[1].strftime("%d.%m")}")


        st.markdown("#### Backup job and virtual machines selection")
        job_obj = st.session_state['job_obj']

        selected_job_obj = {}

        container = st.container()
        all = st.checkbox("Select all", value=True)

        with container:
            with st.expander("Select backup jobs"):
                if all:
                    selected_jobs = st.multiselect("Select backup jobs", options=job_obj.keys(), default=job_obj.keys())
                else:
                    selected_jobs = st.multiselect("Select backup jobs", options=job_obj.keys())

            with st.expander("Select virtual machines"):
                if all:
                    for job in selected_jobs:
                        selected_job_obj[job] = st.multiselect(f"Select machines from {job}", options=job_obj[job], default=job_obj[job])
                else:
                    if not selected_jobs:
                        st.write("No backup job selected")
                    else:
                        for job in selected_jobs:
                            selected_job_obj[job] = st.multiselect(f"Select machines from {job}", options=job_obj[job], default=job_obj[job])

        backup_df = st.session_state['uploaded_backup']
        obj_df = st.session_state['uploaded_obj']

        start_date = selected_date_range[0]
        end_date = selected_date_range[1]
        backup_df = backup_df[(backup_df['Date'] >= start_date) & (backup_df['Date'] <= end_date)]
        obj_df = obj_df[(obj_df['Date'] >= start_date) & (obj_df['Date'] <= end_date)]

        obj_df = obj_df[obj_df.apply(lambda row: row['Object'] in selected_job_obj.get(row['Backup Job'], []), axis=1)]
        unique_pairs = obj_df[['Date', 'Backup Job']].drop_duplicates()
        backup_df = backup_df[backup_df.set_index(['Date', 'Backup Job']).index.isin(unique_pairs.set_index(['Date', 'Backup Job']).index)]
        
        if backup_df.empty or obj_df.empty:
            btn = st.button(f'Save', use_container_width=True, help=":material/warning: No data available for the selected parameters. Please change the date range or select different backup jobs.", disabled=True)
        else:
            if st.button(f'Save', use_container_width=True):
                st.session_state['backup'] = backup_df
                st.session_state['obj'] = obj_df
                st.session_state['execution'] = execution_df[execution_df['Backup Job'].isin(selected_job_obj.keys())]

                st.session_state['selected_date_range'] = selected_date_range
                st.session_state['selected_job_obj'] = selected_job_obj
                st.session_state['params_just_saved'] = True
                st.rerun()
