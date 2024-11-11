import streamlit as st
import json
from PIL import Image
import os

class HomeInventoryApp:
    def __init__(self):
        st.title("Home Inventory Organizer")

        # Create images directory if it doesn't exist
        if not os.path.exists('item_images'):
            os.makedirs('item_images')

        # Initialize session state if not exists
        if 'inventory' not in st.session_state:
            # Load existing data if available
            try:
                with open('home_inventory.json', 'r') as file:
                    st.session_state.inventory = json.load(file)
            except FileNotFoundError:
                st.session_state.inventory = {}

        # Create two columns for layout
        left_col, right_col = st.columns(2)

        with left_col:
            st.subheader("Area Management")
            area_name = st.text_input("Area Name")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Add Area"):
                    self.add_area(area_name)
            with col2:
                if st.button("Delete Area"):
                    self.delete_area()

            st.subheader("Select Area")
            selected_area = st.selectbox("Choose Area", 
                                       options=list(st.session_state.inventory.keys()),
                                       key='area_select')

            st.subheader("Storage Location Management")
            storage_name = st.text_input("Storage Location Name")
            col3, col4 = st.columns(2)
            with col3:
                if st.button("Add Storage"):
                    self.add_storage(storage_name)
            with col4:
                if st.button("Delete Storage"):
                    self.delete_storage()

            storage_options = []
            if selected_area and selected_area in st.session_state.inventory:
                storage_options = list(st.session_state.inventory[selected_area].keys())
            
            st.subheader("Select Storage Location")
            selected_storage = st.selectbox("Choose Storage Location",
                                          options=storage_options,
                                          key='storage_select')

            st.subheader("Item Management")
            item_name = st.text_input("Item Name")
            uploaded_file = st.file_uploader("Upload Item Image", type=['png', 'jpg', 'jpeg'])
            if st.button("Add Item"):
                self.add_item(item_name, uploaded_file)

        with right_col:
            st.subheader("Inventory List")
            if st.button("Delete Selected"):
                self.delete_item()
            
            # Display inventory as a table
            data = []
            for area in st.session_state.inventory:
                for storage in st.session_state.inventory[area]:
                    for item_data in st.session_state.inventory[area][storage]:
                        if isinstance(item_data, dict):
                            item_name = item_data['name']
                            image_path = item_data.get('image', '')
                            if image_path and os.path.exists(image_path):
                                image = Image.open(image_path)
                                data.append({
                                    "Area": area,
                                    "Storage": storage,
                                    "Item": item_name,
                                    "Image": image
                                })
                            else:
                                data.append({
                                    "Area": area,
                                    "Storage": storage,
                                    "Item": item_name,
                                    "Image": None
                                })
                        else:
                            # Handle legacy data
                            data.append({
                                "Area": area,
                                "Storage": storage,
                                "Item": item_data,
                                "Image": None
                            })
            
            if data:
                st.data_editor(data, key='inventory_table', 
                             column_config={
                                 "Area": st.column_config.TextColumn("Area"),
                                 "Storage": st.column_config.TextColumn("Storage"),
                                 "Item": st.column_config.TextColumn("Item"),
                                 "Image": st.column_config.ImageColumn("Image", help="Item image")
                             },
                             hide_index=True)

    def add_area(self, area):
        if not area:
            st.error("Please enter an area name")
            return
        if area not in st.session_state.inventory:
            st.session_state.inventory[area] = {}
            self.save_inventory()
            st.success(f"Area '{area}' added successfully")
            st.rerun()
        else:
            st.error("Area already exists")

    def delete_area(self):
        if st.session_state.area_select:
            # Delete associated images first
            area = st.session_state.area_select
            for storage in st.session_state.inventory[area].values():
                for item in storage:
                    if isinstance(item, dict) and 'image' in item:
                        if os.path.exists(item['image']):
                            os.remove(item['image'])
            
            del st.session_state.inventory[area]
            self.save_inventory()
            st.success("Area deleted successfully")
            st.rerun()

    def add_storage(self, storage):
        if not st.session_state.area_select:
            st.error("Please select an area first")
            return
        if not storage:
            st.error("Please enter a storage location name")
            return
        if storage not in st.session_state.inventory[st.session_state.area_select]:
            st.session_state.inventory[st.session_state.area_select][storage] = []
            self.save_inventory()
            st.success(f"Storage '{storage}' added successfully")
            st.rerun()
        else:
            st.error("Storage location already exists in this area")

    def delete_storage(self):
        if st.session_state.area_select and st.session_state.storage_select:
            # Delete associated images first
            storage = st.session_state.inventory[st.session_state.area_select][st.session_state.storage_select]
            for item in storage:
                if isinstance(item, dict) and 'image' in item:
                    if os.path.exists(item['image']):
                        os.remove(item['image'])
            
            del st.session_state.inventory[st.session_state.area_select][st.session_state.storage_select]
            self.save_inventory()
            st.success("Storage location deleted successfully")
            st.rerun()

    def add_item(self, item, uploaded_file):
        if not all([st.session_state.area_select, st.session_state.storage_select, item]):
            st.error("Please fill in all fields")
            return

        area = st.session_state.area_select
        storage = st.session_state.storage_select
        
        if area not in st.session_state.inventory:
            st.error("Please select a valid area")
            return
        if storage not in st.session_state.inventory[area]:
            st.error("Please select a valid storage location")
            return
        
        item_data = {'name': item}
        
        if uploaded_file:
            # Save the uploaded image
            image_path = os.path.join('item_images', f"{area}_{storage}_{item}_{uploaded_file.name}")
            with open(image_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            item_data['image'] = image_path
        
        st.session_state.inventory[area][storage].append(item_data)
        self.save_inventory()
        st.success(f"Item '{item}' added successfully")
        st.rerun()

    def delete_item(self):
        if 'inventory_table' in st.session_state and st.session_state.inventory_table:
            selected_rows = st.session_state.inventory_table
            for row in selected_rows:
                area = row['Area']
                storage = row['Storage']
                item_name = row['Item']
                
                # Find and remove the item
                storage_list = st.session_state.inventory[area][storage]
                for item in storage_list:
                    if isinstance(item, dict) and item['name'] == item_name:
                        if 'image' in item and os.path.exists(item['image']):
                            os.remove(item['image'])
                        storage_list.remove(item)
                        break
                    elif item == item_name:  # Legacy data
                        storage_list.remove(item)
                        break
                
                if not st.session_state.inventory[area][storage]:
                    del st.session_state.inventory[area][storage]
                if not st.session_state.inventory[area]:
                    del st.session_state.inventory[area]
            
            self.save_inventory()
            st.success("Selected items deleted successfully")
            st.rerun()

    def save_inventory(self):
        with open('home_inventory.json', 'w') as file:
            json.dump(st.session_state.inventory, file)

if __name__ == "__main__":
    app = HomeInventoryApp()
