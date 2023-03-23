import xml.etree.ElementTree as ET
import streamlit as st
import pandas as pd
import os
import datetime

st.set_page_config(page_title="Mixes XML to CSV")
# Sidebar to select plant code
plant_code = st.sidebar.radio("Select plant code", ["001", "002", "003", "004", "005"])


col1, col2 = st.columns(2)
# Filter by mix name
mix_name_filter = col1.text_input('Search Mix Number', placeholder='mix')
# Filter by mix desc
mix_desc_filter = col2.text_input('Search Mix Description', placeholder='mix')

# Parse the XML file
tree = ET.parse(f"mixes_xml/01-Mixes-{plant_code}.xml")
root = tree.getroot()

# Get last modified date of xml file
last_modified = os.path.getmtime(f"mixes_xml/01-Mixes-{plant_code}.xml")
dt_object = datetime.datetime.fromtimestamp(last_modified)
central_us_tz = datetime.timezone(datetime.timedelta(hours=-6)) # CST
central_us_time = dt_object.astimezone(central_us_tz)
st.caption("Last Update: %s" % central_us_time)

# Find the "MixHeader" elements in the XML file
mix_headers = root.findall(".//MixHeader")


def create_mix_list(headers, mix_filter, desc_filter):
    # Create a list to store the data
    mix_list = []
    for mix_header in headers:
        mix_number = mix_header.find("MixNumber").text
        mix_description = mix_header.find("MixDescription").text
        plant = mix_header.find("PlantCode").text
        constituents = mix_header.findall(".//Constituents")
        # Create a dictionary to store the data for each mix
        mix_data = {
            "mix_number": mix_number,
            "mix_description": mix_description,
            "plant": plant
        }
        for constituent in constituents:
            constituent_code = constituent.find("ConstituentCode").text
            dosage = constituent.find("Dosage").text
            mix_data[constituent_code] = dosage
        # Append the mix data to the list
        mix_list.append(mix_data)

    filtered_mix_list = [mix_data for mix_data in mix_list if mix_filter.lower() in mix_data['mix_number'].lower()]
    filtered_mix_desc_list = [mix_data for mix_data in mix_list if desc_filter.lower() in mix_data['mix_description'].lower()]

    return mix_list, filtered_mix_list, filtered_mix_desc_list


# Create mix list by plant and filtered mix if applicable
mix_list_by_plant, mix_filtered, desc_filtered = create_mix_list(mix_headers, mix_name_filter, mix_desc_filter)

# Create DataFrame
if mix_name_filter:
    df = pd.DataFrame(mix_filtered)
elif mix_desc_filter:
    df = pd.DataFrame(desc_filtered)
else:
    df = pd.DataFrame(mix_list_by_plant)

# Display the data in a table
st.dataframe(df)

# Specify the directory to save the CSV file
downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
if not os.path.exists(downloads_dir):
    os.makedirs(downloads_dir)
# Save the DataFrame to a CSV file
filename = f"01-Mixes-{plant_code}.csv"
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
