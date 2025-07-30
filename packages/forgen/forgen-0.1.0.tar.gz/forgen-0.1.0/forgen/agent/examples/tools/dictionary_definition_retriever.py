import requests
from forgen.tool.builder import ToolBuilder

# Function to fetch word definitions from Merriam-Webster API
def fetch_word_definition(input_data):
    word = input_data["word"].strip().lower()
    api_key = "30a07727-45e9-4aec-bbd6-501af9db04db"  # Your API key
    api_url = f"https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key={api_key}"

    response = requests.get(api_url)
    if response.status_code != 200:
        return {"error": "Failed to fetch data from API"}

    data = response.json()
    if not data or isinstance(data[0], str):  # Handles cases where suggestions are returned instead of definitions
        return {"word": word, "definitions": [], "phonetics": [], "examples": []}

    definitions, phonetics, examples = [], [], []

    for entry in data:
        if not isinstance(entry, dict):
            continue

        definitions.extend(entry.get("shortdef", []))

        if "hwi" in entry and "prs" in entry["hwi"]:
            phonetics.extend([pron["mw"] for pron in entry["hwi"]["prs"] if "mw" in pron])

        if "def" not in entry:
            continue

        for sense in entry["def"]:
            if "sseq" not in sense:
                continue

            for seq in sense["sseq"]:
                for sense_entry in seq:
                    if not (isinstance(sense_entry, list) and len(sense_entry) > 1):
                        continue

                    sense_data = sense_entry[1]
                    if "dt" not in sense_data:
                        continue

                    for dt in sense_data["dt"]:
                        if dt[0] == "vis":
                            examples.extend([vis["t"] for vis in dt[1] if "t" in vis])

    return {
        "word": word,
        "definitions": definitions,
        "phonetics": phonetics,
        "examples": examples
    }


# Define the tool with input and output schemas
dictionary_tool = ToolBuilder(
    name="FetchWordDefinition",
    tool_fn=fetch_word_definition,
    input_schema={"word": str},
    output_schema={"word": str, "definitions": list, "phonetics": list, "examples": list},
    description="Fetches the definition, phonetics, and examples usage of a given word from the Merriam-Webster API."
)

# Build the tool
dictionary_tool = dictionary_tool.build()

# Example usage
if __name__ == "__main__":
    user_input = {"word": "test"}  # Example word lookup
    output = dictionary_tool.execute(user_input)
    print(output)
