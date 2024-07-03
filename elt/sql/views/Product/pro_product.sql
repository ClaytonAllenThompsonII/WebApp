CREATE OR REPLACE VIEW pro_product AS
WITH latest_products AS (
    SELECT 
        product_code,
        item_description,
        MAX(upload_date) AS most_recent_upload_date
    FROM 
        pro_line_item
    GROUP BY 
        product_code, item_description
)
SELECT 
    pli.product_code,
    pli.item_description,
    MAX(pli.brand) AS brand,
    MAX(pli.unit_of_measure) AS unit_of_measure,
    MAX(pli.unit_price) AS most_recent_unit_price,
    MAX(pli.net_amount) AS most_recent_net_amount,
    MAX(pli.taxes) AS most_recent_taxes,
    MAX(pli.discount) AS most_recent_discount,
    MAX(pli.quantity) AS most_recent_quantity,
    MAX(pli.price) AS most_recent_price,
    MAX(pli.pack) AS most_recent_pack,
    MAX(pli.size) AS most_recent_size,
    MAX(pli.unit) AS most_recent_unit,
    MAX(pli.weight) AS most_recent_weight,
    lp.most_recent_upload_date AS last_updated
FROM 
    pro_line_item pli
JOIN 
    latest_products lp
ON 
    pli.product_code = lp.product_code
AND 
    pli.item_description = lp.item_description
AND 
    pli.upload_date = lp.most_recent_upload_date
GROUP BY 
    pli.product_code, pli.item_description, lp.most_recent_upload_date;