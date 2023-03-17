import xml.etree.ElementTree as ET
import streamlit as st

# Parse the XML file
tree = ET.parse('01-Mixes-001.xml')
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
