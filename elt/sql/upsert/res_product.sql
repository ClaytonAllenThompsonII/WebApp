INSERT INTO out_product (
    product_code,
    item_description,
    brand,
    unit_of_measure,
    most_recent_unit_price,
    most_recent_net_amount,
    most_recent_taxes,
    most_recent_discount,
    most_recent_quantity,
    most_recent_price,
    most_recent_pack,
    most_recent_size,
    most_recent_unit,
    most_recent_weight,
    last_updated
)
SELECT
    product_code,
    item_description,
    brand,
    unit_of_measure,
    most_recent_unit_price,
    most_recent_net_amount,
    most_recent_taxes,
    most_recent_discount,
    most_recent_quantity,
    most_recent_price,
    most_recent_pack,
    most_recent_size,
    most_recent_unit,
    most_recent_weight,
    last_updated
FROM 
    pro_product
ON CONFLICT (product_code, item_description) DO UPDATE SET
    brand = EXCLUDED.brand,
    unit_of_measure = EXCLUDED.unit_of_measure,
    most_recent_unit_price = EXCLUDED.most_recent_unit_price,
    most_recent_net_amount = EXCLUDED.most_recent_net_amount,
    most_recent_taxes = EXCLUDED.most_recent_taxes,
    most_recent_discount = EXCLUDED.most_recent_discount,
    most_recent_quantity = EXCLUDED.most_recent_quantity,
    most_recent_price = EXCLUDED.most_recent_price,
    most_recent_pack = EXCLUDED.most_recent_pack,
    most_recent_size = EXCLUDED.most_recent_size,
    most_recent_unit = EXCLUDED.most_recent_unit,
    most_recent_weight = EXCLUDED.most_recent_weight,
    last_updated = EXCLUDED.last_updated;