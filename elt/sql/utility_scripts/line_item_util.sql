SELECT 
    ld_text,
    type_text,
    COUNT(*) AS count
FROM 
    ext1_line_item
WHERE 
    type_text = 'OTHER'
GROUP BY 
    ld_text,
    type_text
ORDER BY 
    count DESC;