import requests
import json
import os

# Endpoint and headers
url = "https://cults3d.com/graphql"
headers = {
    "Authorization": f"Bearer {os.getenv('CULTS_API_KEY')}",
    "Content-Type": "application/json"
}

# GraphQL query
query = '''
query Search($input: SearchInput!) {
  search(input: $input) {
    nodes {
      ... on Product {
        id
        name
        slug
        coverUrl
        tags {
          name
        }
        downloadUrl
      }
    }
  }
}
'''

# Broader list of geek-centric keywords
search_terms = ["anime", "rpg", "video game", "dnd", "final fantasy"]
models = []

# Query loop
for term in search_terms:
    variables = {
        "input": {
            "q": term,
            "types": ["product"],
            "sort": "LATEST"
        }
    }

    response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)
    data = response.json()

    for item in data.get("data", {}).get("search", {}).get("nodes", []):
        if not item.get("downloadUrl"):
            continue
        models.append({
            "title": item["name"],
            "image": item["coverUrl"],
            "tags": [tag["name"] for tag in item.get("tags", [])],
            "link": item["downloadUrl"]
        })

# Remove duplicates by downloadUrl
seen = set()
unique_models = []
for model in models:
    if model["link"] not in seen:
        unique_models.append(model)
        seen.add(model["link"])

# Write final JSON
with open("models.json", "w") as f:
    json.dump(unique_models, f, indent=2)