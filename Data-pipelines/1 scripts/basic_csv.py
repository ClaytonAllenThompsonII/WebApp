import pandas as pd
import matplotlib.pyplot as plt
import squarify

# Provide the correct path to your file
file_path = '/Users/claytonthompson/Desktop/out_line_item.csv'

# Try loading the file with error handling
try:
    line_items_df = pd.read_csv(file_path)
    print("File loaded successfully!")

    # Step 1: Group by 'product_id' and calculate the sum of the 'price' column
    product_sum = line_items_df.groupby('product_id')['price'].sum().reset_index()

    # Step 2: Sort by price in descending order (optional) and keep the top 30
    top_30_products = product_sum.sort_values(by='price', ascending=False).head(30)

    # Step 3: Create a color palette of light blues and greys
    cmap = plt.get_cmap('Blues')  # Using a blue color palette
    normed_prices = top_30_products['price'] / top_30_products['price'].max()  # Normalize for color scaling
    colors = [cmap(value) for value in normed_prices]

    # Step 4: Create the treemap with borders and custom colors
    plt.figure(figsize=(12, 8))
    
    # Treemap sizes are based on the price (total spend) for each product
    squarify.plot(sizes=top_30_products['price'], 
                  label=top_30_products['product_id'], 
                  color=colors, 
                  alpha=0.8, 
                  edgecolor="grey",  # Border color
                  linewidth=2)  # Border thickness

    # Customize the plot
    plt.title('Treemap of Top 30 Products by Total Spend', fontsize=16, color='grey')
    plt.axis('off')  # Turn off the axis for a cleaner look
    plt.show()

except FileNotFoundError:
    print(f"File not found at path: {file_path}")
except pd.errors.EmptyDataError:
    print("File is empty.")
except pd.errors.ParserError:
    print("Error parsing the file. Check the file format.")
except Exception as e:
    print(f"An error occurred: {e}")