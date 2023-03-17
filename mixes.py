import xml.etree.ElementTree as ET
import streamlit as st

# Parse the XML file
tree = ET.parse('01-Mixes-001.xml')
root = tree.getroot()

# Find the "Mix" elements in the XML file
mixes = root.findall(".//MixNumber")

for mix in mixes:
    st.write(mix)

# for element in root.iter():
#     st.write(f"{element.tag} {element.attrib}")

