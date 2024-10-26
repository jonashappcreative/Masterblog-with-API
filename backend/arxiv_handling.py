import os
import requests
import sqlite3
import xmltodict

from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def fetch_arxiv_articles(category='cs.HC', start=0, max_results=5, sort_by='submittedDate', sort_order='descending', published_after=None, published_before=None):
    """
    Fetches a list of articles from the ARXIV API based on specified category and other parameters.

    Parameters:
        category (str): The ARXIV category to filter articles by (default: 'cs.HC' for Human-Computer Interaction).
        start (int): The starting index for results (default: 0).
        max_results (int): Maximum number of results to return (default: 20).
        sort_by (str): Field to sort results by, e.g., 'submittedDate' (default: 'submittedDate').
        sort_order (str): Sorting order, 'ascending' or 'descending' (default: 'descending').
        published_after (str): Optional date filter for articles published after this date, format 'YYYYMMDD'.
        published_before (str): Optional date filter for articles published before this date, format 'YYYYMMDD'.

    Returns:
        dict: Parsed XML response in dictionary format if successful, or an error message string otherwise.
    """
    
    # Define the API endpoint
    url = "http://export.arxiv.org/api/query"
    
    # Build the search query
    search_query = f'cat:{category}'

    # Add the parameter to check for new articles
    if published_after:
        search_query += f"+AND+submittedDate:[{published_after}+TO+*]"
    if published_before:
        search_query += f"+AND+submittedDate:[*+TO+{published_before}]"

    # Set up the query parameters as variables
    params = {
        'search_query': f'cat:{category}',  # Search for articles in the specified category
        'start': start,  # Starting index for results
        'max_results': max_results,  # Number of results to return
        'sortBy': sort_by,  # Sorting criteria (e.g., submission date)
        'sortOrder': sort_order,  # Sorting order (e.g., descending)
    }
    
    # Make the request to the ArXiv API
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        # Parse the XML response to dict
        articles_dict = xmltodict.parse(response.content)
        return articles_dict
    else:
        return f"Error: {response.status_code}"


def clean_arxiv_response(response_dict):
    """
    Parses the ARXIV API response dictionary and extracts relevant article information.
    Might get deleted later if everything is handled through the Databse.

    Parameters:
        response_dict (dict): Dictionary of articles from ARXIV API response.

    Returns:
        articles_list: A list of dictionaries, each containing article details such as ID, title, abstract, 
              published date, updated date, primary category, and links to PDF and HTML versions.
    """

    articles_list = []
    entries = response_dict["feed"]["entry"]
    
    print(f"Number of New Articles: {len(entries)}")

    # Handle single or multiple articles in the 'entry' field
    if not isinstance(entries, list):
        entries = [entries]  # Ensure we have a list

    for entry in entries:
        article_data = {
            "arxiv_id": entry.get("id"),
            "title": entry.get("title"),
            "abstract": entry.get("summary"),
            "published": entry.get("published"),
            "updated": entry.get("updated"),
            "pdf_link": next((link["@href"] for link in entry["link"] if link.get("@title") == "pdf"), None),
            "html_link": next((link["@href"] for link in entry["link"] if link.get("@rel") == "alternate"), None),
            
            # here, cleaning is necessary. The primary cat is not always cs.HC!
            "primary_category": entry.get("arxiv:primary_category", {}).get("@term"),

            "favorites": False  # Default value
        }
        articles_list.append(article_data)
    
    return articles_list


def insert_to_database(article):
    """
    Inserts a single article into the 'articles' table.

    Parameters:
        db_path (str): Path to the SQLite database file.
        article_data (dict): Dictionary containing article information with keys:
                             'arxiv_id', 'title', 'abstract', 'published', 'updated',
                             'pdf_link', 'html_link', 'primary_category', and 'favorites'.

    """
    # Connect to the SQLite database
    conn = sqlite3.connect("hci_database.sqlite3")
    cursor = conn.cursor()

    # SQL statement to insert article data
    insert_query = """
    INSERT INTO articles (arxiv_id, title, abstract, published, updated, pdf_link, html_link, primary_category, favorites)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    # Prepare data for insertion
    article_values = (
        article['arxiv_id'],
        article['title'],
        article['abstract'],
        article['published'],
        article['updated'],
        article['pdf_link'],
        article['html_link'],
        article['primary_category'],
        False  # Default to False if 'favorites' key is not present
    )

    # Execute the insertion and commit
    cursor.execute(insert_query, article_values)
    conn.commit()

    # Close the connection
    cursor.close()
    conn.close()


def insert_articles(articles_list):
    """
    Inserts multiple articles into the 'articles' table.
    Checks each article, if it already exists in the Database.
    Parameters:
        articles_list (list): A list of dictionaries, each containing article data.
    """


    for article in articles_list:

        if article_exists(article['arxiv_id']):
            print(f"Article {article['title']} exists aready!")
            continue
        else:
            insert_to_database(article)


def article_exists(arxiv_id):
    """
    Checks if an article with a given arxiv_id already exists in the database.

    Parameters:
        db_path (str): Path to the SQLite database file.
        arxiv_id (str): The arxiv_id of the article to check.

    Returns:
        bool: True if the article exists, False otherwise.
    """
    conn = sqlite3.connect("hci_database.sqlite3")
    cursor = conn.cursor()

    query = "SELECT 1 FROM articles WHERE arxiv_id = ?"
    cursor.execute(query, (arxiv_id,))
    exists = cursor.fetchone() is not None

    cursor.close()
    conn.close()
    return exists


def refresh_database():
    
    most_recent_article_date = find_most_recent_db_entry()
    print(f"\nThe most recent article was published on: {most_recent_article_date}\n")

    # Perform a SQL Query to find the most recent article 

    # api_response = fetch_arxiv_articles(published_after=most_recent_article_date)

    api_response = fetch_arxiv_articles(published_after="202410", published_before="20241022")
    articles_list = clean_arxiv_response(api_response)
    insert_articles(articles_list)


def find_most_recent_db_entry():
    """
    Fetches the most recent published article from the 'articles' table.
    Does not handle the error when table is empty at the beginning.

    Parameters:
        db_path (str): Path to the SQLite database file.

    Returns:
        The most recent articles date in the format "YYYYMMDD"
    """
    conn = sqlite3.connect("hci_database.sqlite3")
    cursor = conn.cursor()
    
    query = """
    SELECT * FROM articles
    ORDER BY published DESC
    LIMIT 1
    """
    
    cursor.execute(query)
    most_recent_article = cursor.fetchone()
    
    cursor.close()
    conn.close()

    datetime = most_recent_article[5]
    most_recent_date = datetime[0:4] + datetime[5:7] + datetime[8:10]

    return most_recent_date


if __name__ == "__main__":
    load_dotenv()
    
    refresh_database()

    ''' WORKING CODE
    api_response = fetch_arxiv_articles()
    articles_list = clean_arxiv_response(api_response)
    insert_articles(articles_list)
    '''