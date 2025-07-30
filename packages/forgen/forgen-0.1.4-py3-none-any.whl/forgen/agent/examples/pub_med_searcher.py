import requests
from forgen.tool.builder import ToolBuilder


def pubmed_preprocessing(input_data):
    query = input_data["query"]
    return {"formatted_query": query.replace(" ", "+")}  # Format query for URL


def pubmed_search_function(input_data):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    search_url = f"{base_url}?db=pubmed&term={input_data['formatted_query']}&retmax=5&retmode=json"

    response = requests.get(search_url)

    if response.status_code != 200:
        return {"papers": []}  # Return an empty list if the request fails

    # Extract paper IDs from PubMed response
    paper_ids = response.json().get("esearchresult", {}).get("idlist", [])

    papers = []
    for paper_id in paper_ids:
        fetch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={paper_id}&retmode=json"
        paper_response = requests.get(fetch_url)

        if paper_response.status_code == 200:
            paper_data = paper_response.json().get("result", {}).get(paper_id, {})
            papers.append({
                "title": paper_data.get("title", "No title available"),
                "authors": paper_data.get("authors", "Unknown"),
                "summary": paper_data.get("pubdate", "No abstract available"),
                "link": f"https://pubmed.ncbi.nlm.nih.gov/{paper_id}"
            })

    return {"papers": papers}


builder = ToolBuilder(name="PubMedSearchAgent")

builder.set_description("Searches for scientific literature on PubMed, retrieving relevant articles based on medical "
                        "or life sciences queries, along with metadata like authors and abstracts.")

pubmed_search_input_schema = {"query": str}
pubmed_search_output_schema = {"papers": list}

builder.set(pubmed_search_input_schema, pubmed_search_output_schema, pubmed_search_function, preprocessor_code=pubmed_preprocessing)

pubmed_search_agent = builder.build()


if __name__ == "__main__":
    user_input = {"query": "Cancer Immunotherapy"}
    output = pubmed_search_agent.execute(user_input)
    print(f"OUTPUT: {str(output)}")
