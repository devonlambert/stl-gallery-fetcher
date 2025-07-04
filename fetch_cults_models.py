import requests
import json
import os
import base64

# Prepare Basic Auth Header
username = os.getenv("CULTS_API_USERNAME")
password = os.getenv("CULTS_API_KEY")

if not username or not password:
    print("❌ CULTS_API_USERNAME or CULTS_API_KEY is missing.")
    exit(1)

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

# Keywords to search for
search_terms = ["anime", "rpg", "video game", "dnd", "final fantasy"]
models = []

# Query loop with debug output
for term in search_terms:
    print(f"\n🔍 Searching for term: '{term}'")
    
    graphql_query = {
        "query": f'''
        query {{
          search(query: "{term}", type: PRODUCT, sort: LATEST) {{
            id
            name
            slug
            coverUrl
            tags {{
              name
            }}
            downloadUrl
          }}
        }}
        '''
    }

    try:
        response = requests.post(url, json=graphql_query, headers=headers)
        print(f"Status code for '{term}': {response.status_code}")
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

    results = data.get("data", {}).get("search", [])
    print(f"✅ Found {len(results)} items for '{term}'")

    added = 0
    for item in results:
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

print(f"\n🧮 Total unique models: {len(unique_models)}")

# Save to models.json
with open("models.json", "w") as f:
    json.dump(unique_models, f, indent=2)
