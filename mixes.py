import xml.etree.ElementTree as ET
import streamlit as st

# Parse the XML file
tree = ET.parse('01-Mixes-001.xml')
root = tree.getroot()

for element in root.iter():
    st.write(f"{element.tag} {element.attrib}")

