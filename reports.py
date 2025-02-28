import matplotlib.pyplot as plt
from datetime import datetime
import os

class InventoryReporter:
    def __init__(self, database):
        self.db = database
        self.reports_dir = "reports"
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)

    def generate_value_report(self):
        """Generate report of total inventory value per item"""
        items = self.db.get_all_items()
        names = [item[1] for item in items]
        values = [item[2] * item[3] for item in items]  # quantity * price

        plt.figure(figsize=(10, 6))
        plt.bar(names, values)
        plt.title('Total Value by Item')
        plt.xlabel('Items')
        plt.ylabel('Total Value ($)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        filename = f"{self.reports_dir}/value_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(filename)
        plt.close()
        return filename

    def generate_quantity_report(self):
        """Generate report of quantity distribution"""
        items = self.db.get_all_items()
        names = [item[1] for item in items]
        quantities = [item[2] for item in items]

        plt.figure(figsize=(10, 6))
        plt.pie(quantities, labels=names, autopct='%1.1f%%')
        plt.title('Inventory Quantity Distribution')
        plt.axis('equal')
        
        filename = f"{self.reports_dir}/quantity_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(filename)
        plt.close()
        return filename
 
    def generate_summary_report(self):
        """Generate text summary of inventory status"""
        items = self.db.get_all_items()
        total_items = len(items)
        total_quantity = sum(item[2] for item in items)
        total_value = sum(item[2] * item[3] for item in items)
        avg_price = total_value / total_quantity if total_quantity > 0 else 0

        report = f"""Noliktavas Kopsavilkuma Atskaite
Izveidots: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
------------------------
Kopējais unikālo preču skaits: {total_items}
Kopējais daudzums: {total_quantity}
Kopējā noliktavas vērtība: €{total_value:.2f}
Vidējā cena par vienību: €{avg_price:.2f}
"""
        filename = f"{self.reports_dir}/summary_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        return filename 