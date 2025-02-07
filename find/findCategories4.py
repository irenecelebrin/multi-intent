# findCategories4 
# This scripts reads a batch of queries + titles from a csv file, and for each row, it calls the OpenAI API to get the categories and confidence scores for the query based on the query + the titles. It also considers a golden set imported in the prompt. 
# It writes the output to a csv file. The output format is: query,category|confidence sccore;category2|confidence score. 
# created by: irene celebrin 

import openai 
import csv
import logging

# OpenAI API key
openai.api_key = 'api-key'
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


#set up the prompt
#The prompt inputs batch rows (query+titles) individually. It also imports a golden set with pre-annotated data. 
# TODO check if the way the golden set is imported is the best way. 
# The response format is: category1|score;category2|score...
def get_all_categories(batch_row,golden_set):
    prompt = (
       f""" Carefully read the row in {batch_row}. It includes a web Query, and two or three Titles from the search results page, all related to that Query. Review the query and then the titles, and based on that assign all relevant categories to the query. Assign a confidence score from 0 to 1 to each category, based on how certain you are. 
            The categories are the following: 

            - Adult: The query contains explicit or implicit intent for adult content. Some queries may not be obviously related to pornography, such amateur videos and daddy movies.
            - Automotive: This category includes queries about cars, motorcycles, trucks, parts, products, and services. It also covers searches to buy, sell, or research vehicles, as well as local automotive businesses such as dealerships, mechanics, and service providers. The label  does not apply to car rental and should not be assigned to queries that are only related to boats or RVs.
            - Company: This is for queries seeking generic company information, such as links to a company's official website, Wikipedia page, or social media accounts (e.g., Twitter, LinkedIn).
            - Dictionary: The query is expected to trigger dictionary-related modules, such as definitions, synonyms, antonyms, or usage explanations.
            - Education: Covers anything related to formal education, including schools (kindergarten to universities), vocational training, tutors, educational supplies, local educational organizations, policies, lesson planning, and education-related issues or services. The label is not assigned to queries related to school subjects (math, science, history, grammar, etc.) and homework.
            - Finance: Includes topics related to personal or corporate finance, stock tickers, financial services, stock markets, finance-related news, financial organizations, and businesses. The label is also applied to queries related to financial entities such as banks, mortgage lenders, financial advisors and insurance companies.
            - Health: Covers queries about diseases, conditions, therapies, treatments, healthcare providers, facilities (hospitals, clinics, offices), medical supplies, health-related policies, and health news (e.g., symptoms, healthcare reforms like Obamacare). The label should not be assigned to topics related to "alternative medicine", such as traditional Chinese medicine, aromatherapy, massage, Santeria, and Ayurveda.
            - Local: The query is intended to show a module containing information about businesses (addresses, phone numbers, hours). This is typical for searches involving nearby services or specific local needs. The label should not be assigned to queries seeking residential addresses.
            - Location Sensitivity: Queries where the search results (modules, algorithms, ads) vary depending on the user’s location. For example, local weather forecasts, region-specific services, or local listings on platforms like Craigslist and Redfin. This includes queries for specific addresses and directions. The label should be assigned to all the queries labeled with "Local".
            - TV: The query is expected to trigger TV-related Direct Displays, such as information on shows, channels, or programming schedules. Usually, queries with the "TV" label will also have the "entertainment" label.
            - Movie: The query is expected to trigger movie-related Direct Displays (e.g., film information, trailers, reviews). Usually, queries with the "Movie" label will also have the "entertainment" label.
            - Entertainment: Includes anything related to books, movies, music, TV, games, and other forms of entertainment. Also includes topics such as comedy, magazines, newspapers, comics, radio, live performances, visual arts, nightclubs, and theatre. 
            - Navigational: The intent is to navigate directly to a specific website, either explicitly (e.g., "facebook.com") or implicitly (e.g., "Facebook" to visit the homepage).
            - People: Covers queries about both notable and non-notable people. Notable people include current, historical, or fictional figures. Queries related to non-famous individuals include searches for names, social media handles, personal emails, or phone numbers.
            - Place: Refers to geographic locations such as cities, countries, states, tourist attractions, parks, and schools (including districts or colleges). The label should not be applied to regular businesses, unless the business has become a major point of interest.
            - Shopping: Covers queries related to purchasing tangible goods or researching products before buying. The label should not be applied to queries related to large purchases, such as cars (not auto parts) and houses, and services, such as hotel booking, movie tickets. The label applies to coupons, business-to-business (B2B) product searches, and retailers like Amazon or Walmart that do not specialize in a specific category, since these queries usually have a shopping intent.
            - Sports: Includes all organized sports (professional, college, amateur), active indoor or outdoor activities, sports-related organizations, leagues, teams, athletes, coaches, venues (arenas, stadiums), products, and events. Also covers informational sports queries (e.g., "how many innings in baseball").
            - Technology: Covers queries related to computers, software, hardware, electronic devices (e.g., smartphones, cameras), and tech-related businesses, organizations, and people (e.g., CEOs, developers). Also includes queries for tech support or programming-related topics. For companies, the label should only apply to those provide tech related services and products(Apple, Dell, IBM, etc.), not companies like Google, Facebook, and Yahoo.
            - Travel: Covers leisure or business travel, tourism services, lodging (hotels, campgrounds), destinations, transportation options (not for commuting), travel-related products, events, and organizations.
            - Others: The label is applied when the query is mostly related to identifiable topics (up to 3) apart from the labels above. For example, if the query is related to news or music, "Entertainment" would probably be applied, but the more specific topics of news or music can be conveyed through the "Others" label. Please specify the topic in the parenthesis after Others, so the label should look like "Others (music)".
           
            Further instructions: 
            You can read the examples in {golden_set} to see how categories are assigned. Apply up to 4 categories. 
            Make sure you judge based on the query and the titles. Judge the overall query, not individual elements. Fo example, the query "Barefoot in the park" is a film title and should have the category "Movie", but not "places" just because the title mentions a park.
            The titles associated to each query help provide some context on the categories involved.

            Provide as output each category and related confidence score, separated by "|". 
            Examples: 
            Input:  walmart near me,Walmart Supercenter in Mesquite, TX;Find a nearby store - Walmart.com
            Output: location_sensitivity;1|local;1|shopping;1. 

            Input: unitek outlook email,Sign In - Unitek Learning;Portal hosted on cloud - Unitek College;Outlook
            Output: navigational;1|education;1

            Input: sierra|Sierra: Shop Active & Outdoor Apparel, Footwear & Gear from ...|Clearance | Camping, Fishing, Cycling & More - Sierra
            Output: shopping:1|navigational:0,9 

            Make sure you provide as ouput only categories and scores, nothing else.  
            
            """
            )

    # Call the OpenAI API with the prompt
    response = openai.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant skilled in web searches and search query understanding"},
            {"role": "user", "content": prompt}
        ],
        model="gpt-4o-mini",
    )

    # Extract the text response from the API
    return response.choices[0].message.content


