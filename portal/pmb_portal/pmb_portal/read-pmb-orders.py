import pandas as pd

# Load the CSV file 
file_path = "pmb-orders.csv"  # Update the path if needed
df = pd.read_csv(file_path)

# Drop completely empty rows
df_clean = df.dropna(how='all')

# Rename columns to generic field names
df_clean.columns = ['Name', 'Email', 'Phone', 'Address', 'Zip']

# Drop rows where essential fields like Name or Email are missing
df_clean = df_clean.dropna(subset=['Name', 'Email'])

# Convert each row into a dictionary (customer profile)
customer_profiles = df_clean.to_dict(orient='records')

# Print the customer profiles
for profile in customer_profiles:
    print(profile)
