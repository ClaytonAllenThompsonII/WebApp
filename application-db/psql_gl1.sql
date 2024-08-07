psql -h localhost -U your_username -d your_database
\copy gl_level_1(gl1_name) FROM '/Users/claytonthompson/Desktop/Data/django_data_models/django_gl_csv/GLLevel1.csv' DELIMITER ',' CSV HEADER;

# The PG shell approach is best for data that has already been modeled and is used for tesing. IDs determined in ELT process not on app-db insert. 
# This approach falls apart when considering auto incremenet new ids. Use import_gl_pg.py in invoice app. 
\copy gl_level_2()