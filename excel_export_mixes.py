import xml.etree.ElementTree as ET
import streamlit as st
import pandas as pd
import os
import datetime

st.set_page_config(page_title="Mixes XML to CSV")
# Sidebar to select plant code
plant_select = st.sidebar.radio("Select Plant", ["Coal City", "Morris", "River", "Plano", "Oswego"])
plant_code = {"Coal City": "001", "Morris": "002", "River": "003", "Plano": "004", "Oswego": "005"}.get(plant_select, "001")

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
            "plant": plant
        }
        for constituent in constituents:
            constituent_code = constituent.find("ConstituentCode").text
            dosage = constituent.find("Dosage").text
            mix_data[constituent_code] = dosage
        # Append the mix data to the list
        mix_list.append(mix_data)
    # for item in mix_list:
    #     print(item.items())

    # Get component costs for total_cost of mixes
    for component in components:
        product_code = component.find("ProductCode").text
        cost_element = component.find("Cost").text
        if cost_element == " ":
            cost = .01
        else:
            cost = float(cost_element)
        component_data = {
            "product_code": product_code,
            "cost": cost
        }
        component_list.append(component_data)
    # for component in component_list:
    #     print(component)

    # Iterate through each dictionary in mix_list
    for mix_dict in mix_list:
        print("Mix - %s" % mix_dict['mix_number'])
        total_cost = 0
        cost_dict = {}
        cementitious = 0
        # Iterate through each component code in the dictionary
        for component_code in mix_dict:
            # Calculate total cementitious for each mix
            if component_code in ["CEMENT", "SLAG", "FLYASH", "CEMENT 2"]:
                cementitious += int(mix_dict.get(component_code, 0))
            # Check if the component code exists in component_list
            for component_dict in component_list:
                if component_dict['product_code'] == component_code:
                    # Set the cost of the component in mix_list equal to the cost in component_list
                    if component_dict['product_code'] in ["CEMENT", "STONE 1", "SAND", "CHIPS", "GRAVEL", "SLAG",
                                                          "FLYASH", "PEA", "STONE 2", "1.5 STONE", "CEMENT 2"]:
                        cost = component_dict['cost'] / 2000
                    elif component_dict['product_code'] in ["SIKA 161", "SIKA 1000", "SIKATARD"]:
                        cwt = float(cementitious/100)
                        comp_cost_gal = float(component_dict.get('cost', 0))
                        comp_cost_oz = comp_cost_gal/128
                        comp_dosage = float(mix_dict.get(component_code, 0)) * cwt
                        cost = float(comp_cost_oz * comp_dosage)
                    else:
                        cost = component_dict['cost']
                    cost_dict[component_code] = cost * float(mix_dict[component_code])
                    total_cost += cost_dict[component_code]
                    print("component %s costs %s" % (component_dict['product_code'], cost_dict[component_code]))
                    break
        mix_dict['cost'] = cost_dict
        mix_dict['total_cost'] = total_cost
        print("Total cost for mix %s is %s" % (mix_dict['mix_number'], total_cost))
        # print("Mix %s cementitious is %s" % (mix_dict['mix_number'], cementitious))
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
                item.get('STONE 1', None),
                item.get('CEMENT', None),
                item.get('SLAG', None),
                item.get('COLD', None),
                item.get('GRAVEL', None),
                item.get('CHIPS', None),
                item.get('PEA', None),
                item.get('1.5 STONE', None),
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
                          columns=['Mix', 'Description', 'Plant', 'Sand', '3/4 Stone', 'Cement', 'Slag', 'Water', 'Gravel',
                                   'Chips', 'Pea', '1.5 Stone', 'Stone 2', 'Cement 2', 'Air', '1000', '161', '440', 'NCA',
                                   'test'])
        df['test'] = df['test'].map("{:.2f}".format)

    # Display the data in a table
    if df_list is not None:
        st.dataframe(df)
    else:
        st.write("Search does not match existing mix")

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


# Create mix list by plant and filtered mix if applicable
mix_list_by_plant, mix_filtered, desc_filtered = create_mix_list(mix_headers, component_headers, mix_name_filter, mix_desc_filter)
# Create DataFrame for Streamlit and CSV Download
create_dataframe_csv()
