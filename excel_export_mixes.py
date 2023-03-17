import xml.etree.ElementTree as ET
import streamlit as st
import pandas as pd
import os

# Sidebar to select plant code
plant_code = st.sidebar.radio("Select plant code", ["001", "002", "003"])

# Parse the XML file
tree = ET.parse(f"01-Mixes-{plant_code}.xml")
root = tree.getroot()

# Find the "MixHeader" elements in the XML file
mix_headers = root.findall(".//MixHeader")

# Create a list to store the data
data = []

for mix_header in mix_headers:
    mix_number = mix_header.find("MixNumber").text
    mix_description = mix_header.find("MixDescription").text
    plant = mix_header.find("PlantCode").text
    constituents = mix_header.findall(".//Constituents")

    # Create a dictionary to store the data for each mix
    mix_data = {
        "Mix Number": mix_number,
        "Mix Description": mix_description,
        "Plant": plant
    }
    for constituent in constituents:
        constituent_code = constituent.find("ConstituentCode").text
        dosage = constituent.find("Dosage").text
        mix_data[constituent_code] = dosage

    # Append the mix data to the list
    data.append(mix_data)

# Create a DataFrame from the data
df = pd.DataFrame(data)

# Display the data in a table
st.dataframe(df)

# Set the path to the downloads folder
DOWNLOADS_PATH = os.path.expanduser("~") + "/Downloads"

# Create a function to save the CSV file to the downloads folder
def save_csv(df, file_name):
    file_path = os.path.join(DOWNLOADS_PATH, file_name)
    df.to_csv(file_path, index=False)
    return file_path

# Add a button to save the CSV file
if st.button("Download CSV"):
    file_path = save_csv(df, "my_data.csv")
    st.download_button(
        label="Download",
        data=file_path,
        file_name="my_data.csv",
        mime="text/csv"
    )
\











