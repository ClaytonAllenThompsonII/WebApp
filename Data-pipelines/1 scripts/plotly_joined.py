import pandas as pd
import plotly.express as px

# Provide the correct path to your file
file_path = '/Users/claytonthompson/Desktop/out_line_item.csv'

# Try loading the file with error handling
try:
    line_items_df = pd.read_csv(file_path)
    print("File loaded successfully!")

    # Step 1: Group by 'product_id' to get sum of 'price' and first (min) 'item_description'
    product_agg = line_items_df.groupby('product_id').agg({
        'price': 'sum',  # Total price for each product
        'item_description': 'first'  # First description by default (can be min/max or other)
    }).reset_index()

    # Step 2: Sort by price in descending order and keep the top 30
    top_30_products = product_agg.sort_values(by='price', ascending=False).head(30)

    # Step 3: Create an interactive treemap using Plotly, with item description included
    fig = px.treemap(top_30_products, 
                     path=[px.Constant("Products"), 'item_description'],  # Use item description for labeling
                     values='price',  # Size of squares based on price
                     hover_data=['product_id'],  # Include product_id in hover info
                     title='Interactive Treemap of Top 30 Products by Total Spend')

    # Update layout
    fig.update_layout(
        treemapcolorway=["#c7e9f7", "#92c5de", "#4393c3", "#2166ac"],  # Light blue color palette
        margin=dict(t=50, l=25, r=25, b=25),
        title_font_size=16,
        title_font_color='grey',
        paper_bgcolor='white'
    )

    # Show the interactive plot
    fig.show()

except FileNotFoundError:
    print(f"File not found at path: {file_path}")
except pd.errors.EmptyDataError:
    print("File is empty.")
except pd.errors.ParserError:
    print("Error parsing the file. Check the file format.")
except Exception as e:
    print(f"An error occurred: {e}")