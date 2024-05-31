CREATE OR REPLACE VIEW distinct_other_details AS
SELECT DISTINCT jsonb_object_keys(other_details) AS detail_key
FROM ext2_line_item;


-- use these to monitor new other fields. 
-- This view will give you a list of all unique keys within the other_details JSONB object from ext2_line_item. 
-- If you need distinct values for each key, the query can be expanded further to split the JSONB into key-value pairs and then aggregate those pairs:

CREATE OR REPLACE VIEW distinct_other_details AS
SELECT DISTINCT jsonb_object_keys(other_details) AS detail_key
FROM ext2_line_item;