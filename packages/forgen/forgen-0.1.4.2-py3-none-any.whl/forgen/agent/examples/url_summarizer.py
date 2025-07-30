from forgen.tool.builder import ToolBuilder
from forgen.llm.openai_interface.interface import get_chat_completions_response
import requests
from bs4 import BeautifulSoup


def url_preprocessing(input_data):
    url = input_data['url']
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        text_content = soup.get_text()
        return {'formatted_input': text_content}
    except requests.exceptions.RequestException as e:
        return {'formatted_input': f"Error fetching URL content: {str(e)}"}


def url_summarizer_generation_function(input_data, openai_client=None):
    # Call OpenAI's API to generate the summary
    response = get_chat_completions_response(
        message_history=[],
        system_content="SUMMARIZE THIS URL INTO A JSON WITH OUTPUT SCHEMA: {{'summary_text': summary_text}} where " +
                       "summary_text is a string that is your response.",
        user_content=input_data["formatted_input"],
        username="",
        json_response=True,
        ai_client=openai_client
    )
    return response


builder = ToolBuilder(name="URLSummarizerAgent")

url_summarizer_input_schema = {'url': str}
url_summarizer_generation_input_schema = {'formatted_input': str}
url_summarizer_output_schema = {'summary_text': str}

builder.set_description("Fetches and summarizes the content of a given URL, extracting key points and structuring the "
                        "information in a concise, readable format.")


builder.set(
    url_summarizer_input_schema,
    url_summarizer_output_schema,
    url_summarizer_generation_function,
    preprocessor_code=url_preprocessing,
    operative_input_schema=url_summarizer_generation_input_schema)

url_summarizer_agent = builder.build()


if __name__ == "__main__":
    user_input = {
        "url": "https://en.wikipedia.org/wiki/United_States_Patent_and_Trademark_Office"
    }
    generated_summary_output = url_summarizer_agent.execute(user_input)
    print(f"OUTPUT: {str(generated_summary_output)}")
