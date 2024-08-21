import streamlit as st
from utils.params_tools import *
from datetime import datetime, timedelta
import calendar

st.header("Adjust parameters")

if 'backup' not in st.session_state:
    st.warning(":material/warning: Data file not uploaded yet. Please upload your data file to set parameters.")
    if st.button(":material/arrow_back_ios: Back: Upload file", use_container_width=True):
        st.switch_page('pages/upload_file.py')
else:
    st.markdown("#### Date selection")
    option = st.radio("Select the date selection method", ["Date range", "Month and week", "Day range in month", "Predefined date ranges"])

    if option == "Date range":
        min_date = st.session_state['min_date']
        max_date = st.session_state['max_date']
        date_range = st.date_input(
            "Select the date range for analysis",
            (min_date, max_date),
            min_date,
            max_date,
            format="MM.DD.YYYY"
            )
        st.write(date_range)
    elif option == "Month and week":
        month_week = get_month_week()

        col1, col2 = st.columns(2)
        with col1:
            selected_month = st.selectbox("Select month", month_week.keys())
        with col2:
            selected_week = st.selectbox(
                "Select week", 
                month_week[selected_month], 
                format_func=lambda x: f"Week {x}: {get_week_dates(selected_month, x)[0].strftime('%d.%m')} - {get_week_dates(selected_month, x)[1].strftime('%d.%m')}"
                )
        date_range = get_week_dates(selected_month, selected_week)
        st.write(date_range)
    elif option == "Day range in month":
        months = get_month_week().keys()
        selected_month = st.selectbox("Select month", months)
        selected_month = datetime.strptime(selected_month, "%B").month
        year = st.session_state['year']

        _, num_days_in_month = calendar.monthrange(year, selected_month)

        min_day, max_day = get_days_for_month(year, selected_month)

        day_range = st.slider(
            f"Select the range of days in {datetime(year, selected_month, 1).strftime('%B')}",
            min_value=min_day,
            max_value=max_day,
            value=(min_day, max_day)
        )

        st.write(f"Selected date range: {day_range[0]:02d}.{selected_month:02d} - {day_range[1]:02d}.{selected_month:02d}")
    elif option == "Predefined date ranges":
        predefined_option = st.selectbox("Quick select a date range", ["Last week", "Last 2 weeks", "Last 3 weeks", "Last month"])

        if predefined_option == "Last week":
            date_range = (datetime.today() - timedelta(days=7), datetime.today())
            st.write(f"Selected range: Last week, from {date_range[0].date()} to {date_range[1].date()}")
        # elif predefined_option == "Last 2 weeks":

        # elif predefined_option == "Last 3 weeks":

        # elif predefined_option == "Last month"

    st.markdown("#### Backup job and virtual machines selection")
    job_obj = st.session_state['job_obj']
    selected = {}

    col1, col2 = st.columns([0.8, 0.2], vertical_alignment="bottom")

    with col1:
        multiselect_job = st.multiselect("Select backup jobs", options=job_obj.keys())
    with col2:
        if st.button("Select all", use_container_width=True):
            st.write("selected")

    with st.expander("Select virtual machines"):
        if not multiselect_job:
            st.write("No backup job selected")
        else:
            for i, job in enumerate(multiselect_job):
                multiselect_obj = st.multiselect(f"Select machines from {job}", options=job_obj[job])
                selected[job] = multiselect_obj
    
    if st.button(f'Next step: View results :material/arrow_forward_ios:' , use_container_width=True):
            st.switch_page("pages/dashboard.py")
                
            

    