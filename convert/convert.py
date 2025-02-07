# convert.py 
# Check README to find what the script does  
# created by: irene celebrin 


import pandas as pd

def manipulate_csv(input_file_path, output_file_path):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(input_file_path)
    
    # Initialize a loop to iterate over the DataFrame rows
    i = 0
    while i < len(df):
        # Check if the current row has a query
        if pd.notna(df.at[i, 'Query']) and df.at[i, 'Query'] != '':
            # Initialize a list to store titles for this query
            titles = [df.at[i, 'Titles']]

# Initialize j for the following loop
            j = i + 1
            
            # Loop through subsequent rows to collect titles until a new query is found
            while j < len(df) and (pd.isna(df.at[j, 'Query']) or df.at[j, 'Query'] == ''):
                titles.append(df.at[j, 'Titles'])
                j += 1
            
            # Concatenate all collected titles with ';'
            df.at[i, 'Titles'] = ';'.join(titles)

        # Move to the next entry after processing
        i = j

# Remove rows where 'Query' is empty
    df = df[df['Query'].notna() & (df['Query'] != '')]

    # Write the modified DataFrame to a new CSV file
    df.to_csv(output_file_path, index=False)


# Usage
input_file = '/Users/icelebrin/Desktop/work-stuff/Multi_Intent/convert/input.csv'  # Path to your input CSV file
output_file = '/Users/icelebrin/Desktop/work-stuff/Multi_Intent/convert/output.csv'  # Path where you want to save the modified CSV
manipulate_csv(input_file, output_file)


