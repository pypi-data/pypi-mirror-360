import feedparser
from forgen.tool.builder import ToolBuilder


def arxiv_preprocessing(input_data):
    query = input_data["query"]
    return {"formatted_query": query.replace(" ", "+")}  # Format query for URL


def arxiv_search_function(input_data):
    base_url = "http://export.arxiv.org/api/query?search_query="
    search_url = f"{base_url}{input_data['formatted_query']}&start=0&max_results=5"
    feed = feedparser.parse(search_url)
    papers = []
    for entry in feed.entries:
        papers.append({
            "title": entry.title,
            "authors": [author.name for author in entry.authors],
            "summary": entry.summary,
            "link": entry.link
        })
    return {"papers": papers}


builder = ToolBuilder(name="arXivSearchAgent")

builder.set_description("Searches for academic papers on arXiv based on a given query, retrieving relevant metadata "
                        "such as title, authors, abstract, and publication date.")
arxiv_search_input_schema = {"query": str}
arxiv_search_output_schema = {"papers": list}

builder.set(arxiv_search_input_schema, arxiv_search_output_schema, arxiv_search_function,
            preprocessor_code=arxiv_preprocessing,
            operative_input_schema={"formatted_query": str},
            )

arxiv_search_agent = builder.build()


if __name__ == "__main__":
    user_input = {"query": "RLHF LORA"}
    output = arxiv_search_agent.execute(user_input)
    print(f"OUTPUT: {str(output)}")
