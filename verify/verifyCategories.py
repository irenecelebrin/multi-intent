# verufy.py
# this script reads a batch of data, and for each row, it calls the OpenAI API to review the categories assigned to the query to find out FNs and FPs. 
# created by: irene celebrin 


import openai
import csv
import logging

# OpenAI API key
openai.api_key = "paste your API key here"


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


#set up the prompt
def review_categories(batch_row,guidelines_file,golden_set):
    prompt = (
       f""" I need to assign categories to identify user intents when inputting search queries on the web. 

       Read carefully the set of categories in {guidelines_file} to familiarize with the categories, and review the golden set in {golden_set} to see how categories are assigned. 
       
       After that, help me review the following data to check if any categories are missing, or are wrong. 
       Read the row in {batch_row}. It includes the following information: 
       - Query: a search query 
       - Titles: two or three titles from the search results page, all related to that query. They are separateb by ";"
       - Intent categories: One or more categories to define the intent behind the query. They are based on the query and on the Titles. 

       Based on Query and Titles, review the Intent categories assigned and do the following: 
       - If one or more categories included in "Intent categories" are wrong, provide as output: "WRONG:wrong category1|wrong category 2",
       - If one or more categories are missing from "Intent categories", provide as output: MISSING:missing category1|missing category 2" 

      Provide as output only your judgements on wrong or missing categories. Only use the categories included in the {guidelines_file}, do not introduce new categories. Do not add categories as MISSING, if they are already in "Intent categories". 
      Make sure you follow the expected output structure: WRONG:wrong category1,MISSING:missing category. For example: 
      My input: walmart near me,Walmart Supercenter in Mesquite, TX;Find a nearby store - Walmart.com;Walmart Neighborhood Market - Official MapQuest,local|location_sensitive|travel
      Your output: WRONG:travel,MISSING:shopping


      If you don't identify any wrong category, only add "WRONG:," followed by wrong categories. Do the same for missing categories. For example:     
      My input: metv.com schedule,What's On MeTV?;Watch meTV,entertainment|navigational
      Your output: WRONG:,MISSING:tv  ."""
            )

    # Call the OpenAI API with the prompt
    response = openai.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant skilles in web searches"},
            {"role": "user", "content": prompt}
        ],
        model="gpt-4o-mini",
    )

    # Extract the text response from the API
    return response.choices[0].message.content


#read batch 
def read_batch(file_path):
    try:
        batch = []
        with open(file_path, mode='r', newline ='',encoding='utf-8') as csvfile:
            batch_reader = csv.reader(csvfile)
            
            for row in batch_reader:
                if len(row) != 3:
                    print('more than 3 values')  # Skip malformed rows
                query, titles, categories = row
                titles_list = titles.split(';')
                categories = categories.split(';')
                batch.append({
                    "Query" : query.strip(),
                    "Titles" : titles_list,
                    "Categories" : categories
                })
            return batch
    except FileNotFoundError:
            logging.error(f"Input file {file_path} not found.")
            return []
    except Exception as e:
            logging.error(f"Error reading {file_path}: {e}")
            return []

    
#read golden set 
def read_goldenSet(file_path):
    try:
        golden_set = []
        with open(file_path, mode='r', newline='', encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file)

            for row in csv_reader:
                if len(row) != 3:
                    print('more than 3 values')  # Skip malformed rows
                query, titles, all_categories = row
                titles_list = titles.split('|')
                all_categories_list = all_categories.split('|')
                golden_set.append({
                    "Query": query.strip(),
                    "Titles": titles_list,
                    "All categories": all_categories_list
                })
            return golden_set      
    except FileNotFoundError:
            logging.error(f"Input file {file_path} not found.")
            return []
    except Exception as e:
            logging.error(f"Error reading {file_path}: {e}")
            return []

#read guidelines 
def read_guidelines(file_path):
    try:
        guidelines = []
        with open(file_path, mode='r', newline='', encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file)

            for row in csv_reader:
                if len(row) != 3:
                    print('more than 3 values')  # Skip malformed rows
                category, explanation, additional = row
                guidelines.append({
                    "Categories": category.strip(),
                    "Explanations": explanation.strip(),
                    "Additional Guidance/Examples": additional.strip()
                })
            return guidelines    
    except FileNotFoundError:
            logging.error(f"Input file {file_path} not found.")
            return []
    except Exception as e:
            logging.error(f"Error reading {file_path}: {e}")
            return []

#write output file 
def write_csv(file_path, data):
    try:
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Query','Titles','All Categories','LLM Review']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                writer.writerow(row)
        logging.info(f"Output written to {file_path}")
    except Exception as e:
        logging.error(f"Error writing to {file_path}: {e}")


def main():
    # Paths to files
    batch_file = '/Users/icelebrin/Desktop/Scripts/Multi_Intent/verify/batchSample.csv'
    output_file = '/Users/icelebrin/Desktop/Scripts/Multi_Intent/verify/LLMreviewOutput.csv'
    goldenSet_file = '/Users/icelebrin/Desktop/Scripts/Multi_Intent/verify/goldenSet.csv'
    guidelines = '/Users/icelebrin/Desktop/Scripts/Multi_Intent/guidelines.csv'

    batch = read_batch(batch_file)
    if not batch:
        logging.error("No companies to process. Exiting the program.")
        return
    golden_set = read_goldenSet(goldenSet_file)
    if not golden_set:
        logging.error("No companies to process. Exiting the program.")
        return   
    guidelines = read_guidelines(guidelines)

    result_data = []

    for batch_row in batch:
        query, titles, categories = batch_row
        logging.info(f"Finding categories: {batch_row[query]}")
        LLM_review = review_categories(batch_row,guidelines,golden_set)
        result_data.append({'Query': batch_row[query],'Titles':batch_row[titles], 'All Categories':batch_row[categories], 'LLM Review': LLM_review})

    write_csv(output_file, result_data)


if __name__ == "__main__":
    main()
