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

# List of geek-centric keywords to search
search_terms = ["anime", "rpg", "video game", "dnd", "final fantasy"]
models = []

# Query loop with debugging
for term in search_terms:
    print(f"🔍 Searching for term: '{term}'")
    variables = {
        "input": {
            "q": term,
            "types": ["product"],
            "sort": "LATEST"
        }
    }

    response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)
    print(f"Status code for '{term}': {response.status_code}")

    try:
        data = response.json()
    except Exception as e:
        print(f"❌ Error parsing JSON for '{term}': {e}")
        continue

    if "errors" in data:
        print(f"⚠️ GraphQL errors for '{term}': {data['errors']}")
        continue

    nodes = data.get("data", {}).get("search", {}).get("nodes", [])
    print(f"✅ Found {len(nodes)} nodes for '{term}'")

    added = 0
    for item in nodes:
        if not item.get("downloadUrl"):
            continue
        models.append({
            "title": item["name"],
            "image": item["coverUrl"],
            "tags": [tag["name"] for tag in item.get("tags", [])],
            "link": item["downloadUrl"]
        })
        added += 1
    print(f"➕ Added {added} models for '{term}'")

# Remove duplicates
seen = set()
unique_models = []
for model in models:
    if model["link"] not in seen:
        unique_models.append(model)
        seen.add(model["link"])

print(f"🧮 Total unique models: {len(unique_models)}")

# Write to models.json
with open("models.json", "w") as f:
    json.dump(unique_models, f, indent=2)
