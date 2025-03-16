"""
This module processes expense document data from a specified JSON file. It extracts detailed line items and summary fields,
merges them into a unified dataset, and displays the combined information.

The script specifically:
- Extracts line items, capturing specific details like product codes, items, quantities, and prices from various expense documents.
- Gathers summary fields from each document, which include metadata such as addresses, total amounts, and other summarized data.
- Merges these two types of data based on a common index, providing a comprehensive view of each document's line items along with their corresponding summary information.
"""
import json
import pandas as pd

def extract_line_items(data):
    """
    Extracts line items from JSON data into a pandas DataFrame.
    Each line item is extracted with its associated group and expense index,
    alongside specific field types and values from the line item expense fields.

    Args:
        data (dict): JSON object containing nested data for expense documents.

    Returns:
        pd.DataFrame: DataFrame containing processed line items, with each row representing one line item.
    """
    extracted_data = []
    for expense_doc in data["ExpenseDocuments"]:
        for line_item_group in expense_doc["LineItemGroups"]:
            group_index = line_item_group["LineItemGroupIndex"]
            for line_item in line_item_group["LineItems"]:
                line_item_data = {'GroupIndex': group_index, 'ExpenseIndex': expense_doc["ExpenseIndex"]}
                for field in line_item["LineItemExpenseFields"]:
                    type_text = field["Type"]["Text"]
                    value_text = field["ValueDetection"]["Text"]
                    line_item_data[type_text] = value_text
                extracted_data.append(line_item_data)
    return pd.DataFrame(extracted_data)

def extract_summary_fields(data):
    """ Extracts summary fields from JSON data into a pandas DataFrame.
    Each document's summary fields are processed to extract types and values,
    which are used to populate a DataFrame.

    Args:
        data (dict): JSON object containing 'ExpenseDocuments' with 'SummaryFields'.

    Returns:
        pd.DataFrame: DataFrame containing summary fields with each row corresponding to a document's summaries.
        """
    summary_data = []
    for expense_doc in data["ExpenseDocuments"]:
        expense_index = expense_doc["ExpenseIndex"]
        document_summary = {'ExpenseIndex': expense_index}
        for summary_field in expense_doc["SummaryFields"]:
            type_text = summary_field["Type"]["Text"]
            value_text = summary_field["ValueDetection"]["Text"]
            document_summary[type_text] = value_text
        summary_data.append(document_summary)
    return pd.DataFrame(summary_data)

def merge_data(df_line_items, df_summary_fields):
    """ Merges line items and summary fields DataFrames based on the 'ExpenseIndex'.
    Args:
        df_line_items (pd.DataFrame): DataFrame containing line items.
        df_summary_fields (pd.DataFrame): DataFrame containing summary fields.

    Returns:
        pd.DataFrame: A merged DataFrame where each line item is augmented with the corresponding summary fields.
          """
    merged_df = pd.merge(df_line_items, df_summary_fields, on='ExpenseIndex', how='left')
    return merged_df

def process_expense_documents(file_path):
    """ Processes a given JSON file to extract, combine, and return line items and summary fields.
    Args:
        file_path (str): Path to the JSON file to process.

    Returns:
        pd.DataFrame: A DataFrame containing combined line items and summary field data.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    df_line_items = extract_line_items(data)
    df_summary_fields = extract_summary_fields(data)
    df_merged = merge_data(df_line_items, df_summary_fields)
    return df_merged

def main():
    """ Main execution function to process an expense document and print the resulting data.
    """
    file_path = '/Users/claytonthompson/Desktop/2022_0407_KX_600159_1360.84.pdf.json'
    df = process_expense_documents(file_path)
    print(df)

if __name__ == "__main__":
    main()
