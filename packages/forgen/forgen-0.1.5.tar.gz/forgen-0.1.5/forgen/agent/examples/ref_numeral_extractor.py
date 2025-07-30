import re
from forgen.tool.builder import ToolBuilder

# Create a ToolBuilder instance
builder = ToolBuilder(name="ReferenceNumeralExtractor")

# Define input and output schemas
extractor_input_schema = {
    'input_text': str
}
extractor_output_schema = {
    'reference_numerals': list,  # List of extracted reference numerals
    'figure_references': list    # List of extracted figure references
}


# Function to extract reference numerals from input text
def extract_reference_numerals(input_data):
    input_text = input_data.get("input_text", "")

    if not input_text:
        return {"error": "Input text is required."}

    # Regex to capture reference numerals in bold markdown **123** or XML-like <b>123</b>
    reference_numeral_patterns = [
        r'\*\*(\d+)\*\*',  # Markdown-style bold numbers
        r'<b>(\d+)</b>'   # HTML/XML bold numbers
    ]

    # Regex for figure references specifically inside <figref> tags
    figure_reference_pattern = r'<figref[^>]*>(.*?)</figref>'

    reference_numerals = set()  # Use a set to avoid duplicates
    figure_references = set()

    # Extract general reference numerals
    for pattern in reference_numeral_patterns:
        matches = re.findall(pattern, input_text)
        reference_numerals.update(matches)

    # Extract figure references separately
    figure_matches = re.findall(figure_reference_pattern, input_text)
    figure_references.update(figure_matches)

    return {
        "reference_numerals": list(reference_numerals),
        "figure_references": list(figure_references)
    }


# Add tool to the builder
builder = ToolBuilder(
    name="ReferenceNumeralExtractor",
    tool_fn=extract_reference_numerals,
    input_schema=extractor_input_schema,
    output_schema=extractor_output_schema,
    description="Extracts reference numerals from a given text, identifying numbers formatted in bold (Markdown or "
                "HTML) and categorizing figure references separately for better document parsing."
)

# Build the tool
reference_numeral_extractor_tool = builder.build()

# Example execution of the tool
if __name__ == "__main__":
    sample_input = {
        "input_text": """
        The heat sink **100** comprises a lower shell <b>102</b>, an upper shell <b>104</b>, 
        and an internal matrix **106**. See <figref idref="DRAWINGS">FIG. 2A</figref> and <figref idref="DRAWINGS">FIGS. 3B-D</figref>.
        """
    }

    # Execute the tool
    extracted_output = reference_numeral_extractor_tool.execute(sample_input)
    print(f"OUTPUT: {str(extracted_output)}")
