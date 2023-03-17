import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET

# Parse the XML file
tree = ET.parse('01-Mixes-001.xml')
root = tree.getroot()

# Extract the necessary information to build the table
table_data = []
for child in root:
    row = {}
    for subchild in child:
        row[subchild.tag] = subchild.text
    table_data.append(row)

# Create a dataframe from the extracted information
df = pd.DataFrame(table_data)

# Display the table using Streamlit
st.table(df)
