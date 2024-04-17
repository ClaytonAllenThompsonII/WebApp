import json
import pandas as pd


def extract_summary_fields(data):
    """ 
     Extracts summary fields from the JSON data into a DataFrame.
     This function iterates over each document's summary fields, creating a dictionary
     that maps each type of field (from 'Type' field) to its corresponding value (from 'ValueDetection' field).

    Args:
    data (dict): JSON data loaded from a file, containing the key 'ExpenseDocuments'.

    Returns:
    pd.DataFrame: A DataFrame where each row represents the summary fields of a single document,
                  with columns dynamically generated for each type of summary field found in the documents. 
     
     """
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
    """ Processes the JSON file located at file_path to extract summary fields.

    Args:
    file_path (str): The file path to the JSON file containing expense documents.

    Returns:
    pd.DataFrame: A DataFrame containing the extracted summary field data for each document.
    """
    # Load JSON data from the file
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Extract data into a DataFrame
    df = extract_summary_fields(data)
    return df

def main():
    """ Main execution function to load data from a specified file,
      process it, and print the resulting DataFrame. """
    # Adjust to your actual file path
    file_path = '/Users/claytonthompson/Desktop/2022_0407_KX_600159_1360.84.pdf.json'  
    df = process_expense_documents(file_path)
    print(df)

if __name__ == "__main__":
    main()
