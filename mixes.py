import xml.etree.ElementTree as ET
import streamlit as st

# Parse the XML file
tree = ET.parse('01-Mixes-001.xml')
root = tree.getroot()

# Find the "Mix" element with the desired MixNumber
mix_number = "41"
mix = root.find(f".//MixFormula='{mix_number}'")

# If a matching Mix element is found, print its Constituents
if mix is not None:
    constituents = mix.findall(".//Constituent")
    for constituent in constituents:
        name = constituent.get("ConstituentCode")
        dosage = constituent.get("Dosage")
        st.write(f"Constituent Name: {name}, Dosage: {dosage}")
else:
    st.write(f"No mix with MixNumber '{mix_number}' found in the XML file.")

