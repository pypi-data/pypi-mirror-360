def get_drawing_summary_prompt():
    return "Summarize any information from the drawings that may be useful in answering the user prompt"


def get_augmentative_data_prompt(system_content, augmentative_data):
    return f"BASED ON THE FOLLOWING PROMPT AND ANY AUGMENTATIVE_DATA PROVIDED, PROVIDE A NEW OR (IF AUGMENTATIVE_DATA PRESENT) AN UPDATED JSON THAT ANSWERS THE PROMPT USING ANY USER INFO PROVIDED:  PROMPT: {system_content};\n\nAUGMENTATIVE_DATA: {augmentative_data}"


def get_summary_of_images_text_with_prompt(summary_of_images):
    return f"\n\nHere is a summary of the drawings/images for use in answering my prompt above: {summary_of_images}"
