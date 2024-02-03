import csv
from inventory.models import GLLevel1, GLLevel2, GLLevel3

# Execute the function to import GL Level 1 data
def import_gl_level_1():
    file_path = '/Users/claytonthompson/Desktop/Django GL and Product CSV/GLLevel1.csv'  # Update this path accordingly
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        count = 0
        for row in reader:
            # Assuming your CSV has columns 'name' that match your model fields
            _, created = GLLevel1.objects.get_or_create(name=row['name'])
            if created:
                print(f"Added new GL Level 1: {row['name']}")
                count += 1
            else:
                print(f"GL Level 1 already exists: {row['name']}")
        print(f"Total new GL Level 1 added: {count}")

# Remember to replace '/path/to/your/GLLevel1.csv' with the actual path to your CSV file.
        
def import_gl_level_2():
    file_path = '/Users/claytonthompson/Desktop/Django GL and Product CSV/GLLevel2.csv'  # Update this path accordingly
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        count = 0
        for row in reader:
            # Skip the header row with column names or empty rows
            if row['name'].lower() == 'name' or not row['name'].strip():
                continue

            # Get or create the GL Level 1 parent
            parent_name = row['parent'].strip()
            parent, _ = GLLevel1.objects.get_or_create(name=parent_name)

            # Get or create the GL Level 2 item
            _, created = GLLevel2.objects.get_or_create(
                name=row['name'].strip(),
                parent=parent
            )
            if created:
                count += 1
                print(f"Added new GL Level 2: {row['name']} under {parent_name}")
            else:
                print(f"GL Level 2 already exists: {row['name']} under {parent_name}")
        print(f"Total new GL Level 2 added: {count}")

# Call this function from the Django shell        
        

def import_gl_level_3():
    file_path = '/Users/claytonthompson/Desktop/Django GL and Product CSV/GLLevel3.csv'  # Update this path accordingly
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        count = 0
        for row in reader:
            # Skip the header row with column names or empty rows
            if row['name'].lower() == 'name' or not row['name'].strip():
                continue

            # Get or create the GL Level 2 parent
            parent_name = row['parent'].strip()
            parent, _ = GLLevel2.objects.get_or_create(name=parent_name)

            # Get or create the GL Level 3 item
            _, created = GLLevel3.objects.get_or_create(
                name=row['name'].strip(),
                parent=parent
            )
            if created:
                count += 1
                print(f"Added new GL Level 3: {row['name']} under {parent_name}")
            else:
                print(f"GL Level 3 already exists: {row['name']} under {parent_name}")
        print(f"Total new GL Level 3 added: {count}")

   

# Call this function from the Django shell