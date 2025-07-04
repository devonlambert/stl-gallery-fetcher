import requests
import json
import os
import base64

# Prepare Basic Auth Header
username = os.getenv("CULTS_API_USERNAME")
password = os.getenv("CULTS_API_KEY")

credentials = f"{username}:{password}"
encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")

headers = {
    "Authorization": f"Basic {encoded_credentials}",
    "Content-Type": "application/json"
}

print(f"🔐 Using Basic Auth with username: {username}")
print(f"🧾 Encoded credentials (truncated): {encoded_credentials[:10]}...")

# GraphQL endpoint
url = "https://cults3d.com/graphql"

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

# Keywords to search for
search_terms = ["anime", "rpg", "video game", "dnd", "final fantasy"]
models = []

# Query loop with debug output
for term in search_terms:
    print(f"🔍 Searching for term: '{term}'")
    variables = {
        "input": {
            "q": term,
            "types": ["product"],
            "sort": "LATEST"
        }
    }

    try:
        response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)
        print(f"Status code for '{term}': {response.status_code}")
        if response.status_code == 401:
            print(f"❌ Unauthorized access. Headers sent: {headers}")
            print(f"🔓 Raw response for '{term}':\n{response.text}")
    except Exception as e:
        print(f"❌ Request failed for '{term}': {e}")
        continue

    try:
        data = response.json()
    except Exception as e:
        print(f"❌ Error parsing JSON for '{term}': {e}")
        print(f"🧾 Raw response text:\n{response.text}")
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

# Save to models.json
with open("models.json", "w") as f:
    json.dump(unique_models, f, indent=2)
