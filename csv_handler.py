import csv

def export_to_csv(filename, items):
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['ID', 'Name', 'Quantity', 'Price'])
        for item in items:
            writer.writerow(item)

def import_from_csv(filename):
    items = []
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row
        for row in reader:
            items.append((row[1], int(row[2]), float(row[3])))
    return items   