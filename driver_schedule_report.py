import dateutil.parser
import pandas as pd
import pytz
import requests
import streamlit as st
# from fpdf import FPDF

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
                 'pin': item['pin'], 'cellNumber': item['cellNumber']})
        print('Employee Data Filtered Keys')
        print(list(employee_data[0].keys()))
        # for item in employee_data:
        #     print(item)
        return employee_data
    else:
        print(f"Error: Failed to retrieve data from {url}")


def get_schedule_data():
    url = 'https://dfapi.digitalfleet.com/api/v2/Schedule?page=1&pageSize=100'

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        schedule_data = []
        data = response.json()
        print('Schedule Data Full Keys')
        print(list(data["data"][0].keys()))
        for item in data['data']:
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


employee_list = get_employee_data()
schedule_list = get_schedule_data()

schedule_report = []
for item in schedule_list:
    for name in employee_list:
        if item['userId'] == name['userId'] and item['startTime'] is not None:
            schedule_report.append({'userId': name['userId'], 'firstName': name['firstName'], 'lastName': name['lastName'],
                                    'plantPointId': item['plantPointId'], 'scheduleDate': item['scheduleDate'], 'startTime': item['startTime']})

print('Start Times')
for item in schedule_report:
    print(item)


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
    print('localtime %s' % localtime)
    start_time = localtime.ctime()
    print('start time %s' % start_time)

    if isinstance(item, dict):
        data.append([
            item['firstName'],
            item['lastName'],
            plantId,
            start_time
        ])
    df = pd.DataFrame(data,
                      columns=['First', 'Last', 'Plant', 'Start Time'])
    # df = df.sort_values(['Plant', 'Start Time'], ascending=[True, True])

st.dataframe(df)

# pdf = FPDF()
# pdf.add_page()
# pdf.set_xy(0, 0)
# pdf.set_font('arial', 'B', 12)
#
# pdf.cell(50, 10, 'First', 1, 0, 'C')
# pdf.cell(40, 10, 'Last', 1, 0, 'C')
# pdf.cell(40, 10, 'Plant', 1, 0, 'C')
# pdf.cell(40, 10, 'Start Time', 1, 0, 'C')
#
# pdf.output('test.pdf', 'F')


