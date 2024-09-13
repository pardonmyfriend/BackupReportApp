# BackupReportApp
A Streamlit application for analyzing and visualizing backup reports sourced from Veeam Backup & Replication. Provides a dashboard with insights into backup performance.

## Description

This application allows users to upload backup reports and view them in a comprehensive dashboard. The dashboard provides insights into backup performance, success rates, errors and more.

## Installation

Follow these steps to install and run the application on your local machine.

### Clone the Repository

```
git clone https://github.com/pardonmyfriend/BackupReportApp.git
cd BackupReportApp
```

### Create and Activate a Virtual Environment (optional but recommended)

On macOS/Linux:
```
python3 -m venv .venv
source venv/bin/activate
```

On Windows:
```
python -m venv .venv
.venv\Scripts\activate
```

### Install Dependencies
```
pip install -r requirements.txt
```

## Running the App
```
streamlit run app.py
```

## Usage

1. Upload your backup report files in Excel format, ensuring they are generated from the Veeam Backup & Replication application.
3. Customize your analysis by selecting a date range and filtering the backup jobs or virtual machines you're interested in.
2. View the generated dashboard to analyze backup performance.
