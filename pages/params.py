import streamlit as st

st.header("Adjust parameters")

if 'backup_summary' not in st.session_state:
    st.warning(":material/warning: Data file not uploaded yet. Please upload your data file to set parameters.")
    if st.button(":material/arrow_back_ios: Back: Upload file", use_container_width=True):
        st.switch_page('pages/upload_file.py')
else:
    min_date = st.session_state['min_date']
    max_date = st.session_state['max_date']
    date = st.date_input(
        "Select the date range for analysis",
        (min_date, max_date),
        min_date,
        max_date,
        format="MM.DD.YYYY"
        )
    
    job_obj = st.session_state['job_obj']
    selected = {}

    multiselect_job = st.multiselect("Select backup jobs", options=job_obj.keys())

    with st.expander("Select virtual machines"):
        if not multiselect_job:
            st.write("No backup job selected")
        else:
            for i, job in enumerate(multiselect_job):
                multiselect_obj = st.multiselect(f"Select machines from {job}", options=job_obj[job])
                selected[job] = multiselect_obj
    
    if st.button(f'Next step: View results :material/arrow_forward_ios:' , use_container_width=True):
            st.switch_page("pages/dashboard.py")
                
            

    