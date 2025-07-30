import requests
from forgen.tool.builder import ToolBuilder


def semantic_scholar_preprocessing(input_data):
    query = input_data["query"]
    return {"formatted_query": query.replace(" ", "+")}  # Format query for URL


def semantic_scholar_search_function(input_data):
    base_url = "https://api.semanticscholar.org/graph/v1/paper/search"
    search_url = f"{base_url}?query={input_data['formatted_query']}&limit=5&fields=title,authors,abstract,url"
    response = requests.get(search_url)
    if response.status_code != 200:
        return {"papers": []}
    results = response.json().get("data", [])
    papers = []
    for paper in results:
        papers.append({
            "title": paper.get("title", "No title available"),
            "authors": [author.get("name", "Unknown") for author in paper.get("authors", [])],
            "summary": paper.get("abstract", "No abstract available"),
            "link": paper.get("url", "No link available")
        })
    return {"papers": papers}


builder = ToolBuilder(name="SemanticScholarSearchAgent")

semantic_scholar_input_schema = {"query": str}
semantic_scholar_operative_input_schema = {"formatted_query": str}
semantic_scholar_output_schema = {"papers": list}
builder.set_schema(
    semantic_scholar_input_schema,
    semantic_scholar_output_schema,
    operative_input_schema=semantic_scholar_operative_input_schema
)

builder.set_code(semantic_scholar_search_function, preprocessor_code=semantic_scholar_preprocessing)

builder.set_description("Searches for research papers on Semantic Scholar, retrieving key details like abstracts, "
                        "citations, and author information based on a given query.")

semantic_scholar_search_tool = builder.build()


if __name__ == "__main__":
    user_input = {"query": "Quantum Computing"}
    output = semantic_scholar_search_tool(user_input)
    print(f"OUTPUT: {str(output)}")
