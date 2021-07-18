import requests
import json
import stdiomask
from itertools import groupby
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2 import service_account

# Copyright 2021 Micheal Stephenson

# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

#   http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

##################
## GET PASSWORD ##
##################

# to safely accept passwords 
# getpass import getpass 

## CODE ## 
#  from getpass import getpass
# password = getpass()


######################
## GLOBAL VARIABLES ## 
######################

authtoken = None
enrollmentId = None
courseId = None
requiredAssignments = []
requiredGrades = []
allGrades = None
assignmentTitles = []
currentAssignment = {'dueDate':datetime(2018, 9, 15, 12, 45, 36)}
currentStudents = []


###############
## CHANGE ME ##
###############

# Service Account JSON Credentials Location 
SERVICE_ACCOUNT_FILE = 'creds.json'

# Spreadsheets to edit. 

# The ID and range of a sample spreadsheet.
# Remove a specific portion of the URL for the ID 
# Example https://docs.google.com/spreadsheets/d/ID_STRING/edit?usp=sharing

SAMPLE_SPREADSHEET_ID = 'ID_STRING'  # Prod 

# Static variables for testing. Use at your own risk. 
# If not used you'll be prompted for your username and password. 
#authtoken = "mytoken"
email = None
password = None


############
## LOG IN ##
############

# Logs in and sets authtoken 
# authtoken is required for all other queries 

def login():
  global authtoken, email, password
  
  url = "https://bootcampspot.com/api/instructor/v1/login"
  
  if email is None:
    email = input("Username: ")
  if password is None: 
    password = stdiomask.getpass()

  payload = {
      'email':email,
      'password':password
      }

  headers = {'Content-Type': 'application/json'}
  response = requests.request("POST", url, headers=headers, json=payload,)
  authtoken = response.json()["authenticationInfo"]["authToken"]

login()

#################
## GET PROFILE ##
#################

# Sets enrollmentId and courseId

def getProfile():
  global enrollmentId, courseId
  
  url = "https://bootcampspot.com/api/instructor/v1/me"

  headers = {
    'authToken':authtoken,
    'Content-Type':'application/json'
  }

  response = requests.request("POST", url, headers=headers)
  
  me = response.json()["Enrollments"]
  enrollmentId = me[0]['id']
  courseId = me[0]['courseId']

getProfile()

#################
## ASSIGNMENTS ##
#################

# Get Required Assignments

def getRequiredAssignments():
  global requiredAssignments, authtoken, enrollmentId, currentAssignment
  url = "https://bootcampspot.com/api/instructor/v1/assignments"

  payload = {
     'enrollmentId':enrollmentId
  }
  headers = {
    'authToken':authtoken,
    'Content-Type':'application/json'
  }

  response = requests.request("POST", url, headers=headers, json=payload)
  assignments = response.json()["calendarAssignments"]  
  currentWeek =  response.json()["currentWeekAssignments"]  # list 

  #print(type(assignments[1]))

  
  a = []
  for i in assignments:
    
    if i['required']:
      a.append(i['title'])
      requiredAssignments.append(i.copy())
  assignmentTitles.append(a)  

  # Get Current Weeks Assignment 
  
  for i in currentWeek:
    
    if i['required'] == True and i['context']['contextCode'] == "academic":
      if datetime.strptime(i['dueDate'],'%Y-%m-%dT%H:%M:%SZ') > currentAssignment['dueDate']:
        #print(i['id'], i['title'])
        currentAssignment = i

  #print(currentWeek)


getRequiredAssignments()

#########################################
## GET CURRENT ASSIGNMENT STUDENT LIST ##
#########################################

# I have not seen any student roster that shows whether a student is dropped. 
# If a student dropped they may still show up in the grades table. 
# A dropped student will now show up in the assignment details for new assignments.
# This will get a list of students in the current assignemnt so that the dropped students can be identified. 

def getCurrentAssignmentStudents():
  global currentStudents
  url = "https://bootcampspot.com/api/instructor/v1/assignmentDetail"

  id = currentAssignment['id']

  payload = {
     'assignmentId':id
  }
  headers = {
    'authToken':authtoken,
    'Content-Type':'application/json'
  }

  response = requests.request("POST", url, headers=headers, json=payload)
  respStudents = response.json()['students']

  for i in respStudents:

    if i['student']['active'] == True:
      currentStudents.append(i['student']['firstName']+" "+i['student']['lastName'] )
  
  

getCurrentAssignmentStudents()



################
## GET GRADES ##
################

def getGrades():
  global allGrades
  url = "https://bootcampspot.com/api/instructor/v1/grades"

  payload = {
     'courseId':courseId
  }
  headers = {
    'authToken':authtoken,
    'Content-Type':'application/json'
  }

  response = requests.request("POST", url, headers=headers, json=payload)
  allGrades = response.json()

