import csv
from django.db.models import Max
from invoice.models import GLLevel1, GLLevel2, GLLevel3, ConsolidatedGL

def clean_csv_row(row):
    return {key.lstrip('\ufeff').strip(): value.strip() for key, value in row.items()}

def delete_existing_gl_data():
    GLLevel3.objects.all().delete()
    GLLevel2.objects.all().delete()
    GLLevel1.objects.all().delete()
    print("Existing GL data deleted.")

def import_gl_level_1():
    file_path = '/Users/claytonthompson/Desktop/Data/django_data_models/django_gl_csv/GLLevel1.csv'
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        count = 0
        for row in reader:
            cleaned_row = clean_csv_row(row)
            gl1_name = cleaned_row['gl1_name']
            gl1_code = cleaned_row['gl1_code']
            GLLevel1.objects.create(gl1_name=gl1_name, gl1_code=gl1_code)
            print(f"Added new GL Level 1: {gl1_name} with code {gl1_code}")
            count += 1
        print(f"Total new GL Level 1 added: {count}")

def import_gl_level_2():
    file_path = '/Users/claytonthompson/Desktop/Data/django_data_models/django_gl_csv/GLLevel2.csv'
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        count = 0
        gl2_sequence = {}

        for row in reader:
            cleaned_row = clean_csv_row(row)
            gl2_name = cleaned_row['gl2_name']
            gl1_name = cleaned_row['gl1_name']

            try:
                gl1 = GLLevel1.objects.get(gl1_name=gl1_name)
            except GLLevel1.DoesNotExist:
                print(f"Error: GL Level 1 '{gl1_name}' not found for GL Level 2 '{gl2_name}'. Ensure '{gl1_name}' is correctly added to the GL Level 1 table.")
                continue

            if gl1.gl1_code not in gl2_sequence:
                gl2_sequence[gl1.gl1_code] = 1
            else:
                gl2_sequence[gl1.gl1_code] += 1

            gl2_code = f"{gl1.gl1_code}-{gl2_sequence[gl1.gl1_code]}"

            GLLevel2.objects.create(gl2_name=gl2_name, gl1=gl1, gl2_code=gl2_code)
            print(f"Added new GL Level 2: '{gl2_name}' under '{gl1_name}' with code '{gl2_code}'")
            count += 1

        print(f"Total new GL Level 2 added: {count}")

def import_gl_level_3():
    file_path = '/Users/claytonthompson/Desktop/Data/django_data_models/django_gl_csv/GLLevel3.csv'
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        count = 0
        gl3_sequence = {}

        for row in reader:
            cleaned_row = clean_csv_row(row)
            gl3_name = cleaned_row['gl3_name']
            gl2_name = cleaned_row['gl2_name']

            try:
                gl2 = GLLevel2.objects.get(gl2_name=gl2_name)
            except GLLevel2.DoesNotExist:
                print(f"Error: GL Level 2 '{gl2_name}' not found for GL Level 3 '{gl3_name}'. Ensure '{gl2_name}' is correctly added to the GL Level 2 table.")
                continue

            if gl2.gl2_code not in gl3_sequence:
                gl3_sequence[gl2.gl2_code] = 100
            else:
                gl3_sequence[gl2.gl2_code] += 10

            gl3_code = f"{gl2.gl2_code}-{gl3_sequence[gl2.gl2_code]}"

            GLLevel3.objects.create(gl3_name=gl3_name, gl2=gl2, gl3_code=gl3_code)
            print(f"Added new GL Level 3: '{gl3_name}' under '{gl2_name}' with code '{gl3_code}'")
            count += 1

        print(f"Total new GL Level 3 added: {count}")



def populate_consolidated_gl():
    consolidated_entries = []

    gl_level_3_entries = GLLevel3.objects.all()

    for gl3 in gl_level_3_entries:
        gl2 = gl3.gl2
        gl1 = gl2.gl1
        
        consolidated_entry = ConsolidatedGL(
            gl1_id=gl1.gl1_id,
            gl1_name=gl1.gl1_name,
            gl1_code=gl1.gl1_code,
            gl2_id=gl2.gl2_id,
            gl2_name=gl2.gl2_name,
            gl2_code=gl2.gl2_code,
            gl3_id=gl3.gl3_id,
            gl3_name=gl3.gl3_name,
            gl3_code=gl3.gl3_code
        )
        consolidated_entries.append(consolidated_entry)

    # Bulk create the consolidated entries
    ConsolidatedGL.objects.bulk_create(consolidated_entries)

    print(f"Total new ConsolidatedGL entries added: {len(consolidated_entries)}")













# Run your import steps in the Django shell as follows:
# Open the Django shell:
# source ~/Desktop/Venvs/WebAppVenv/bin/activate
# cd ~/Desktop/Source/WebApp
# python3 manage.py shell

# Inside the Django shell:
# from invoice.import_gl_pg import delete_existing_gl_data, import_gl_level_1, import_gl_level_2, import_gl_level_3
# delete_existing_gl_data()
# import_gl_level_1()
# import_gl_level_2()
# import_gl_level_3()