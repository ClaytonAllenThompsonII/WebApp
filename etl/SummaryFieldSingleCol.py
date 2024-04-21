import json
import pandas as pd

def extract_summary_fields(data):
    """ 
     Extracts summary fields from the JSON data into a DataFrame.
     This function iterates over each document's summary fields, creating a list of dictionaries,
     each representing a single field and its corresponding value.

    Args:
        data (dict): JSON data loaded from a file, containing the key 'ExpenseDocuments'.

    Returns:
        pd.DataFrame: A DataFrame where each row represents one summary field, with columns for field names and values. 
    """
    # Prepare an empty list to store each field as a dictionary
    summary_data = []

    # Iterate through each part of the data
    for expense_doc in data["ExpenseDocuments"]:
        expense_index = expense_doc["ExpenseIndex"]  # Assuming each document has a unique index

        # Process each summary field within the document
        for summary_field in expense_doc["SummaryFields"]:
            type_text = summary_field["Type"]["Text"]  # Get the type of the field
            value_text = summary_field["ValueDetection"]["Text"]  # Get the value of the field
            
            # Append a dictionary for each field with its type and value
            summary_data.append({
                'Field': type_text,
                'Value': value_text
            })

    # Convert the list of field dictionaries to a DataFrame
    return pd.DataFrame(summary_data)

def process_expense_documents(file_path):
    """ Processes the JSON file located at file_path to extract summary fields.

    Args:
        file_path (str): The file path to the JSON file containing expense documents.

    Returns:
        pd.DataFrame: A DataFrame containing the extracted summary field data.
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
    file_path = '/Users/claytonthompson/Desktop/2022_0407_KX_600159_1360.84.pdf.json'
    df = process_expense_documents(file_path)
    # Print the DataFrame clearly
    print(df.to_string(index=False))

if __name__ == "__main__":
    main()
