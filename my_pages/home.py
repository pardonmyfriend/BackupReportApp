import streamlit as st


st.title("Backup Report Analysis")
st.caption("Analyze your Veeam backup reports efficiently")
st.divider()

st.markdown(
    """
        ### How to get started:
        1. Upload your backup report by clicking on the button below.
        2. Select your desired parameters such as date range and specific backups.
        3. View and analyze the results on the dashboard.
    """
)

if st.button("Start analysis: Upload file :material/arrow_forward_ios:", use_container_width=True, type='primary'):
    st.switch_page("my_pages/file_upload.py")