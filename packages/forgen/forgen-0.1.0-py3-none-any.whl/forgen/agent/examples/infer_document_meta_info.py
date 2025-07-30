import json
from forgen.tool.builder import ToolBuilder
from forgen.llm.openai_interface.interface import get_chat_completions_response


def gen(input_data, openai_client=None):
    response = get_chat_completions_response(
        message_history=[],
        system_content="""
You are analyzing patent-related documents. Your task is to classify the document into a predefined document type and extract a short summary and key metadata based on its content.

RETURN ONLY VALID JSON in the following format:
{
    "document_type": "<DOCUMENT_TYPE_CODE>",
    "brief_summary": "<A concise summary (2–4 sentences) of the document's content and purpose>",
    "other_metadata": {
        ... any additional useful metadata derived from the document ...
    }
}

CHOOSE ONE "document_type" VALUE FROM THE FOLLOWING DOCUMENT TYPES:

- "claims"
- "specifications"
- "drawings"
- "abstracts"
- "oa"  (Office Action)
- "non_final_rejections"
- "final_rejections"
- "restrictions"
- "responses"
- "claim_amendments"
- "spec_amendments"
- "drawing_amendments"
- "abstract_amendments"
- "preliminary_amendments"
- "amendments"
- "interview"  (Examiner Interview Summary)
- "examiner_amendments"
- "examiner_interviews"
- "restriction_responses"
- "ids"  (Information Disclosure Statement)
- "appeal"
- "pre_appeal"
- "rce"  (Request for Continued Examination)
- "issue_fee"
- "notice_of_allowance"
- "post_allowance_documents"
- "post_issuance_documents"
- "petitions"
- "pta_calculations"
- "certificates_of_correction"
- "affidavits"
- "oaths_and_declarations"
- "ads"  (Application Data Sheet or Transmittal)
- "application_part_forms"
- "fee"  (Fee worksheet)
- "assignments"
- "pre_exam_formalities"
- "bibliographic_data"
- "file_wrapper_info"
- "misc" (For anything unclear or uncategorizable)

OTHER RETURN FIELDS:

- `brief_summary`: Write a plain-language, professional summary for a patent practitioner that describes the purpose and content of the document.
- `other_metadata`: This object may contain any of the following, where relevant and discernible from the document:

    - "app_no": string of 8 digits only indicating the U.S. patent application serial number if doc is part of U.S. patent application
    - "mentions_prior_art": true/false
    - "mentions_claim_amendment": true/false
    - "references_figures": true/false
    - "examiner_name": "<name if found>"
    - "invention_field": "<subject matter like AI, biotech, mechanical, etc.>"
    - "rejection_basis": "<101 | 102 | 103 | 112 | other>" (only if Office Action)
    - "is_final_rejection": true/false (only if Office Action)
    - "doc_date": "<date if mentioned in document>"
    - "claim_count": <integer> (only if claims)
    - "figure_count": <integer> (if drawing references or figure sections)
    - "appeal_stage": "<pre-appeal | appeal | reply-brief | decision>" (if appeal)
    - "form_type": "<ads | oath | petition | etc.>" (if it’s a form)

ONLY include metadata fields that can be confidently inferred or clearly referenced in the document.

EXAMPLE OUTPUT:
{
  "document_type": "oa",
  "brief_summary": "This is a non-final Office Action rejecting claims 1–5 based on lack of novelty under 35 U.S.C. § 102. The examiner cites two prior art references and provides reasoning for each rejection.",
  "other_metadata": {
    "mentions_prior_art": true,
    "mentions_claim_amendment": false,
    "rejection_basis": "102",
    "is_final_rejection": false,
    "examiner_name": "J. Smith",
    "doc_date": "2023-08-15"
  }
}

NOW ANALYZE THE FOLLOWING DOCUMENT AND RETURN THE JSON ONLY.
""",
        user_content=f"{input_data['text_string']}",
        ai_client=openai_client,
        json_response=True
    )

    # Safely parse if needed
    if isinstance(response, str):
        try:
            response = json.loads(response)
        except json.JSONDecodeError:
            response = {}

    return response


def post(output_data):
    return {"response": output_data}


builder = ToolBuilder(name="infer_document_meta_info")

builder.set_description("Analyzes a patent-related document to classify its type and extract useful metadata")

builder.set_input_schema({
    "text_string": str
})
builder.set_output_schema({
    "response": dict
})

builder.set_generative_function(gen)
builder.set_code_output(post)

infer_document_meta_info = builder.build()
# test_input = {
#     "text_string": """
#     Claim 1. A method for training a neural network comprising: receiving input data;
#     performing a forward pass through the neural network; computing a loss function;
#     and updating network weights based on a gradient descent algorithm.
#
#     The present invention relates to improvements in artificial intelligence models,
#     specifically deep learning architectures.
#
#     FIG. 2 shows an examples implementation of the model. Prior art techniques have failed
#     to optimize training efficiency to the same degree.
#
#     The claims have been amended to clarify the scope of the invention.
#     """
# }
#
# result = infer_document_meta_info.execute(test_input)
# print(result)
