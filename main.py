import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
import csv
from tkinter import filedialog
from reports import InventoryReporter
import os
import sys
import subprocess

class WarehouseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Noliktavas Pārvaldības Sistēma")
        self.db = Database()
        self.reporter = InventoryReporter(self.db)
        
        self.apply_styling()
        
        self.main_container = ttk.Frame(root, padding="20")
        self.main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.main_container.columnconfigure(1, weight=1)
        self.main_container.rowconfigure(1, weight=1)
        
        self.create_header()
        self.setup_search_frame()
        self.setup_item_list()
        self.setup_item_form()
        self.setup_buttons()
        self.setup_reports_section()
        
        self.refresh_item_list()
    
    def apply_styling(self):
        style = ttk.Style()
        
        try:
            style.theme_use('clam')
        except:
            pass
        
        style.configure('Header.TLabel', 
                       font=('Helvetica', 24, 'bold'),
                       foreground='#2c3e50')
        style.configure('SubHeader.TLabel', 
                       font=('Helvetica', 14),
                       foreground='#34495e')
        
        style.configure('Action.TButton',
                       padding=8,
                       font=('Helvetica', 10),
                       background='#3498db')
        style.configure('Danger.TButton',
                       padding=8,
                       font=('Helvetica', 10),
                       background='#e74c3c')
        
        style.configure('Search.TLabelframe',
                       padding=15,
                       relief='solid',
                       borderwidth=1)
        style.configure('Form.TLabelframe',
                       padding=15,
                       relief='solid',
                       borderwidth=1)
        
        style.configure('Treeview',
                       font=('Helvetica', 10),
                       rowheight=25)
        style.configure('Treeview.Heading',
                       font=('Helvetica', 10, 'bold'))

    def create_header(self):
        header_frame = ttk.Frame(self.main_container)
        header_frame.grid(row=0, column=0, columnspan=2, pady=(0, 30))
        
        ttk.Label(
            header_frame, 
            text="Noliktavas Pārvaldības Sistēma",
            style='Header.TLabel'
        ).grid(row=0, column=0)
        
        ttk.Label(
            header_frame,
            text="Inventāra Kontrole un Uzskaite",
            style='SubHeader.TLabel'
        ).grid(row=1, column=0, pady=(5, 0))

    def setup_search_frame(self):
        search_frame = ttk.LabelFrame(
            self.main_container,
            text="Meklēt Preces",
            padding="15",
            style='Search.TLabelframe'
        )
        search_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Name search
        name_frame = ttk.Frame(search_frame)
        name_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        ttk.Label(name_frame, text="Preces Nosaukums:", style='SubHeader.TLabel').pack(side=tk.LEFT, padx=(0, 10))
        self.search_name = ttk.Entry(name_frame, width=40)
        self.search_name.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Filters frame
        filters_frame = ttk.Frame(search_frame)
        filters_frame.grid(row=1, column=0, sticky=tk.W)
        
        # Quantity filter
        quantity_frame = ttk.Frame(filters_frame)
        quantity_frame.pack(side=tk.LEFT, padx=(0, 20))
        ttk.Label(quantity_frame, text="Daudzums:", style='SubHeader.TLabel').pack(anchor=tk.W)
        qty_inputs = ttk.Frame(quantity_frame)
        qty_inputs.pack(fill=tk.X)
        self.quantity_min = ttk.Entry(qty_inputs, width=15)
        self.quantity_min.insert(0, "Min")
        self.quantity_min.pack(side=tk.LEFT, padx=2)
        ttk.Label(qty_inputs, text="-").pack(side=tk.LEFT, padx=2)
        self.quantity_max = ttk.Entry(qty_inputs, width=15)
        self.quantity_max.insert(0, "Max")
        self.quantity_max.pack(side=tk.LEFT, padx=2)
        
        # Price filter
        price_frame = ttk.Frame(filters_frame)
        price_frame.pack(side=tk.LEFT)
        ttk.Label(price_frame, text="Cena:", style='SubHeader.TLabel').pack(anchor=tk.W)
        price_inputs = ttk.Frame(price_frame)
        price_inputs.pack(fill=tk.X)
        self.price_min = ttk.Entry(price_inputs, width=15)
        self.price_min.insert(0, "Min")
        self.price_min.pack(side=tk.LEFT, padx=2)
        ttk.Label(price_inputs, text="-").pack(side=tk.LEFT, padx=2)
        self.price_max = ttk.Entry(price_inputs, width=15)
        self.price_max.insert(0, "Max")
        self.price_max.pack(side=tk.LEFT, padx=2)
        
        # Search button
        ttk.Button(
            search_frame,
            text="Pielietot Filtrus",
            style='Action.TButton',
            command=self.search_items
        ).grid(row=1, column=1, sticky=tk.E, padx=(10, 0))
    
    def setup_item_list(self):
        self.tree = ttk.Treeview(self.main_container, columns=('ID', 'Nosaukums', 'Daudzums', 'Cena'))
        self.tree.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.tree.heading('ID', text='ID')
        self.tree.heading('Nosaukums', text='Nosaukums')
        self.tree.heading('Daudzums', text='Daudzums')
        self.tree.heading('Cena', text='Cena')
        
        self.tree.bind('<<TreeviewSelect>>', self.item_selected)
    
    def setup_item_form(self):
        form_frame = ttk.LabelFrame(self.main_container, text="Preces Informācija", padding="5")
        form_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        ttk.Label(form_frame, text="Nosaukums:").grid(row=0, column=0)
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(form_frame, textvariable=self.name_var)
        self.name_entry.grid(row=0, column=1)
        
        ttk.Label(form_frame, text="Daudzums:").grid(row=1, column=0)
        self.quantity_var = tk.StringVar()
        self.quantity_entry = ttk.Entry(form_frame, textvariable=self.quantity_var)
        self.quantity_entry.grid(row=1, column=1)
        
        ttk.Label(form_frame, text="Cena:").grid(row=2, column=0)
        self.price_var = tk.StringVar()
        self.price_entry = ttk.Entry(form_frame, textvariable=self.price_var)
        self.price_entry.grid(row=2, column=1)
    
    def setup_buttons(self):
        button_frame = ttk.Frame(self.main_container, padding="5")
        button_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        ttk.Button(button_frame, text="Pievienot Preci", command=self.add_item).grid(row=0, column=0)
        ttk.Button(button_frame, text="Atjaunināt Preci", command=self.update_item).grid(row=0, column=1)
        ttk.Button(button_frame, text="Dzēst Preci", command=self.delete_item).grid(row=0, column=2)
        ttk.Button(button_frame, text="Eksportēt CSV", command=self.export_csv).grid(row=0, column=3)
        ttk.Button(button_frame, text="Importēt CSV", command=self.import_csv).grid(row=0, column=4)
    
    def setup_reports_section(self):
        reports_frame = ttk.LabelFrame(
            self.main_container,
            text="Atskaites",
            padding="10",
            style='Search.TLabelframe'
        )
        reports_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Button(
            reports_frame,
            text="Vērtības Atskaite",
            command=self.generate_value_report,
            style='Action.TButton'
        ).grid(row=0, column=0, padx=5)
        
        ttk.Button(
            reports_frame,
            text="Daudzuma Atskaite",
            command=self.generate_quantity_report,
            style='Action.TButton'
        ).grid(row=0, column=1, padx=5)
        
        ttk.Button(
            reports_frame,
            text="Kopsavilkuma Atskaite",
            command=self.generate_summary_report,
            style='Action.TButton'
        ).grid(row=0, column=2, padx=5)

    def validate_inputs(self, name, quantity, price):
        errors = []
        
        if not name or len(name.strip()) == 0:
            errors.append("Nosaukums nevar būt tukšs")
        
        try:
            qty = int(quantity)
            if qty < 0:
                errors.append("Daudzumam jābūt pozitīvam skaitlim")
        except ValueError:
            errors.append("Daudzumam jābūt derīgam skaitlim")
        
        try:
            prc = float(price)
            if prc < 0:
                errors.append("Cenai jābūt pozitīvam skaitlim")
        except ValueError:
            errors.append("Cenai jābūt derīgam skaitlim")
        
        return errors

    def clear_form(self):
        self.name_var.set("")
        self.quantity_var.set("")
        self.price_var.set("")

    def add_item(self):
        try:
            name = self.name_var.get()
            quantity = self.quantity_var.get()
            price = self.price_var.get()
            
            errors = self.validate_inputs(name, quantity, price)
            if errors:
                messagebox.showerror("Ievades Kļūda", "\n".join(errors))
                return
            
            self.db.add_item(name, int(quantity), float(price))
            
            self.clear_form()
            self.refresh_item_list()
            messagebox.showinfo("Veiksmīgi", "Prece pievienota veiksmīgi!")
        except Exception as e:
            messagebox.showerror("Kļūda", f"Neizdevās pievienot preci: {str(e)}")

    def update_item(self):
        try:
            selected = self.tree.selection()
            if not selected:
                messagebox.showwarning("Warning", "Please select an item to update")
                return
            
            item_id = self.tree.item(selected[0])['values'][0]
            name = self.name_var.get()
            quantity = self.quantity_var.get()
            price = self.price_var.get()
            
            errors = self.validate_inputs(name, quantity, price)
            if errors:
                messagebox.showerror("Input Error", "\n".join(errors))
                return
            
            self.db.update_item(item_id, name, int(quantity), float(price))
            
            self.clear_form()
            self.refresh_item_list()
            messagebox.showinfo("Success", "Item updated successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update item: {str(e)}")

    def delete_item(self):
        try:
            selected = self.tree.selection()
            if not selected:
                messagebox.showwarning("Warning", "Please select an item to delete")
                return
            
            if not messagebox.askyesno("Confirm", "Are you sure you want to delete this item?"):
                return
            
            item_id = self.tree.item(selected[0])['values'][0]
            self.db.delete_item(item_id)
            
            self.clear_form()
            self.refresh_item_list()
            messagebox.showinfo("Success", "Item deleted successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete item: {str(e)}")

    def item_selected(self, event):
        try:
            selected = self.tree.selection()
            if not selected:
                return
            
            values = self.tree.item(selected[0])['values']
            
            self.name_var.set(values[1])
            self.quantity_var.set(values[2])
            self.price_var.set(values[3])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to select item: {str(e)}")

    def refresh_item_list(self):
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            items = self.db.get_all_items()
            for item in items:
                self.tree.insert('', 'end', values=item)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh item list: {str(e)}")

    def search_items(self):
        try:
            search_term = self.search_name.get()
            
            # Get quantity range
            qty_min = self.quantity_min.get()
            qty_max = self.quantity_max.get()
            quantity_range = {
                'min': int(qty_min) if qty_min != "Min" and qty_min.strip() else None,
                'max': int(qty_max) if qty_max != "Max" and qty_max.strip() else None
            }
            
            # Get price range
            price_min = self.price_min.get()
            price_max = self.price_max.get()
            price_range = {
                'min': float(price_min) if price_min != "Min" and price_min.strip() else None,
                'max': float(price_max) if price_max != "Max" and price_max.strip() else None
            }
            
            # Clear current items
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Get all items and filter
            items = self.db.get_all_items()
            filtered_items = []
            
            for item in items:
                # Check if item matches name filter
                if search_term and search_term.lower() not in item[1].lower():
                    continue
                
                # Check quantity range
                if quantity_range['min'] is not None and item[2] < quantity_range['min']:
                    continue
                if quantity_range['max'] is not None and item[2] > quantity_range['max']:
                    continue
                
                # Check price range
                if price_range['min'] is not None and item[3] < price_range['min']:
                    continue
                if price_range['max'] is not None and item[3] > price_range['max']:
                    continue
                
                filtered_items.append(item)
            
            # Display filtered items
            for item in filtered_items:
                self.tree.insert('', 'end', values=item)
            
        except ValueError as e:
            messagebox.showerror("Kļūda", "Lūdzu ievadiet derīgus skaitļus filtriem")
        except Exception as e:
            messagebox.showerror("Kļūda", f"Neizdevās meklēt preces: {str(e)}")

    def open_file(self, filepath):
        try:
            if sys.platform == "win32": #windows
                os.startfile(filepath)
            elif sys.platform == "darwin":  # mac
                subprocess.run(["open", filepath])
            else:  # linux
                subprocess.run(["xdg-open", filepath])
        except Exception as e:
            messagebox.showerror("Kļūda", f"Neizdevās atvērt failu: {str(e)}")

    def generate_value_report(self):
        try:
            filename = self.reporter.generate_value_report()
            self.open_file(filename)
            messagebox.showinfo("Veiksmīgi", "Vērtības atskaite izveidota veiksmīgi!")
        except Exception as e:
            messagebox.showerror("Kļūda", f"Neizdevās izveidot vērtības atskaiti: {str(e)}")

    def generate_quantity_report(self):
        try:
            filename = self.reporter.generate_quantity_report()
            self.open_file(filename)
            messagebox.showinfo("Veiksmīgi", "Daudzuma atskaite izveidota veiksmīgi!")
        except Exception as e:
            messagebox.showerror("Kļūda", f"Neizdevās izveidot daudzuma atskaiti: {str(e)}")
 
    def generate_summary_report(self):
        try:
            filename = self.reporter.generate_summary_report()
            self.open_file(filename)
            messagebox.showinfo("Veiksmīgi", "Kopsavilkuma atskaite izveidota veiksmīgi!")
        except Exception as e:
            messagebox.showerror("Kļūda", f"Neizdevās izveidot kopsavilkuma atskaiti: {str(e)}")

    def export_csv(self):
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if not filename:
                return
            
            items = self.db.get_all_items()
            
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['ID', 'Name', 'Quantity', 'Price'])
                writer.writerows(items)
            
            messagebox.showinfo("Success", "Dati eksportēti veiksmīgi!")
        except Exception as e:
            messagebox.showerror("Error", f"Kļuda eksportojot datus: {str(e)}")

    def import_csv(self):
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if not filename:
                return
            
            with open(filename, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    self.db.add_item(
                        name=row['Name'],
                        quantity=int(row['Quantity']),
                        price=float(row['Price'])
                    )
            
            self.refresh_item_list()
            messagebox.showinfo("Success", "Dati importēti veiksmīgi!")
        except Exception as e:
            messagebox.showerror("Error", f"Kļūda importējot datus: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WarehouseApp(root)
    root.mainloop() 