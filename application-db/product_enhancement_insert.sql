-- Insert new records or update existing ones in the out_product_enhanced table
INSERT INTO out_product_enhanced (
    product_code,
    item_description,
    brand,
    last_updated,
    generated_product_name,
    enhanced_details,
    estimated_expiration
)
SELECT
    product_code,
    item_description,
    brand,
    last_updated,
    NULL AS generated_product_name,  -- Placeholder for new fields
    NULL AS enhanced_details,        -- Placeholder for new fields
    NULL AS estimated_expiration     -- Placeholder for new fields
FROM
    out_product
ON CONFLICT (product_code, item_description)
DO UPDATE SET
    brand = EXCLUDED.brand,
    last_updated = EXCLUDED.last_updated;