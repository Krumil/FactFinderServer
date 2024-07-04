import requests
from langchain_core.tools import tool


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
    url = f"https://factchecktools.googleapis.com/v1alpha1/claims:search"
    params = {"query": query, "key": api_key, "languageCode": language_code}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        claims = data.get("claims", [])
        results = []
        for claim in claims:
            text = claim.get("text", "")
            claimant = claim.get("claimant", "")
            review = claim.get("claimReview", [])
            if review:
                publisher = review[0].get("publisher", {}).get("name", "")
                review_rating = review[0].get("textualRating", "")
                result = f"Claim: {text}\nClaimant: {claimant}\nReviewed by: {publisher}\nRating: {review_rating}\n"
                results.append(result)
        return "\n".join(results) if results else "No fact check results found."
    else:
        return "Failed to fetch data from Google Fact Check API."


# Example usage
api_key = "your_api_key_here"
query = "The Great Wall of China can be seen from the moon."
result = check_fact(query, api_key)
print(result)
