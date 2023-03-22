import os
import dateutil.parser
import pandas as pd
import pytz
import requests
import streamlit as st
import sys

api_key = "9A2B3075-33A5-42FD-9831-3A6ACEAE97F4"
headers = {'X-API-KEY': f'{api_key}'}

st.set_page_config(page_title="Driver Schedule")


def get_employee_data():
    url = 'https://dfapi.digitalfleet.com/api/v2/Users?page=1&pageSize=100'
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        employee_data = []
        data = response.json()
        if len(data['data']) == 0:
            st.write("'data' is empty")
            st.write(data)
            sys.exit(1)
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
        st.write(f"Error: Failed to retrieve data  from {url}")
        sys.exit(1)


def get_schedule_data(iso_date_arg):
    url = f'https://dfapi.digitalfleet.com/api/v2/Schedule?startTime={iso_date_arg}%3A00%3A00&endTime={iso_date_arg}%3A00%3A00&pageSize=100'
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        schedule_data = []
        data = response.json()
        if len(data['data']) == 0:
            st.write("No Schedule Found For This Day")
            sys.exit(1)
        print('Schedule Data Full Keys')
        print(list(data["data"][0].keys()))
        for item in data['data']:
            if iso_date_arg in item['scheduleDate']:
                schedule_data.append(
                    {'userId': item['userId'], 'plantPointId': item['plantPointId'],
                     'scheduleDate': item['scheduleDate'],
                     'seniority': item['seniority'], 'notes': item['notes'], 'startTime': item['startTime'],
                     'deadHeadPlantPointId': item['deadHeadPlantPointId'], 'availability': item['availability']})
        print('Schedule Data Filtered Keys')
        print(list(schedule_data[0].keys()))
        # for item in schedule_data:
        #     print(item)
        return schedule_data
    else:
        st.write(f"Error: Failed to retrieve data from {url}")
        sys.exit(1)


# Create 3 equal-width columns
col1, col2 = st.columns(2)
# Add a date picker to the first column
selected_date = col1.date_input("Select a date")
if selected_date:
    iso_date = selected_date.strftime('%Y-%m-%dT%H')
# Display the selected date in the second column
# col1.write('Selected date: ' + str(iso_date))

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
oswego_count = 0
plano_count = 0
morris_count = 0

col4, col5, col6 = st.columns([3, 1, 1])

data = []
for item in schedule_report:
    if item['plantPointId'] == 15095411:
        plantId = 'Oswego'
        oswego_count += 1
    elif item['plantPointId'] == 10533262:
        plantId = 'Plano'
        plano_count += 1
    elif item['plantPointId'] == 10533260:
        plantId = 'Morris'
        morris_count += 1
    else:
        plantId = str(item['plantPointId'])

    if item['deadHeadPlantPointId'] == 15095411:
        dead_head = 'Oswego'
    elif item['deadHeadPlantPointId'] == 10533262:
        dead_head = 'Plano'
    elif item['deadHeadPlantPointId'] == 10533260:
        dead_head = 'Morris'
    else:
        dead_head = str(item['deadHeadPlantPointId'])
    iso_date_str = item['startTime']
    iso_start_time = dateutil.parser.parse(iso_date_str)
    # print('iso_start_time %s' % iso_start_time)
    localtime = iso_start_time.astimezone(pytz.timezone("US/Central"))
    # print('localtime %s' % localtime)
    start_time = localtime.ctime()
    csv_file_format = localtime.strftime('%a %b %d %Y')
    # print('start time %s' % start_time)
    start_time_without_year = ' '.join(start_time.split()[:4])
    start_time_without_seconds = start_time_without_year[:-3]

    name = f"{item['firstName']} {item['lastName']}"
    if isinstance(item, dict):
        data.append([
            item['hireDate'],
            name,
            plantId,
            start_time_without_seconds,
            dead_head
        ])
    df = pd.DataFrame(data,
                      columns=['Hire', 'Name', 'Plant', 'Start Time', "Dead Head"])
    df = df.sort_values('Hire')
    df = df.drop(columns='Hire')

col4.dataframe(df)

col5.write("Morris: %s" % morris_count)
col5.write("Plano: %s" % plano_count)
col5.write("Oswego: %s" % oswego_count)
col5.write("\n\n")
col5.write("Total: %s" % (morris_count + plano_count + oswego_count))

# Specify the directory to save the CSV file
downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")

if not os.path.exists(downloads_dir):
    os.makedirs(downloads_dir)

# Save the DataFrame to a CSV file
filename = f"{csv_file_format}.csv"
filepath = os.path.join(downloads_dir, filename)
df.to_csv(filepath, index=False)

# Create a download button for the CSV file
with open(filepath, "rb") as f:
    st.download_button(
        label="Download CSV",
        data=f.read(),
        file_name=filename,
        mime="text/csv"
    )
