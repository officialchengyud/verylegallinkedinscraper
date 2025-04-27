import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Debug: Print the API key (first few characters only for security)
api_key = os.getenv('APOLLO_API_KEY')

# First, let's verify the API key and check what access we have
verify_url = "https://api.apollo.io/api/v1/auth/health"
headers = {
    "accept": "application/json",
    "Cache-Control": "no-cache",
    "Content-Type": "application/json",
    "x-api-key": api_key
}

url = "https://api.apollo.io/api/v1/people/search"

# API parameters should be in the request body
data = {
    "person_titles": ["Sales Manager", "Go to Market Manager", "Sales", "Business Development"],
    "include_similar_titles": True,
    "person_locations": ["New York"],
    "person_seniorities": ["vp", "head", "director", "manager", "senior"],
    "q_keywords": "Asian Food Tech",
    "page": 1,
    "per_page": 5  # Keep this at 5 for now to avoid running out of credits
}

response = requests.post(url, headers=headers, json=data)

print(response.text)

#Company search

# url = "https://api.apollo.io/api/v1/mixed_companies/search"

# headers = {
#     "accept": "application/json",
#     "Cache-Control": "no-cache",
#     "Content-Type": "application/json"
# }

# response = requests.post(url, headers=headers)

# print(response.text)