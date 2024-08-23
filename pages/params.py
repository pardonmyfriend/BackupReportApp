import streamlit as st
from utils.params_tools import *
from datetime import datetime, timedelta, date
import calendar

st.header("Adjust parameters")

if 'backup' not in st.session_state:
    st.warning(":material/warning: Data file not uploaded yet. Please upload your data file to set parameters.")
    if st.button(":material/arrow_back_ios: Back: Upload file", use_container_width=True):
        st.switch_page('pages/upload_file.py')
else:
    backup = st.session_state['backup']
    obj = st.session_state['obj']
    last_backup = st.session_state['last_backup']
    last_obj = st.session_state['last_obj']
    execution = st.session_state['execution']

    year = st.session_state['year']
    min_date = st.session_state['min_date']
    max_date = st.session_state['max_date']

    st.markdown("#### Date selection")
    option = st.radio("Select the date selection method", ["Date range", "Month and week", "Day range in month", "Predefined date ranges"])

    if option == "Date range":
        date_range = st.date_input(
            "Select the date range for analysis",
            (min_date, max_date),
            min_date,
            max_date,
            format="DD.MM.YYYY"
            )
    elif option == "Month and week":
        month_week = get_month_week(execution)

        col1, col2 = st.columns(2)

        with col1:
            selected_month = st.selectbox(
                "Select month", 
                month_week.keys(), 
                format_func=lambda x: calendar.month_name[x])

        with col2:
            selected_week = st.selectbox(
                "Select week", 
                month_week[selected_month], 
                format_func=lambda x: f"Week {x}: {get_week_dates(year, selected_month, x)[0].strftime('%d.%m')} - {get_week_dates(year, selected_month, x)[1].strftime('%d.%m')}"
                )
            
        date_range = get_week_dates(year, selected_month, selected_week)
    elif option == "Day range in month":
        months = get_month_week(execution).keys()

        col1, col2, col3 = st.columns(3)

        with col1:
            selected_month = st.selectbox("Select month", months, format_func=lambda x: calendar.month_name[x])

        min_day, max_day = get_days_for_month(year, selected_month, min_date, max_date)

        with col2:
            start_day = st.number_input("Start day", min_day, max_day, min_day)

        with col3:
            end_day = st.number_input("End day", start_day, max_day, max_day)

        # day_range = st.slider(
        #     f"Select the range of days in {datetime(year, selected_month, 1).strftime('%B')}",
        #     min_value=min_day,
        #     max_value=max_day,
        #     value=(min_day, max_day)
        # )

        # date_range = (date(year, selected_month, day_range[0]), date(year, selected_month, day_range[1]))
        # st.write(f"Selected date range: {day_range[0]:02d}.{selected_month:02d} - {day_range[1]:02d}.{selected_month:02d}")

        date_range = (date(year, selected_month, start_day), date(year, selected_month, end_day))
        st.write(f"Selected range: {date_range[0].strftime("%d.%m")} - {date_range[1].strftime("%d.%m")}")
    elif option == "Predefined date ranges":
        year = st.session_state['year']
        month_week = get_month_week(execution)
        month_week_tuples = [(key, element) for key, values in month_week.items() for element in values]

        predefined_option = st.selectbox("Quick select a date range", ["Last week", "Last 2 weeks", "Last 3 weeks", "Last 4 weeks", "Last month"])

        if predefined_option == "Last week":
            last_week = month_week_tuples[-1]
            date_range = get_week_dates(year, last_week[0], last_week[1])
            st.write(f"Selected range: {date_range[0].strftime("%d.%m")} - {date_range[1].strftime("%d.%m")}")
            
        elif predefined_option == "Last 2 weeks":
            last_2_weeks = month_week_tuples[-2:]
            end_date = get_week_dates(year, last_2_weeks[1][0], last_2_weeks[1][1])
            start_date = end_date[0] - timedelta(days=7)
            end_date = end_date[1]
            date_range = (start_date, end_date)
            st.write(f"Selected range: {date_range[0].strftime("%d.%m")} - {date_range[1].strftime("%d.%m")}")

        elif predefined_option == "Last 3 weeks":
            last_3_weeks = month_week_tuples[-3:]
            end_date = get_week_dates(year, last_3_weeks[2][0], last_3_weeks[2][1])
            start_date = end_date[0] - timedelta(days=14)
            end_date = end_date[1]
            date_range = (start_date, end_date)
            st.write(f"Selected range: {date_range[0].strftime("%d.%m")} - {date_range[1].strftime("%d.%m")}")
        
        elif predefined_option == "Last 4 weeks":
            last_4_weeks = month_week_tuples[-4:]
            end_date = get_week_dates(year, last_4_weeks[3][0], last_4_weeks[3][1])
            start_date = end_date[0] - timedelta(days=21)
            end_date = end_date[1]
            date_range = (start_date, end_date)
            st.write(f"Selected range: {date_range[0].strftime("%d.%m")} - {date_range[1].strftime("%d.%m")}")
        
        elif predefined_option == "Last month":
            last_month = list(month_week.items())[-1]
            start_date = get_week_dates(year, last_month[0], last_month[1][0])[0]
            end_date = get_week_dates(year, last_month[0], last_month[1][-1])[1]
            date_range = (start_date, end_date)
            st.write(f"Selected range: {date_range[0].strftime("%d.%m")} - {date_range[1].strftime("%d.%m")}")


    st.markdown("#### Backup job and virtual machines selection")
    job_obj = st.session_state['job_obj']

    if 'job_list' not in st.session_state:
        st.session_state['job_list'] = []
    
    if 'obj_list' not in st.session_state:
        st.session_state['obj_list'] = []

    if 'selected_job_obj' not in st.session_state:
        st.session_state['selected_job_obj'] = {}

    if 'all_job_selected' not in st.session_state:
        st.session_state['all_job_selected'] = False

    if 'all_job_obj_selected' not in st.session_state:
        st.session_state['all_job_obj_selected'] = False

    col1, col2 = st.columns([0.79, 0.21], vertical_alignment="bottom")

    with col2:
        if st.button("Select all" if not st.session_state['all_job_selected'] else "Clear all", key="job_btn", use_container_width=True):
            if st.session_state['all_job_selected']:
                st.session_state['all_job_selected'] = False
                st.session_state['all_job_obj_selected'] = False
                st.session_state['job_list'] = []
                st.session_state['selected_job_obj'] = {}
            else:
                st.session_state['all_job_selected'] = True
                st.session_state['job_list'] = job_obj.keys()
                # for job in st.session_state['job_list']:
                #     st.session_state['selected_job_obj'][job] = st.session_state['selected_job_obj'][job] if job in st.session_state['selected_job_obj'].keys() else []
            st.rerun()

    with col1:
        with st.expander("Select backup jobs"):
            job_list = st.session_state['job_list']
            st.session_state['job_list'] = st.multiselect("Select backup jobs", options=job_obj.keys(), default=st.session_state['job_list'])
            for job in st.session_state['job_list']:
                st.session_state['selected_job_obj'][job] = st.session_state['selected_job_obj'][job] if job in st.session_state['selected_job_obj'].keys() else []
            if job_list != st.session_state['job_list']:
                st.rerun()

    col3, col4 = st.columns([0.79, 0.21], vertical_alignment="bottom")

    with col4:
        if st.button("Select all" if not st.session_state['all_job_obj_selected'] else "Clear all", key="job_obj_btn", disabled=not st.session_state['job_list'], use_container_width=True):
            if st.session_state['all_job_obj_selected']:
                st.session_state['all_job_obj_selected'] = False
                st.session_state['obj_list'] = []
                st.session_state['selected_job_obj'] = {}
            else:
                st.session_state['all_job_obj_selected'] = True
                for job in st.session_state['job_list']:
                    st.session_state['selected_job_obj'][job] = job_obj[job]
            st.rerun()

    with col3:
        with st.expander("Select virtual machines"):
            if not st.session_state['job_list']:
                st.write("No backup job selected")
            else:
                for i, job in enumerate(st.session_state['job_list']):
                    st.session_state['selected_job_obj'][job] = st.multiselect(f"Select machines from {job}", options=job_obj[job], default=st.session_state['selected_job_obj'][job])
                    # st.session_state['selected_job_obj'][job] = st.session_state['obj_list']

    
    if st.button(f'Next step: View results :material/arrow_forward_ios:' , use_container_width=True):
            st.switch_page("pages/dashboard.py")
                
            

    