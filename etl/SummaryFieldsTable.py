import json
import pandas as pd


def extract_summary_fields(data):
    # Prepare an empty list to store the data
    summary_data = []

    # Iterate through each part of the data
    for expense_doc in data["ExpenseDocuments"]:
        expense_index = expense_doc["ExpenseIndex"]  # Assuming each document has a unique index
        document_summary = {'ExpenseIndex': expense_index}  # Initialize data dictionary for this document's summary

        # Process each summary field within the document
        for summary_field in expense_doc["SummaryFields"]:
            type_text = summary_field["Type"]["Text"]  # Get the type of the field
            value_text = summary_field["ValueDetection"]["Text"]  # Get the value of the field
            
            # Store each field value under its type in the document's summary data dictionary
            document_summary[type_text] = value_text

        # Append the document's summary data to the list
        summary_data.append(document_summary)

    # Convert the list of data to a DataFrame for easy manipulation and visualization
    return pd.DataFrame(summary_data)

def process_expense_documents(file_path):
    # Load JSON data from the file
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Extract data into a DataFrame
    df = extract_summary_fields(data)
    return df

def main():
    file_path = '/Users/claytonthompson/Desktop/2022_0407_KX_600159_1360.84.pdf.json'  # Adjust to your actual file path
    df = process_expense_documents(file_path)
    print(df)

if __name__ == "__main__":
    main()
