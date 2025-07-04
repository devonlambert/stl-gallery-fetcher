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

# GraphQL query: fetch user’s own models
graphql_query = {
    "query": '''
    {
      myself {
        creationsBatch(limit: 50, offset: 0) {
          results {
            name(locale: EN)
            url(locale: EN)
            illustrationImageUrl
            downloadsCount
            viewsCount
            totalSalesAmount(currency: USD) { cents }
            blueprints {
              fileUrl
              imageUrl
            }
          }
        }
      }
    }
    '''
}

# Fetch the data
print("📡 Sending request to Cults3D API...")
response = requests.post(url, json=graphql_query, headers=headers)
print(f"📬 Status Code: {response.status_code}")

try:
    data = response.json()
except Exception as e:
    print(f"❌ Failed to parse JSON: {e}")
    print(response.text)
    exit(1)

if "errors" in data:
    print(f"⚠️ GraphQL Errors: {data['errors']}")
    exit(1)

creations = data.get("data", {}).get("myself", {}).get("creationsBatch", {}).get("results", [])
print(f"✅ Retrieved {len(creations)} creations")

# Parse into models.json format
models = []
for item in creations:
    models.append({
        "title": item.get("name"),
        "image": item.get("illustrationImageUrl"),
        "tags": ["my creations"],  # Placeholder tag
        "link": item.get("url"),
        "downloads": item.get("downloadsCount", 0),
        "views": item.get("viewsCount", 0),
        "sales_cents": item.get("totalSalesAmount", {}).get("cents", 0),
        "stl_file_url": item.get("blueprints", [{}])[0].get("fileUrl"),
        "stl_image_url": item.get("blueprints", [{}])[0].get("imageUrl")
    })

# Write to models.json
print(f"💾 Writing {len(models)} models to models.json")
with open("models.json", "w") as f:
    json.dump(models, f, indent=2)

print("✅ Done.")
