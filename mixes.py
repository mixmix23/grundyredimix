import xml.etree.ElementTree as ET
import streamlit as st

# Parse the XML file
tree = ET.parse('01-Mixes-001.xml')
root = tree.getroot()

# Find the "MixNumber" elements in the XML file
mix_numbers = root.findall(".//MixNumber")

# Iterate over the "MixNumber" elements and print their values
for mix_number in mix_numbers:
    st.write(mix_number.text)

# for element in root.iter():
#     st.write(f"{element.tag} {element.attrib}")

