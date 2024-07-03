CREATE OR REPLACE VIEW pro2_line_item AS
SELECT 
    pli.*,
    p.product_id
FROM 
    pro_line_item pli
JOIN 
    out_product p
ON 
    pli.product_code = p.product_code
AND 
    pli.item_description = p.item_description

ORDER BY product_code, product_id;