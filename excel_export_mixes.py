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

# Create a button to save the data to a CSV file
if st.button("Save as CSV"):
    # Specify the directory to save the CSV file
    directory = "C:\Users\mixmi\Downloads"
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Save the DataFrame to a CSV file
    filename = f"01-Mixes-{plant_code}.csv"
    filepath = os.path.join(directory, filename)
    df.to_csv(filepath, index=False)

    # Display a success message
    st.success(f"Data saved to {filepath}")