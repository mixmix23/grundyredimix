import dateutil.parser
import pandas as pd
import pytz
import streamlit as st
from driver_schedule_report import get_employee_data, get_schedule_data

employee_list = get_employee_data()
schedule_list = get_schedule_data()

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