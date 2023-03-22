import xml.etree.ElementTree as ET
import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Mixes XML to CSV")
# Sidebar to select plant code
plant_code = st.sidebar.radio("Select plant code", ["001", "002", "003", "004", "005"])

# Filter by mix name
col1, col2 = st.columns([3, 1])
mix_name_filter = col1.text_input('Search Mix', placeholder='mix')

# Parse the XML file
tree = ET.parse(f"mixes_xml/01-Mixes-{plant_code}.xml")
root = tree.getroot()
# Find the "MixHeader" elements in the XML file
mix_headers = root.findall(".//MixHeader")


def create_mix_list(headers, mix_filter):
    # Create a list to store the data
    mix_list = []
    mix_list_filtered = []
    if mix_filter:
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
        for item in mix_list:
            if item['mix_number'].lower() == mix_filter or item['mix_number'] == mix_filter:
                st.write("got a match")
                st.write("item mix number: %s, mix filter: %s" % (item['mix_number'], mix_filter))
                st.write(item)
                mix_list_filtered[0] = item

    else:
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

    return mix_list, mix_list_filtered


mix_list_by_plant, mix_filtered = create_mix_list(mix_headers, mix_name_filter)

if mix_name_filter:
    st.write(mix_filtered)
    df = pd.DataFrame(mix_filtered)
else:
    st.write(mix_list_by_plant)
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
