from langchain_text_splitters import RecursiveCharacterTextSplitter


def get_summary_inputs(summaries, max_token_size, chunk_overlap=0):
    summary_text = ""
    for summary in summaries:
        if isinstance(summary, dict) and "content" in summary:
            summary_text += summary["content"]
        else:
            summary_text += summary
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=max_token_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=[" ", ",", "\n", "\n\n"],
    )
    docs = text_splitter.create_documents([summary_text])
    input_texts = []
    for doc in docs:
        input_texts.append(doc.page_content)
    # print("input_texts: " + str(len(input_texts)))
    return input_texts


def is_not_sufficiently_condensed(summaries, max_token_size):
    summary_text = ""
    for summary in summaries:
        summary_text += summary + " "

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=max_token_size,
        chunk_overlap=0,
        length_function=len,
        separators=[" ", ",", "\n", "\n\n"],
    )
    docs = text_splitter.create_documents([summary_text])
    if len(docs) >= 2:
        return True
    return False
