import csv
from inventory.models import GLLevel1, GLLevel2, GLLevel3, Product

# Execute the function to import GL Level 1 data
def clean_csv_row(row):
    # Cleans BOM and whitespace from keys and values in the row
    return {key.lstrip('\ufeff').strip(): value.strip() for key, value in row.items()}

def import_gl_level_1():
    file_path = '/Users/claytonthompson/Desktop/Data/Django GL and Product CSV/GLLevel1.csv'  # Update this path accordingly
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        count = 0
        for row in reader:
            cleaned_row = clean_csv_row(row)  # Clean each row before processing
            name = cleaned_row['name']
            _, created = GLLevel1.objects.get_or_create(name=name)
            if created:
                print(f"Added new GL Level 1: {name}")
                count += 1
            else:
                print(f"GL Level 1 already exists: {name}")
        print(f"Total new GL Level 1 added: {count}")

# You can now invoke this function as needed.

# Remember to replace '/path/to/your/GLLevel1.csv' with the actual path to your CSV file.

def import_gl_level_2():
    file_path = '/Users/claytonthompson/Desktop/Data/Django GL and Product CSV/GLLevel2.csv'
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Cleaning the data: removing BOM and whitespace
            cleaned_row = {key.lstrip('\ufeff').strip(): value.strip() for key, value in row.items()}
            
            # Fetching the parent GL Level 1 object
            parent_name = cleaned_row['parent']
            try:
                gl1_parent = GLLevel1.objects.get(name=parent_name)
            except GLLevel1.DoesNotExist:
                print(f"GL Level 1 parent not found for: '{parent_name}'. Ensure it is added correctly.")
                continue  # Skip this row if the parent isn't found
            
            # Creating or getting the GL Level 2 object
            gl_level2, created = GLLevel2.objects.get_or_create(
                name=cleaned_row['name'],
                parent=gl1_parent
            )
            
            if created:
                print(f"Added new GL Level 2: {cleaned_row['name']} under parent {parent_name}")
            else:
                print(f"GL Level 2 already exists: {cleaned_row['name']}")

# Invoke the function to import data
import_gl_level_2()