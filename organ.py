import tkinter as tk
from tkinter import ttk
import json
from tkinter import messagebox

class HomeInventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Home Inventory Organizer")
        self.root.geometry("800x600")

        # Data structure to store items
        self.inventory = {}
        
        # Load existing data if available
        try:
            with open('home_inventory.json', 'r') as file:
                self.inventory = json.load(file)
        except FileNotFoundError:
            self.inventory = {}

        # Create main frames
        self.left_frame = ttk.Frame(root, padding="10")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.right_frame = ttk.Frame(root, padding="10")
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Area management
        ttk.Label(self.left_frame, text="Area Management").pack(pady=5)
        self.area_entry = ttk.Entry(self.left_frame)
        self.area_entry.pack(pady=5)
        ttk.Button(self.left_frame, text="Add Area", command=self.add_area).pack()
        ttk.Button(self.left_frame, text="Delete Area", command=self.delete_area).pack()

        # Area selection
        ttk.Label(self.left_frame, text="Select Area:").pack(pady=5)
        self.area_var = tk.StringVar()
        self.area_combo = ttk.Combobox(self.left_frame, textvariable=self.area_var)
        self.area_combo.pack(pady=5)
        self.area_combo.bind('<<ComboboxSelected>>', self.update_storage_locations)

        # Storage location management
        ttk.Label(self.left_frame, text="Storage Location Management").pack(pady=5)
        self.storage_entry = ttk.Entry(self.left_frame)
        self.storage_entry.pack(pady=5)
        ttk.Button(self.left_frame, text="Add Storage", command=self.add_storage).pack()
        ttk.Button(self.left_frame, text="Delete Storage", command=self.delete_storage).pack()

        # Storage location selection
        ttk.Label(self.left_frame, text="Select Storage Location:").pack(pady=5)
        self.storage_var = tk.StringVar()
        self.storage_combo = ttk.Combobox(self.left_frame, textvariable=self.storage_var)
        self.storage_combo.pack(pady=5)

        # Item entry
        ttk.Label(self.left_frame, text="Item Name:").pack(pady=5)
        self.item_entry = ttk.Entry(self.left_frame)
        self.item_entry.pack(pady=5)

        # Add item button
        ttk.Button(self.left_frame, text="Add Item", command=self.add_item).pack(pady=10)

        # Display area
        self.tree = ttk.Treeview(self.right_frame, columns=('Area', 'Storage', 'Item'), show='headings')
        self.tree.heading('Area', text='Area')
        self.tree.heading('Storage', text='Storage')
        self.tree.heading('Item', text='Item')
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Delete button
        ttk.Button(self.right_frame, text="Delete Selected", command=self.delete_item).pack(pady=5)

        # Update area combobox
        self.update_area_combobox()
        
        # Load existing items into tree
        self.refresh_tree()

    def update_area_combobox(self):
        self.area_combo['values'] = tuple(self.inventory.keys())

    def update_storage_locations(self, event=None):
        area = self.area_var.get()
        if area in self.inventory:
            self.storage_combo['values'] = tuple(self.inventory[area].keys())
        else:
            self.storage_combo['values'] = ()
        self.storage_combo.set('')

    def add_area(self):
        area = self.area_entry.get().strip()
        if not area:
            messagebox.showerror("Error", "Please enter an area name")
            return
        if area not in self.inventory:
            self.inventory[area] = {}
            self.save_inventory()
            self.update_area_combobox()
            self.area_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Area already exists")

    def delete_area(self):
        area = self.area_var.get()
        if area in self.inventory:
            del self.inventory[area]
            self.save_inventory()
            self.update_area_combobox()
            self.refresh_tree()
            self.area_var.set('')
            self.storage_var.set('')
            self.update_storage_locations()

    def add_storage(self):
        area = self.area_var.get()
        storage = self.storage_entry.get().strip()
        if not area:
            messagebox.showerror("Error", "Please select an area first")
            return
        if not storage:
            messagebox.showerror("Error", "Please enter a storage location name")
            return
        if storage not in self.inventory[area]:
            self.inventory[area][storage] = []
            self.save_inventory()
            self.update_storage_locations()
            self.storage_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Storage location already exists in this area")

    def delete_storage(self):
        area = self.area_var.get()
        storage = self.storage_var.get()
        if area in self.inventory and storage in self.inventory[area]:
            del self.inventory[area][storage]
            self.save_inventory()
            self.update_storage_locations()
            self.refresh_tree()
            self.storage_var.set('')

    def add_item(self):
        area = self.area_var.get()
        storage = self.storage_var.get()
        item = self.item_entry.get()

        if not all([area, storage, item]):
            messagebox.showerror("Error", "Please fill in all fields")
            return

        if area not in self.inventory:
            messagebox.showerror("Error", "Please select a valid area")
            return
        if storage not in self.inventory[area]:
            messagebox.showerror("Error", "Please select a valid storage location")
            return
        
        self.inventory[area][storage].append(item)
        self.save_inventory()
        self.refresh_tree()
        self.item_entry.delete(0, tk.END)

    def delete_item(self):
        selected_item = self.tree.selection()
        if not selected_item:
            return
        
        item = self.tree.item(selected_item)['values']
        area, storage, item_name = item
        
        self.inventory[area][storage].remove(item_name)
        if not self.inventory[area][storage]:
            del self.inventory[area][storage]
        if not self.inventory[area]:
            del self.inventory[area]
            self.update_area_combobox()
            self.update_storage_locations()
            
        self.save_inventory()
        self.refresh_tree()

    def refresh_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for area in self.inventory:
            for storage in self.inventory[area]:
                for item in self.inventory[area][storage]:
                    self.tree.insert('', tk.END, values=(area, storage, item))

    def save_inventory(self):
        with open('home_inventory.json', 'w') as file:
            json.dump(self.inventory, file)

if __name__ == "__main__":
    root = tk.Tk()
    app = HomeInventoryApp(root)
    root.mainloop()
