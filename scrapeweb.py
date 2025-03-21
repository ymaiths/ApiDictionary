import serpapi
import os
import re
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables
load_dotenv()
api_key = os.getenv('SERPAPI_KEY')
client = serpapi.Client(api_key=api_key)

# Function to scrape webpage content
def scrape_webpage(url, keyword):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extract all text
            text = soup.get_text(separator=" ", strip=True)
            
            # Find the keyword and extract the text after it
            if keyword in text:
                extracted_text = text[text.find(keyword):]  # Extract from keyword onwards
                return extracted_text[:500]  # Limit to 500 chars for readability
            else:
                return None
        else:
            return None
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def scrape(slang,num="10",clarify_search=" ภาษาวัยรุ่น"):
    extracted_results = []
    # Search query
    result = client.search(
        q= slang+clarify_search,
        engine="google",
        hl="th",
        gl="th",
        num=num,  # Reduce for testing (change as needed)
        filter=0
    )

    # Define the keyword to search for
    start_keyword = slang  # Change this to the keyword you want

    # Iterate through search results
    for index,item in enumerate(result.get("organic_results", [])):
        snippet = item.get("snippet", "No snippet available")
        link = item.get("link")
        source = item.get("source")

        # If the keyword is in the snippet, extract from there
        if start_keyword in snippet:
            extracted_snippet = snippet[snippet.find(start_keyword):]
        else:
            # If the keyword is missing, scrape the webpage
            extracted_snippet = scrape_webpage(link, start_keyword)
        if extracted_snippet is not None:
            extracted_results.append({
                # "index": index,
                # "position": item["position"],
                "extracted_snippet": extracted_snippet if extracted_snippet else "Keyword not found on page"
            })
    return slang,extracted_results

print(scrape("จึ้ง"))
