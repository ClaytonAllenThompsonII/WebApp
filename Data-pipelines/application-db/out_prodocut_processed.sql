

-- local testing using pg admin
psql -h localhost -U your_username -d your_database -c

\copy out_product_processed(product_id, product_code, item_description, brand, classification_id, last_updated) FROM '/Users/claytonthompson/Desktop/out_product.csv' DELIMITER ',' CSV HEADER NULL AS 'NULL';