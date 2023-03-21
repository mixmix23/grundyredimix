import dateutil.parser
import pandas as pd
import pytz
import requests
import streamlit as st
from datetime import datetime

api_key = "9A2B3075-33A5-42FD-9831-3A6ACEAE97F4"
headers = {'X-API-KEY': f'{api_key}'}


def get_employee_data():
    url = 'https://dfapi.digitalfleet.com/api/v2/Users?page=1&pageSize=100'
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        employee_data = []
        data = response.json()
        print('Employee Data Full Keys')
        print(list(data["data"][0].keys()))
        for item in data['data']:
            employee_data.append(
                {'userId': item['userId'], 'firstName': item['firstName'], 'lastName': item['lastName'],
                 'pin': item['pin'], 'hireDate': item['hireDate'], 'cellNumber': item['cellNumber']})
        print('Employee Data Filtered Keys')
        print(list(employee_data[0].keys()))
        # for item in employee_data:
        #     print(item)
        return employee_data
    else:
        print(f"Error: Failed to retrieve data from {url}")


def get_schedule_data(iso_date_arg):
    # st.write(iso_date_arg)
    # url_date = iso_date_arg.strftime('%Y-%m-%dT%H')
    # st.write(url_date)
    url = 'https://dfapi.digitalfleet.com/api/v2/Schedule?page=1&pageSize=100'
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        schedule_data = []
        data = response.json()
        print('Schedule Data Full Keys')
        print(list(data["data"][0].keys()))
        for item in data['data']:
            print(item)
        for item in data['data']:
            if item['scheduleDate'] == iso_date_arg:
                schedule_data.append(
                    {'userId': item['userId'], 'plantPointId': item['plantPointId'], 'scheduleDate': item['scheduleDate'],
                     'seniority': item['seniority'], 'notes': item['notes'], 'startTime':
                         item['startTime'], 'availability': item['availability']})
        print('Schedule Data Filtered Keys')
        print(list(schedule_data[0].keys()))
        # for item in schedule_data:
        #     print(item)
        return schedule_data
    else:
        print(f"Error: Failed to retrieve data from {url}")

# Create 3 equal-width columns
col1, col2, col3 = st.columns(3)
# Add a date picker to the first column
selected_date = st.date_input("Select a date")
if selected_date:
    iso_date = selected_date.strftime('%Y-%m-%dT%H')
# Display the selected date in the second column
col1.write('Selected date: ' + str(iso_date))

employee_list = get_employee_data()
schedule_list = get_schedule_data(iso_date)

schedule_report = []
for item in schedule_list:
    for name in employee_list:
        if item['userId'] == name['userId'] and item['startTime'] is not None:
            schedule_report.append(
                {'hireDate': name['hireDate'], 'userId': name['userId'], 'firstName': name['firstName'],
                 'lastName': name['lastName'], 'plantPointId': item['plantPointId'],
                 'scheduleDate': item['scheduleDate'],
                 'startTime': item['startTime']})
# print('Start Times')
# for item in schedule_report:
#     print(item)
data = []
for item in schedule_report:
    if item['plantPointId'] == 15095411:
        plantId = 'Oswego'
    elif item['plantPointId'] == 10533262:
        plantId = 'Plano'
    elif item['plantPointId'] == 10533260:
        plantId = 'Morris'
    else:
        plantId = str(item['plantPointId'])
    iso_date_str = item['startTime']
    iso_start_time = dateutil.parser.parse(iso_date_str)
    # print('iso_start_time %s' % iso_start_time)
    localtime = iso_start_time.astimezone(pytz.timezone("US/Central"))
    # print('localtime %s' % localtime)
    start_time = localtime.ctime()
    # print('start time %s' % start_time)
    start_time_without_year = ' '.join(start_time.split()[:4])
    start_time_without_seconds = start_time_without_year[:-3]

    name = f"{item['firstName']} {item['lastName']}"
    if isinstance(item, dict):
        data.append([
            item['hireDate'],
            name,
            plantId,
            start_time_without_seconds
        ])
    df = pd.DataFrame(data,
                      columns=['Hire', 'Name', 'Plant', 'Start Time'])
    df = df.sort_values('Hire')
    df = df.drop(columns='Hire')

# # Display dataframe to Streamlit
st.dataframe(df)