getGrades()

## Adds an ID to the required assignments. So that they can be sorted. 
## The assignments in the dictionary appear to be in order. 
## an order key is created so that it can be referenced later. 

x = 1
for i in requiredAssignments:
  
  i['order'] = x
  x=x+1

#####################
# LOOKUP SORT ORDER #
#####################

# Create LookupDict

lookupDict = {}
for i in requiredAssignments:
  lookupDict[i['title']] = i['order']

# Lookup function. Takes assignment title and lookup sort order. 

def lookupID(name):
  for title, order in lookupDict.items():
    if title == name:
      return(order)

###############################
# FILTER ONLY REQUIRED GRADES #
###############################

## Creates a list of required grades 
res = [ sub['title'] for sub in requiredAssignments]

for i in allGrades: 
  if i['assignmentTitle'] in res:
    i['order'] = lookupID(i['assignmentTitle'])
    requiredGrades.append(i.copy())

###########################
# GROUP GRADES BY STUDENT #
###########################

def key_func(k):
  return k['studentName']

requiredGrades = sorted(requiredGrades, key=key_func)
groupedGrades = []
for key, value in groupby(requiredGrades,key_func):
  temp = {}
  temp['name'] = key
  temp['grades'] = list(value)
  groupedGrades.append(temp)

###############
# SORT GRADES #
###############

for k in groupedGrades:
    newlist = sorted(k['grades'], key = lambda i: i['order'])
    k['sortedGrades'] = newlist

###########################
# CREATED THE ORDERED CSVs #
###########################

## Names and Grades 

gradesOut = []
namesOut = []
for i in groupedGrades:
  outS = []
  if i['name'] in currentStudents:
    name = [i['name']]
  else: 
    name = [i['name']+" (Inactive)"] 
  namesOut.append(name)
  for g in i['sortedGrades']:
    if g['submitted'] == True:
        sub = 'Submitted'  
    else: 
        sub = ''
    outS.append(sub)
  gradesOut.append(outS)

## Required Assignments Due Dates 

allDates = []
for i in requiredAssignments:
    date = [i['title']]
    date.append(i['dueDate'][:-10])
    allDates.append(date)




#####################################################################
##                        Google Sheets API                        ##   
#####################################################################


SCOPES = ['https://www.googleapis.com/auth/spreadsheets']



creds = None
creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)



service = build('sheets', 'v4', credentials=creds)

# Call the Sheets API
sheet = service.spreadsheets()
#result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Main!A1:Z46", valueRenderOption="FORMULA").execute()


# Clears 

clear_values_request_body = {
    # TODO: Add desired entries to the request body.
}


batch_clear_values_request_body = {

  'ranges' : [["Main!C3:ZZ"],["Main!A3:A"],["DueDates!A1:ZZ"],["Main!C1:ZZ1"]],

}

## Batch Clear
request = sheet.values().batchClear(spreadsheetId=SAMPLE_SPREADSHEET_ID, body=batch_clear_values_request_body).execute()

## Single Clear
#request = sheet.values().clear(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Main!C3:ZZ", body=clear_values_request_body).execute() # GRADES
#request = sheet.values().clear(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Main!A3:A", body=clear_values_request_body).execute() # NAMES

# Updates 

#aoa = [["foo",4000],["2/2/2020",5000],["5/5/2020",6000]]
aoa = gradesOut
students = namesOut


## Batch Updates

batch_update_values_request_body = {
    # How the input data should be interpreted.
    'value_input_option': 'USER_ENTERED',  # TODO: Update placeholder value.

    # The new values to apply to the spreadsheet.
    'data': [
        {
          'range': "Main!C3",
          'values': aoa
        }, {
          'range': "Main!A3",
          'values': students
        }, {
          'range': "DueDates!A1",
          'values': allDates
        },{
          'range': "Main!C1",
          'values': assignmentTitles
        }




    ],  # TODO: Update placeholder value.

    # TODO: Add desired entries to the request body.
}

request = sheet.values().batchUpdate(spreadsheetId=SAMPLE_SPREADSHEET_ID, body=batch_update_values_request_body).execute()


## Single Updates

#request = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Main!C3", valueInputOption="USER_ENTERED", body={"values":aoa}).execute() # GRADES
#request = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Main!A3", valueInputOption="USER_ENTERED", body={"values":students}).execute()  # Names
#request = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="DueDates!A1", valueInputOption="USER_ENTERED", body={"values":allDates}).execute() #DueDates







#values = result.get('values', [])
#print(result)

