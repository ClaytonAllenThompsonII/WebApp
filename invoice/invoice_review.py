

# Logic to extract Textract Invoice JSON response information. 
# The idea is the access the JSON, show the user relevant fields for invoice
#line items and summary fields, and then allow the user to verify the 
#accuracy of the Textract extration service. Make an Changes, then push the final
# Payload to some staging table for ELT. 


for expense_doc in response["ExpenseDocuments"]:
        for line_item_group in expense_doc["LineItemGroups"]:
            for line_items in line_item_group["LineItems"]:
                for expense_fields in line_items["LineItemExpenseFields"]:
                    print_labels_and_values(expense_fields)
                    print()

        print("Summary:")
        for summary_field in expense_doc["SummaryFields"]:
            print_labels_and_values(summary_field)
            print()