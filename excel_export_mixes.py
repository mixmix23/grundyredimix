import xml.etree.ElementTree as ET
import streamlit as st
import pandas as pd
import os
import datetime

st.set_page_config(page_title="Mixes XML to CSV")
# Sidebar to select plant code
plant_select = st.sidebar.radio("Select Plant", ["Coal City", "Morris", "River", "Plano", "Oswego", "Elburn"])
plant_code = {"Coal City": "001", "Morris": "002", "River": "003", "Plano": "004", "Oswego": "005", "Elburn": "006"}.get(plant_select, "001")

col1, col2 = st.columns(2)
# Filters by mix name and by mix desc
mix_name_filter = col1.text_input('Search Mix Number', placeholder='mix')
mix_desc_filter = col2.text_input('Search Mix Description', placeholder='desc')

# Parse the XML file - Mixes and Components
mix_tree = ET.parse(f"mixes_xml/01-Mixes-{plant_code}.xml")
mix_root = mix_tree.getroot()
component_tree = ET.parse(f"mixes_xml/01-Component-{plant_code}.xml")
component_root = component_tree.getroot()

# Get last modified date of xml file
last_modified = os.path.getmtime(f"mixes_xml/01-Mixes-{plant_code}.xml")
dt_object = datetime.datetime.fromtimestamp(last_modified)
central_us_tz = datetime.timezone(datetime.timedelta(hours=-6))  # CST
central_us_time = dt_object.astimezone(central_us_tz)
st.caption("Last Update: %s" % central_us_time.strftime('%Y-%m-%d %H:%M:%S'))

# Find the "MixHeader" elements in the XML file
mix_headers = mix_root.findall(".//MixHeader")
# Find the "Component" elements in the XML file
component_headers = component_root.findall(".//Component")


def create_mix_list(headers, components, mix_filter, desc_filter):
    # Create a list to store the data
    mix_list = []
    component_list = []
    # Create a list of all Mixes in XML file
    for mix_header in headers:
        mix_number = mix_header.find("MixNumber").text
        mix_description = mix_header.find("MixDescription").text
        plant = mix_header.find("PlantCode").text
        constituents = mix_header.findall(".//Constituents")
        # Create a dictionary to store the data for each mix
        mix_data = {
            "mix_number": mix_number,
            "mix_description": mix_description,
            "plant": plant,
            "cementitious": 0
        }
        # Extract and store constituent data
        for constituent in constituents:
            constituent_code = constituent.find("ConstituentCode").text
            dosage = float(constituent.find("Dosage").text)  # Convert dosage to a float

            # Check if the dosage is greater than 0 before adding it to the dictionary
            if dosage > 0:
                mix_data[constituent_code] = dosage

        # Calculate the total 'cementitious' dosage
        mix_data["cementitious"] = mix_data.get("CEMENT", 0) + mix_data.get("SLAG", 0) + mix_data.get("FLYASH", 0)

        mix_list.append(mix_data)

    # for item in mix_list:
    #     print(item)

    # Get component costs for total_cost of mixes
    for component in components:
        product_code = component.find("ProductCode").text
        cost_element = component.find("Cost").text
        cost_unit = component.find("CostUnitofMeasure").text
        qty_unit_measure = component.find("QuantityUnitofMeasure").text
        cost_breakdown = .01
        if cost_element == " ":
            cost = .01
        else:
            cost = float(cost_element)
        if cost_unit == 'TN':
            cost_breakdown = cost/2000
        elif cost_unit == 'GL':
            if product_code == 'COLD':
                cost_breakdown = cost
            else:
                cost_breakdown = cost/128
        component_data = {
            "product_code": product_code,
            "cost_unit": cost_unit,
            "qty_unit_measure": qty_unit_measure,
            "cost": cost,
            "cost_breakdown": cost_breakdown
        }
        component_list.append(component_data)
    for component in component_list:
        print(component)

    # Iterate through each dictionary in mix_list
    for mix in mix_list:
        # print("Mix - %s it's total cementitious is %s" % (mix['mix_number'], mix['cementitious']))
        total_cost = 0
        cost_dict = {}
        print("Mix %s" % mix['mix_number'])
        # Iterate through each component code in the dictionary
        for component_code in mix:
            # Check if the component code exists in component_list
            for component_dict in component_list:
                if component_dict['product_code'] == component_code:
                    # Set the cost of the component in mix_list equal to the cost in component_list
                    if component_dict["qty_unit_measure"] == 'CW':
                        cost = component_dict['cost_breakdown'] * mix['cementitious']/100
                    else:
                        cost = component_dict['cost_breakdown']
                    cost_dict[component_code] = cost * float(mix[component_code])
                    print("%s %s cost %s" % (component_dict['product_code'], mix[component_code], cost_dict[component_code]))
                    total_cost += cost_dict[component_code]
                    break
        mix['cost'] = cost_dict
        mix['total_cost'] = total_cost
        print("Total cost is %s" % total_cost)
        print("")
    # for item in mix_list:
    #     print(item)

    filtered_mix_list = [mix_data for mix_data in mix_list if mix_filter.lower() in mix_data['mix_number'].lower()]
    filtered_mix_desc_list = [mix_data for mix_data in mix_list if
                              desc_filter.lower() in mix_data['mix_description'].lower()]

    return mix_list, filtered_mix_list, filtered_mix_desc_list


