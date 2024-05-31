

import pandas as pd
import re

# Path to your CSV file
file_path = '/Users/claytonthompson/Desktop/line_item.csv'
with open(file_path, 'r', encoding='utf-8') as file:
    # Read the CSV file into a DataFrame
    data = pd.read_csv(file_path)

# Function to create a new product name
def create_product_name(description):
    # Extract the main product name before 'Item#:'
    product_name = re.search("^(.*?) Item#:", description)
    if product_name:
        product_name = product_name.group(1)
    else:
        product_name = "Unknown Product"
    
    # Optional: extract other parts like Size
    size = re.search("Size: ([^ ]+)", description)
    size = size.group(1) if size else "N/A"
    
    return f"{product_name}, {size}"

# Applying the function to each item in the DataFrame
data['new_product_name'] = data['item'].apply(create_product_name)

# Displaying the new product names
print(data[['item', 'new_product_name']])
