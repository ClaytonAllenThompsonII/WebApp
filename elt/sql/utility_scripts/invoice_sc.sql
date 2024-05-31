SELECT 
    summary_label_text,
    summary_type_text,
    COUNT(*) AS count
FROM 
    ext1_invoice
WHERE 
    summary_type_text = 'PAYMENT_TERMS'
GROUP BY 
    summary_label_text,
    summary_type_text
ORDER BY 
    count DESC;