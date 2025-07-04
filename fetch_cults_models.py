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

# Keywords to search
search_terms = ["anime", "rpg", "video game", "dnd", "final fantasy"]
models = []

# Loop through search terms and collect data
for term in search_terms:
    print(f"\n🔍 Searching for public models with term: '{term}'")

    graphql_query = {
        "query": f'''
        {{
          creationsSearchBatch(query: "{term}", limit: 20) {{
            total
            results {{
              name(locale: EN)
              description(locale: EN)
              shortUrl
              illustrationImageUrl
              downloadsCount
              viewsCount
            }}
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
        print(f"❌ Failed to parse JSON for '{term}': {e}")
        print(f"🧾 Raw response text:\n{response.text}")
        continue

    if "errors" in data:
        print(f"⚠️ GraphQL errors for '{term}': {data['errors']}")
        continue

    results = data.get("data", {}).get("creationsSearchBatch", {}).get("results", [])
    print(f"✅ Found {len(results)} models for '{term}'")

    added = 0
    for item in results:
        models.append({
            "title": item.get("name"),
            "description": item.get("description"),
            "image": item.get("illustrationImageUrl"),
            "link": item.get("shortUrl"),
            "tags": [term],
            "downloads": item.get("downloadsCount", 0),
            "views": item.get("viewsCount", 0)
        })
        added += 1
    print(f"➕ Added {added} models for '{term}'")

# Deduplicate by link
seen = set()
unique_models = []
for m in models:
    if m["link"] not in seen:
        unique_models.append(m)
        seen.add(m["link"])

print(f"\n🧮 Final unique models: {len(unique_models)}")

# Write to models.json
with open("models.json", "w") as f:
    json.dump(unique_models, f, indent=2)

print("✅ models.json written.")
