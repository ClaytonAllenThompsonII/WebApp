CREATE OR REPLACE VIEW pro_product AS
SELECT DISTINCT
    pli.product_code,
    pli.item_description,
    pli.brand
FROM
    pro_line_item pli
ORDER BY
    pli.product_code, pli.item_description, pli.brand;