#read batch: this part reads every row in the batch (query,title;title;title) individially, and sends it to the API 
def read_batch(file_path):
    try:
        batch = []
        with open(file_path, mode='r', newline ='',encoding='utf-8') as csvfile:
            batch_reader = csv.reader(csvfile)
            
            for row in batch_reader:
                if len(row) != 2:
                    print('more than 2 values')  # Skip malformed rows
                query, titles = row
                titles_list = titles.split('|')
                batch.append({
                    "Query" : query.strip(),
                    "Titles" : titles_list
                })
            return batch
    except FileNotFoundError:
            logging.error(f"Input file {file_path} not found.")
            return []
    except Exception as e:
            logging.error(f"Error reading {file_path}: {e}")
            return []

#read guidelines. This function reads every row of the golden set. 
def read_goldenset(file_path):
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

#write output file. In the output file there is 2 values: title,APIresponse
def write_csv(file_path, data):
    try:
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Query','ALL categories']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                writer.writerow(row)
        logging.info(f"Output written to {file_path}")
    except Exception as e:
        logging.error(f"Error writing to {file_path}: {e}")


def main():
    # Paths to files:
    #  input data, output as destination folder, guidelines
    batch_file = '/Users/icelebrin/Desktop/Scripts/my-work/find/input.csv'
    output_file = '/Users/icelebrin/Desktop/Scripts/my-work/find/output.csv'
    goldenSet = '/Users/icelebrin/Desktop/Scripts/my-work/find/guidelines.csv'

    batch = read_batch(batch_file)
    if not batch:
        logging.error("No queries to process. Exiting the program.")
        return []
    goldenset = read_goldenset(goldenSet)

    result_data = []

    for batch_row in batch:
        query, titles = batch_row
        logging.info(f"Finding categories: {batch_row[query]}")
        all_categories = get_all_categories(batch_row,goldenset)
        result_data.append({'Query': batch_row[query], 'ALL categories': all_categories})

    write_csv(output_file, result_data)


if __name__ == "__main__":
    main()






