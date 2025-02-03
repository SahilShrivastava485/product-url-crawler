import json
import os

OUTPUT_FILE = "product_urls.json"

def load_results():
    """Load previous results from the JSON file."""
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_results(domain, urls):
    """Save extracted product URLs to a JSON file."""
    results = load_results()
    results[domain] = list(urls)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=4)
