import xml.etree.ElementTree as ET
import streamlit as st

# Define a dictionary that maps the plant codes to their corresponding XML file names
plant_xml_files = {
    "001": "01-Mixes-001.xml",
    "002": "01-Mixes-002.xml",
    "003": "01-Mixes-003.xml",
    "004": "01-Mixes-004.xml",
    "005": "01-Mixes-005.xml"
}

# Add radio buttons in the sidebar to select the plant code
plant_code = st.sidebar.radio("Select plant code", ["001", "002", "003", "004", "005"])

# Get the corresponding XML file name based on the selected plant code
xml_file_name = plant_xml_files[plant_code]

# Parse the XML file
tree = ET.parse(xml_file_name)
root = tree.getroot()

# Find the "MixHeader" elements in the XML file
mix_headers = root.findall(".//MixHeader")

for mix_header in mix_headers:
    mix_number = mix_header.find("MixNumber").text
    mix_description = mix_header.find("MixDescription").text
    plant = mix_header.find("PlantCode").text
    constituents = mix_header.findall(".//Constituents")

    # Display the mix number and the constituents
    with st.beta_expander(f"Mix {mix_number}"):
        st.write(f"Mix number: {mix_number}")
        st.write(f"Mix Description: {mix_description}")
        st.write(f"Plant: {plant}")
        for constituent in constituents:
            constituent_code = constituent.find("ConstituentCode").text
            dosage = constituent.find("Dosage").text
            st.write(f"{constituent_code}: {dosage}")

