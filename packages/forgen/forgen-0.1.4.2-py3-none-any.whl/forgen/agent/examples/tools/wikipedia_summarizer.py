import requests
from forgen.tool.builder import ToolBuilder

# Function to fetch a summary from Wikipedia
def fetch_wikipedia_summary(input_data):
    term = input_data["term"].strip().replace(" ", "_")
    api_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{term}"

    response = requests.get(api_url)
    if response.status_code != 200:
        return {"error": "Failed to fetch data from Wikipedia"}

    data = response.json()
    if "extract" not in data:
        return {"term": term, "summary": "No summary available."}

    return {
        "term": term,
        "summary": data["extract"],
        "url": data.get("content_urls", {}).get("desktop", {}).get("page", "")
    }

# Create the Wikipedia Summary Tool
wikipedia_tool = ToolBuilder("WikipediaSummaryTool")

# Define the tool with input and output schemas
wikipedia_tool = ToolBuilder(
    name="FetchWikipediaSummary",
    tool_fn=fetch_wikipedia_summary,
    input_schema={"term": str},
    output_schema={"term": str, "summary": str, "url": str},
    description="Fetches the summary of a given term from Wikipedia."
)

# Build the tool
wikipedia_tool = wikipedia_tool.build()

# Example usage
if __name__ == "__main__":
    user_input = {"term": "Artificial intelligence"}
    output = wikipedia_tool.execute(user_input)
    print(output)
