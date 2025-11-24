import os
import dateutil.parser
import pandas as pd
import pytz
import requests
import streamlit as st
import sys
from datetime import datetime

api_key = "9A2B3075-33A5-42FD-9831-3A6ACEAE97F4"
headers = {'X-API-KEY': f'{api_key}'}

st.set_page_config(
    page_title="Driver Schedule",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded"
)


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


# def get_schedule_data(iso_date_arg, iso_end_date_arg):
def get_schedule_data(iso_date_arg):
    # st.write(iso_date_arg)
    # iso_date_arg = "2023-04-10T00"
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


# Header
st.title("🚛 Driver Schedule Dashboard")
st.markdown("---")

# Sidebar for controls
with st.sidebar:
    st.header("📅 Schedule Options")
    selected_date = st.date_input(
        "Select Date",
        value=datetime.now().date(),
        help="Choose the date to view driver schedules"
    )
    
    st.header("🔧 Display Options")
    show_notes = st.checkbox("Show Notes", value=True)
    show_deadhead = st.checkbox("Show Dead Head", value=True)

iso_date = selected_date.strftime('%Y-%m-%dT%H')

# Display selected date prominently
st.subheader(f"Schedule for {selected_date.strftime('%A, %B %d, %Y')}")

# Load data with progress indicator
with st.spinner('Loading employee and schedule data...'):
    employee_list = get_employee_data()
    schedule_list = get_schedule_data(iso_date)

# Plant mapping for cleaner code
PLANT_MAP = {
    15095411: 'Oswego',
    10533262: 'Plano', 
    10533260: 'Morris',
    10533261: 'Coal City',
    10533263: 'River',
    21909850: 'Elburn',
    32151775: 'Ottawa',
    32151802: 'Triumph'
}

# Excluded employees
EXCLUDED_EMPLOYEES = {
    "Dakota Brown", "James Ohlson", "Kevin Brooks", "Michael Smith", "Shane Coyne",
    "Brian Sheedy", "Chris Dewey", "JEREMIAH F NUGENT", "Brent Pommerening", 
    "Brandon Thetard", "Ryan Pratl"
}

# Build schedule report
schedule_report = []
for item in schedule_list:
    for name in employee_list:
        if item['userId'] == name['userId'] and item['startTime'] is not None:
            full_name = f"{name['firstName'].strip()} {name['lastName'].strip()}"
            if full_name not in EXCLUDED_EMPLOYEES:
                schedule_report.append({
                    'hireDate': name['hireDate'],
                    'userId': name['userId'],
                    'fullName': full_name,
                    'plantPointId': item['plantPointId'],
                    'scheduleDate': item['scheduleDate'],
                    'deadHeadPlantPointId': item['deadHeadPlantPointId'] or "-",
                    'startTime': item['startTime'],
                    'notes': item['notes'] or ""
                })
# Process data for display
data = []
plant_counts = {plant: 0 for plant in PLANT_MAP.values()}

for item in schedule_report:
    plant_name = PLANT_MAP.get(item['plantPointId'], str(item['plantPointId']))
    dead_head = PLANT_MAP.get(item['deadHeadPlantPointId'], str(item['deadHeadPlantPointId'])) if item['deadHeadPlantPointId'] != "-" else "-"
    
    plant_counts[plant_name] = plant_counts.get(plant_name, 0) + 1
    
    # Parse and format time
    iso_start_time = dateutil.parser.parse(item['startTime'])
    localtime = iso_start_time.astimezone(pytz.timezone("US/Central"))
    formatted_time = localtime.strftime("%H:%M")
    
    row_data = {
        'Name': item['fullName'],
        'Plant': plant_name,
        'Start Time': formatted_time,
        'Hire Date': item['hireDate']
    }
    
    if show_deadhead:
        row_data['Dead Head'] = dead_head
    if show_notes:
        row_data['Notes'] = item['notes']
        
    data.append(row_data)

# Create DataFrame
df = pd.DataFrame(data)
if not df.empty:
    # Sort by hire date, then drop it for display
    df_sorted = df.sort_values('Hire Date')
    df_display = df_sorted.drop(columns=['Hire Date'])
else:
    df_display = df

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📋 Driver Assignments")
    if not df_display.empty:
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Name": st.column_config.TextColumn("Driver Name", width="medium"),
                "Plant": st.column_config.TextColumn("Plant Location", width="small"),
                "Start Time": st.column_config.TextColumn("Start Time", width="small"),
                "Dead Head": st.column_config.TextColumn("Dead Head", width="small"),
                "Notes": st.column_config.TextColumn("Notes", width="large")
            }
        )
        
        # Download button
        csv_data = df_display.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name=f"driver_schedule_{selected_date.strftime('%Y-%m-%d')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No driver assignments found for this date.")

with col2:
    st.subheader("📊 Plant Summary")
    
    # Filter out plants with zero drivers
    active_plants = {plant: count for plant, count in plant_counts.items() if count > 0}
    
    if active_plants:
        # Create metrics for each plant
        for plant, count in sorted(active_plants.items()):
            st.metric(label=plant, value=f"{count} drivers")
        
        # Total drivers
        total_drivers = sum(active_plants.values())
        st.metric(label="**Total Drivers**", value=total_drivers)
        
        # Create a simple bar chart
        chart_data = pd.DataFrame({
            'Plant': list(active_plants.keys()),
            'Drivers': list(active_plants.values())
        })
        
        st.bar_chart(chart_data.set_index('Plant'), height=300)
    else:
        st.info("No plant assignments found.")

# Footer
st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")h_count > 0:
    count_list.append({'plant': 'Triumph', 'count': triumph_count})
total_count = morris_count + plano_count + oswego_count + cc_count + river_count + elburn_count + ottawa_count + triumph_count
if len(count_list) > 0:
    count_list.append({'plant': 'Total', 'count': total_count})
    df = pd.DataFrame(count_list)
    col5.markdown(df.style.hide(axis="index").to_html(), unsafe_allow_html=True)

col5.write("---")

dh_list = []
if morris_dh_count > 0:
    dh_list.append({'plant': 'Morris', 'count': morris_dh_count})
if plano_dh_count > 0:
    dh_list.append({'plant': 'Plano', 'count': plano_dh_count})
if oswego_dh_count > 0:
    dh_list.append({'plant': 'Oswego', 'count': oswego_dh_count})
if cc_dh_count > 0:
    dh_list.append({'plant': 'Coal City', 'count': cc_dh_count})
if river_dh_count > 0:
    dh_list.append({'plant': 'River', 'count': river_dh_count})
if elburn_dh_count > 0:
    dh_list.append({'plant': 'Elburn', 'count': elburn_dh_count})
if ottawa_dh_count > 0:
    dh_list.append({'plant': 'Ottawa', 'count': ottawa_dh_count})
if triumph_dh_count > 0:
    dh_list.append({'plant': 'Triumph', 'count': triumph_dh_count})
df = pd.DataFrame(dh_list)
if len(dh_list) > 0:
    col5.write("Dead Head")
    col5.markdown(df.style.hide(axis="index").to_html(), unsafe_allow_html=True)