def create_dataframe_csv():
    # Create DataFrame
    df_list = mix_filtered if mix_name_filter else desc_filtered if mix_desc_filter else mix_list_by_plant

    data = []
    for item in df_list:
        # st.write(item)
        if isinstance(item, dict):
            data.append([
                item['mix_number'],
                item['mix_description'],
                item['plant'],
                item.get('SAND', None),
                item.get('ELBURN', None),
                item.get('STONE 1', None),
                item.get('CEMENT', None),
                item.get('SLAG', None),
                item.get('COLD', None),
                item.get('GRAVEL', None),
                item.get('CHIPS', None),
                item.get('PEA', None),
                item.get('1.5 STONE', None),
                item.get('LW', None),
                item.get('STONE 2', None),
                item.get('CEMENT 2', None),
                item.get('AIR', None),
                item.get('SIKA 1000', None),
                item.get('SIKA 161', None),
                item.get('SIKATARD', None),
                item.get('NCA', None),
                item.get('total_cost', None)
            ])
        df = pd.DataFrame(data,
                          columns=['Mix', 'Description', 'Plant', 'Sand', 'Elb Sand', '3/4 Stone', 'Cement', 'Slag', 'Water', 'Gravel',
                                   'Chips', 'Pea', '1.5 Stone', 'LW', 'Stone 2', 'Cement 2', 'Air', '1000', '161', '440', 'NCA',
                                   'Total Cost'])
        df['Total Cost'] = df['Total Cost'].map("{:.2f}".format)
        st.write("main")

    # Create a checkbox to hide/show selected columns
    if st.checkbox("Hide/Show Columns"):
        selected_columns = st.multiselect("Select Columns to Display", df.columns.tolist())
        if selected_columns:
            st.write(df[selected_columns])
            st.write("filtered")

    # Display the data in a table
    if len(df_list) > 0:
        st.dataframe(df)

        # Specify the directory to save the CSV file
        downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        if not os.path.exists(downloads_dir):
            os.makedirs(downloads_dir)
        # Save the DataFrame to a CSV file
        filename = f"01-Mixes-{plant_code}.csv"
        filepath = os.path.join(downloads_dir, filename)
        df.to_csv(filepath, index=False)
        # Create a download button for the CSV file
        with open(filepath, "rb") as f:
            st.download_button(
                label="Download CSV",
                data=f.read(),
                file_name=filename,
                mime="text/csv"
            )
    else:
        st.write("No mix found")


# Create mix list by plant and filtered mix if applicable
mix_list_by_plant, mix_filtered, desc_filtered = create_mix_list(mix_headers, component_headers, mix_name_filter, mix_desc_filter)
# Create DataFrame for Streamlit and CSV Download
create_dataframe_csv()
