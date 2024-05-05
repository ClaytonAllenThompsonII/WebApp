import json
import pandas as pd

def extract_line_items(data):
    """
    Extracts line item data from a nested JSON structure into a pandas DataFrame.
    
    Args:
    data (dict): The JSON data loaded from a file, expected to contain nested data
                 under 'ExpenseDocuments' and 'LineItemGroups'.

    Returns:
    pd.DataFrame: A DataFrame where each row represents a line item, with columns
                  for each 'Type' and 'Value' from the line item's fields.
    """
    # Prepare an empty list to store the data
    extracted_data = []

    # Iterate through each expense document in the provided data
    for expense_doc in data["ExpenseDocuments"]:
        # Iterate through each line item group within an expense document
        for line_item_group in expense_doc["LineItemGroups"]:
            group_index = line_item_group["LineItemGroupIndex"]  # Assuming each group has a unique index
            for line_item in line_item_group["LineItems"]:
                # Process each line item within the group
                line_item_data = {'GroupIndex': group_index}  # Initialize data dictionary for this line item

                # Extract fields from each line item and store them in a dictionary
                for field in line_item["LineItemExpenseFields"]:
                    type_text = field["Type"]["Text"]  # Get the type of the field
                    value_text = field["ValueDetection"]["Text"]  # Get the value of the field

                    # Store each field value under its type in the line item's data dictionary
                    line_item_data[type_text] = value_text

                # Append the line item's data to the list
                extracted_data.append(line_item_data)

    # Convert the list of data to a DataFrame for easy manipulation and visualization
    return pd.DataFrame(extracted_data)

def process_expense_documents(file_path):
    """
    Processes a JSON file to extract and return line item data as a DataFrame.

    Args:
    file_path (str): Path to the JSON file containing the expense documents data.

    Returns:
    pd.DataFrame: DataFrame containing the processed line item data.
    """
    # Load JSON data from the file
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Extract data into a DataFrame
    df = extract_line_items(data)
    return df

def main():
    """ Main function to execute the process of extracting line items from a JSON file
    and printing the resulting DataFrame. """
    
    #file_path = '/Users/claytonthompson/Desktop/2022_0407_KX_600159_1360.84.pdf.json'  # Adjust to your actual file path
    file_path = '/Users/claytonthompson/Desktop/2022_0402_KX_599585_1114.06.pdf.json'  # Adjust to your actual file path

    df = process_expense_documents(file_path)
    print(df)

if __name__ == "__main__":
    main()
