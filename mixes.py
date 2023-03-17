import xml.etree.ElementTree as ET
import streamlit as st

# Parse the XML file
tree = ET.parse('01-Mixes-001.xml')
root = tree.getroot()

# Find the "Mix" elements in the XML file
mixes = root.findall(".//Mix")

# Iterate over the "Mix" elements
for mix in mixes:
    # Extract the relevant information from the "Mix" element
    name = mix.get("Name")
    date = mix.get("Date")
    constituents = mix.findall(".//Constituent")
    constituents_table = []

    # Iterate over the "Constituent" elements and build a table
    for constituent in constituents:
        constituents_table.append({
            "Name": constituent.get("Name"),
            "Percentage": constituent.get("Percentage")
        })

    # Display the mix information and the constituents table using an expander
    with st.beta_expander(f"{name} ({date})"):
        st.write(f"Mix name: {name}")
        st.write(f"Mix date: {date}")
        st.table(constituents_table)

