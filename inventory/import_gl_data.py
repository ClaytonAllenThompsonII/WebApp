import csv
from inventory.models import GLLevel1, GLLevel2, GLLevel3, Product

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
    with open('/Users/claytonthompson/Desktop/Django GL and Product CSV/GLLevel2.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            parent_name = row['parent'].strip()
            gl1_parent = GLLevel1.objects.get(name=parent_name)
            GLLevel2.objects.get_or_create(
                name=row['name'].strip(),
                parent=gl1_parent
            )
    print("GLLevel2 data imported successfully.")

def import_gl_level_3():
    with open('/Users/claytonthompson/Desktop/Django GL and Product CSV/GLLevel3.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Assuming `row` is a dictionary representing a row read from the CSV
            # Clean the BOM from the keys of the row
            cleaned_row = {key.lstrip('\ufeff'): value for key, value in row.items()}

            # Use `cleaned_row` instead of `row` for further processing
            print(cleaned_row)  # Print the entire row to inspect its structure
            print(cleaned_row.keys())  # Print all keys in the cleaned row
            parent_name = cleaned_row['parent'].strip()
            try:
                gl2_parent = GLLevel2.objects.get(name=parent_name)
                GLLevel3.objects.get_or_create(
                    name=cleaned_row['name'].strip(),
                    parent=gl2_parent
                )
            except KeyError as e:
                print(f"KeyError encountered: {e}")
                print(f"Problematic row: {cleaned_row}")
            except GLLevel2.DoesNotExist:
                print(f"GLLevel2 parent not found for: {parent_name}")
    print("GLLevel3 data imported successfully.")


def import_products():
    filepath = '/Users/claytonthompson/Desktop/Django GL and Product CSV/Products.csv'  # Adjust the path as necessary
    with open(filepath, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Clean the BOM from the keys of the row and strip spaces
            cleaned_row = {key.lstrip('\ufeff').strip(): value.strip() for key, value in row.items()}

            # Extract parent_name and product_name using cleaned_row
            parent_name = cleaned_row['parent']
            product_name = cleaned_row['name']

            # Try to get the GLLevel3 parent and create the Product
            try:
                gl3_parent = GLLevel3.objects.get(name=parent_name)
                product, created = Product.objects.get_or_create(
                    name=product_name,
                    parent=gl3_parent
                )
                if created:
                    print(f"Created new product: {product_name} under GLLevel3: {parent_name}")
                else:
                    print(f"Product already exists: {product_name} under GLLevel3: {parent_name}")
            except KeyError as e:
                print(f"KeyError encountered: {e}. Problematic row: {cleaned_row}")
            except GLLevel3.DoesNotExist:
                print(f"GLLevel3 parent not found for: {parent_name}")

    print("Products data imported successfully.")


def test_csv_read():
    with open('/Users/claytonthompson/Desktop/Django GL and Product CSV/GLLevel3.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        headers = reader.fieldnames
        print("Headers:", headers)
        first_row = next(reader, None)
        print("First row:", first_row)

# Invoke the debugging function
test_csv_read()