from dotenv import load_dotenv
from langchain_core.tools import tool
import json
import os
import requests

load_dotenv()

google_fact_check_api_key = os.getenv("GOOGLE_FACT_CHECK_API_KEY")

@tool
def check_fact(query: str, language_code="en") -> str:
    """
    Query the Google Fact Check API to verify the factual content of the given text.

    Args:
    - query: The text content to verify.
    - language_code: Language of the query (default is English).

    Returns:
    - A string summary of the fact-check results.
    """
    url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
    params = {"query": query, "languageCode": language_code, "key": google_fact_check_api_key}
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = json.loads(response.text)
        claims = data.get("claims", [])
        results = []
        for claim in claims:
            text = claim.get("text", "")
            # claimant = claim.get("claimant", "")
            review = claim.get("claimReview", [])
            if review:
                publisher = review[0].get("publisher", {}).get("name", "")
                review_rating = review[0].get("textualRating", "")
                result = f"Claim: {text}\nReviewed by: {publisher}\nRating: {review_rating}\n"
                results.append(result)
        return "\n".join(results) if results else "No fact check results found."
    else:
        return f"Failed to fetch data from Google Fact Check API. Status code: {response.status}"


@tool
def check_news(query: str) -> str:
    """
    Query the GDELT API to get the latest news articles related to the given query.

    Args:
    - query: The text content to search for in news articles.

    Returns:
    - A string summary of the top news articles.
    """
    url = "https://api.gdeltproject.org/api/v2/doc/doc?query={}&format=json".format(query)
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        articles = data.get("articles", [])
        results = []
        for article in articles:
            title = article.get("title", "No title")
            description = article.get("seendescription", "No description")
            source = article.get("source", "Unknown source")
            url = article.get("url", "")
            result = f"Title: {title}\nDescription: {description}\nSource: {source}\nURL: {url}\n"
            results.append(result)
        return "\n".join(results) if results else "No news articles found."
    else:
        return f"Failed to fetch data from GDELT API. Status code: {response.status_code}"
