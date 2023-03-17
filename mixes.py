import xml.etree.ElementTree as ET
import streamlit as st

# Parse the XML file
tree = ET.parse('01-Mixes-001.xml')
root = tree.getroot()

# Find the "Mix" elements in the XML file
mixes = root.findall(".//MixHeader")

# Iterate over the "Mix" elements
for mix in mixes:
    # Extract the relevant information from the "Mix" element
    name = mix.get("MixFormula")
    constituents = mix.findall(".//Constituent")
    constituents_table = []

    # Iterate over the "Constituent" elements and build a table
    for constituent in constituents:
        constituents_table.append({
            "Name": constituent.get("ConstituentCode"),
            "Dosage": constituent.get("Dosage")
        })

    # Display the mix information and the constituents table using an expander
    with st.beta_expander(f"{name}"):
        st.write(f"Mix name: {name}")
        st.table(constituents_table)

