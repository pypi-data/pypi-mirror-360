import importlib
import requests


def test_tool(name, input_data, fn=None):
    try:
        print(f"▶ Testing {name}...")

        if fn:
            tool = fn
        else:
            module = importlib.import_module(f"forgen.agent.examples.{name}")
            if hasattr(module, 'execute'):
                tool = module.execute
            else:
                tool = getattr(module, name).execute
        result = tool(input_data)
        print(f"✅ {name} passed\nOutput: {result}\n")
    except Exception as e:
        print(f"❌ {name} failed with error: {e}\n")


# ----------------------------
# URL Fetcher Implementation
# ----------------------------
def fetch_url_text(input_data: dict) -> dict:
    """
    Given an input dict with a key 'url', fetch the text content from that URL.
    :param input_data: A dictionary containing the key 'url'.
    :return: A dictionary with key 'text' containing the fetched content.
    """
    url = input_data.get("url")
    if not url:
        raise ValueError("Input data must contain a 'url' key.")
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad responses
    return {"text": response.text}


def preprocessing_fn(input_data: dict) -> dict:
    """
    Preprocessing: Ensure the URL starts with 'http://' or 'https://'.
    """
    url = input_data.get("url", "")
    if not (url.startswith("http://") or url.startswith("https://")):
        input_data["url"] = "http://" + url
    return input_data


def postprocessing_fn(output_data: dict) -> dict:
    """
    Postprocessing: Trim whitespace from the fetched text.
    """
    if "text" in output_data:
        output_data["text"] = output_data["text"].strip()
    return output_data


if __name__ == "__main__":

    print("🧪 Running basic tests...\n")

    # === TEST CASES ===

    test_tool("antecedent_basis_checker", {
        "text": "A widget includes a frame. The bracket is attached to the frame.",
        "term": "bracket"
    })

    test_tool("claim_support_finder_node", {
        "claim_text": "A sensor configured to detect temperature.",
        "spec_text": "The temperature sensor may be a thermistor.",
        "target_phrase": "sensor"
    })

    test_tool("dependent_claim_generator_node", {
        "independent_claim": "A display system comprising a screen and a housing.",
        "spec_text": "The housing may include an aluminum frame or a plastic case."
    })

    test_tool("claim_parser_tool", {
        "claim_text": "A processor configured to perform image recognition."
    })

    test_tool("oa_section_classifier_tool", {
        "oa_text": "Claim 1 is rejected under § 102 as being anticipated by Smith. Claim 2 is rejected under § 103 over Smith and Lee."
    })

    test_tool("oa_claim_reference_mapper_tool", {
        "claim_text": "A device including a battery and a charging port.",
        "oa_rejection_text": "Smith shows a battery at col. 4, lines 10–20. Charging port not found."
    })

    test_tool("reference_summarizer_node", {
        "reference_text": "Smith discloses a thermal control system using a fan and heat sink."
    })

    test_tool("oa_report_generator_node", {
        "oa_text": "Claims 1–3 are rejected under § 103.",
        "filing_data": {
            "app_number": "16/888,888",
            "filing_date": "2022-01-01",
            "response_due_date": "2024-05-10",
            "oa_type": "Final",
            "examiner_name": "John Doe",
            "art_unit": "2123"
        },
        "client_preferences": {
            "include_recommendation": True,
            "tone": "bullet-points"
        }
    })

    test_tool("boilerplate_inserter_tool", {
        "template_type": "103_argument",
        "inserts": {
            "limitation": "sensor array",
            "missing_feature": "overlapping field of view"
        }
    })

    test_tool("legal_argument_strategy_node", {
        "rejection_type": "§ 103",
        "claim_element": "control module",
        "prior_art_excerpt": "Smith discloses a control system but lacks modular architecture.",
        "rejection_text": "Claims 1–2 are rejected under § 103 over Smith and Jones."
    })

    test_tool("claim_amendment_generator_node", {
        "claim_text": "A wearable device comprising a strap.",
        "oa_text": "Rejected under § 103 over Smith.",
        "prior_art_text": "Smith discloses a wearable device but not a strap made of elastic."
    })

    test_tool("examiner_data_tool", {
        "examiner_name": "John Smith",
        "art_unit": "2134"
    })


    # batch_text_processor = ToolBuilder("BatchTextProcessor")
    # batch_text_processor = ToolBuilder(
    #     tool_name="BatchProcessor",
    #     tool_fn=text_gloss_generator_tool,  # Pass the agent directly
    #     input_schema={"texts": list},  # No batch_mode in schema
    #     output_schema={"batch_results": list},  # Expect a list of results
    #     forced_interface=True,
    #     batch_mode=True  # Pass batch_mode separately
    # )
    # batch_text_processor = batch_text_processor.build()

    # # Sample batch input
    # batch_input_data = {
    #     "texts": [
    #         "Artificial intelligence is evolving rapidly.",
    #         "Deep learning models require large datasets.",
    #         "Reinforcement learning is used in robotics."
    #     ]
    # }

    # # Execute batch processing
    # batch_results = batch_text_processor.execute(batch_input_data)

    # # Print the results
    # print("Batch Processing Results:", batch_results)




    # # Define the input and output schemas.
    # # Input: a dict with a 'url' key.
    # input_schema = {"url": str}
    # # Output: a dict with a 'text' key.
    # output_schema = {"text": str}
    #
    # # Create the ToolBuilder instance.
    # tool_builder = ToolBuilder(tool_name="URLFetcher", input_schema=input_schema, output_schema=output_schema)
    #
    # # Configure the tool using the URL fetcher function and our optional pre/post-processing.
    # tool_builder = ToolBuilder(
    #     tool_fn=fetch_url_text,
    #     input_schema=input_schema,
    #     output_schema=output_schema,
    #     preprocessing=preprocessing_fn,
    #     postprocessing=preprocessing_fn
    # )
    #
    # # Build the tool.
    # url_fetcher_tool = tool_builder.build()
    #
    # # Example input: a URL to fetch.
    # input_data = {"url": "forgen.ai"}  # Notice the missing 'http://' will be fixed by preprocessing.
    #
    # # Run the tool.
    # try:
    #     result = url_fetcher_tool.execute(input_data)
    #     print("Fetched content (first 500 characters):")
    #     print(result["text"][:500])
    # except Exception as e:
    #     print("Error:", e)
