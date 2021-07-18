# Bootcamp Spot Student Submissions Overview

# Summary

This script will allow you to access the BootCamp Spot API pull submission informatoin and populate Google Spreadsheet showing an overview of all student submissions. This functionality does not currently exist in Bootcamp Spot and has aided cohorts in spotting potentially at risk students at a glance. 

# Requirements 

You can use the links in the requirements section as reference. The YouTube video was particularly helpful in setting up the project and service account. 

- Python3
- Modules in requirements.txt 
  - `pip install -r requirements.txt`
- Google Project
  - <https://www.youtube.com/watch?v=4ssigWmExak>
  - <https://developers.google.com/sheets/api/quickstart/python>
  - <https://developers.google.com/workspace/guides/create-project>
- Google Sheets API service account 
  - <https://developers.google.com/workspace/guides/create-credentials>
  - JSON containing service account credentials. 
- Bootcamp Spot API access
- Copy of template spreadsheet
  - <https://docs.google.com/spreadsheets/d/1OS0NDblSJWLNY4y2nJZ7wEsb570NatAbbFCZ1wu7MOs/edit?usp=sharing>
  - Do not change the names of the sheets. 
  - Grant the API service account editor permission to the spreadsheet. 


# Limitations 

I am only a TA for one corhort and enrollment at the moment. So, I could not see how the API reponses look with multiple enrollments, some additional building will likely be needed if you have more than one cohort or enrollment. 

# Spreadsheet Description 

The script should populate students, homework names, and due dates. There is some conditional formatting to draw attention to students with low homework completion percentages. 

# Script 

## Setup 

See requirements files for resources on setting up some of these requirements. 

- Create Google Project
- Create Google Sheets API service account, download credentials JSON, and add to creds.json.
- Copy of template spreadsheet
- Grant service account Editor permission to the sheet. 
- Install requirements `pip install -r requirements.txt`

## Run the Script 

Run with `python .\Main.py`

