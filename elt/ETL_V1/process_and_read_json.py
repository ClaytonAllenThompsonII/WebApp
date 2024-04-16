

import json
import pandas as pd

def extract_invoice_items(data):
    # Create an empty list to store the data
    extracted_data = []
    
    # Iterate through each part of the data
    for expense_doc in data["ExpenseDocuments"]:
        for line_item_group in expense_doc["LineItemGroups"]:
            for line_item in line_item_group["LineItems"]:
                for field in line_item["LineItemExpenseFields"]:
                    # Extract necessary details
                    type = field.get("Type", {}).get("Text", "N/A")
                    label = field.get("LabelDetection", {}).get("Text", "N/A")
                    value = field.get("ValueDetection", {}).get("Text", "N/A")
                    label_confidence = field.get("LabelDetection", {}).get("Confidence", 0)
                    value_confidence = field.get("ValueDetection", {}).get("Confidence", 0)
                    

                    # Append the extracted data to the list
                    extracted_data.append({
                        "Type": type,
                        "Label": label,
                        "Value": value,
                        "Label Confidence": label_confidence,
                        "Value Confidence": value_confidence
                    })
                    
    # Convert the list to a DataFrame for easy viewing and manipulation
    return pd.DataFrame(extracted_data)

def process_expense_analysis(file_path):
    # Load JSON data from the file
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    # Extract and display invoice items
    df = extract_invoice_items(data)
    print(df)

def main():
    #file_path = '/Users/yourusername/Desktop/yourfile.json'  # Update to your actual file path
    file_path = '/Users/claytonthompson/Desktop/2022_0407_KX_600159_1360.84.pdf.json'

    process_expense_analysis(file_path)

if __name__ == "__main__":
    main()
