import requests
import xmltodict

def fetch_arxiv_articles(category='cs.HC', start=0, max_results=1000, sort_by='submittedDate', sort_order='descending'):
    # Define the API endpoint
    url = "http://export.arxiv.org/api/query"
    
    # PARAM UPLOAD DATE TO REFRESH DATABASE STILL NECESSARY!

    # Set up the query parameters as variables
    params = {
        'search_query': f'cat:{category}',  # Search for articles in the specified category
        'start': start,  # Starting index for results
        'max_results': max_results,  # Number of results to return
        'sortBy': sort_by,  # Sorting criteria (e.g., submission date)
        'sortOrder': sort_order  # Sorting order (e.g., descending)
    }
    
    # Make the request to the ArXiv API
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        # Parse the XML response to dict
        articles_dict = xmltodict.parse(response.content)
        return articles_dict
    else:
        return f"Error: {response.status_code}"

def parse_arxiv_response(articles_dict):
    articles = []
    entries = articles_dict["feed"]["entry"]
    
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
            "total_results": None,
            "search_query": None,
            "doi": None,  # Some entries may contain DOI, you'll need to check for its existence
            "favorites": False  # Default value
        }
        articles.append(article_data)
    
    return articles

# Fetch articles in Human-Computer Interaction category
hci_articles = fetch_arxiv_articles()
simplified_articles = parse_arxiv_response(hci_articles)

count_HC = 0
list_of_titles = []



# Check Articles and API Output
for article in simplified_articles:
    pass
    #print(article["arxiv_id"]) # (equals html link)
    #print(article["title"])
    #print(article["pdf_link"])

    if article["primary_category"] == "cs.HC":

        if article["title"] not in list_of_titles:
            list_of_titles.append(article["title"])
        else:
            print("Duplicate Alert!")
        
        count_HC += 1

    #print()

print(f"Number of Individual Titles: {len(list_of_titles)}")
print(f"Count of Checked Articles: {count_HC}")