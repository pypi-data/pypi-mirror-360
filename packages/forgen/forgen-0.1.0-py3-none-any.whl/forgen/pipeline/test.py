from forgen.agent.examples.text_gloss_generator import text_gloss_generator_tool
from forgen.agent.examples.tools.batch_tool_processor import batch_processor_tool
from forgen.agent.examples.tools.list_to_string import list_to_string_tool
from forgen.agent.examples.url_summarizer import url_summarizer_agent
from forgen.pipeline.pipeline import MultiPathPipeline
from forgen.pipeline.item import PipelineItem
from forgen.pipeline.builder import MultiPathPipelineBuilder


# --- Construct the Pipeline ---
builder = MultiPathPipelineBuilder()

# Batch process the list of URLs with the URL summarizer agent
builder.add_item(PipelineItem("0", batch_processor_tool))

# Each summary should be passed to the text gloss generator
builder.add_item(PipelineItem("1", text_gloss_generator_tool))

# Format the final output as a structured string
builder.add_item(PipelineItem("2", list_to_string_tool))

# Define the execution order in the pipeline
builder.add_engine_tuple("0", "1")  # Process URLs → Summarize each
builder.add_engine_tuple("1", "2")  # Summarized results → Format output

if __name__ == "__main__":

    # Build the pipeline
    pipeline_object = builder.build()
    pipeline = MultiPathPipeline(pipeline_object)

    # --- Run the Pipeline ---
    input_data = {
        "items": [
            "https://en.wikipedia.org/wiki/United_States_Patent_and_Trademark_Office",
            "https://en.wikipedia.org/wiki/NASA",
            "https://en.wikipedia.org/wiki/Artificial_intelligence"
        ],
        "agent": url_summarizer_agent
    }

    url_summarizer_agent.set_forced_interface(True)

    # final_output = pipeline.execute(input_data)

    # Print final structured result
    # print(f"\nFINAL OUTPUT: \n{final_output}")

    builder = MultiPathPipelineBuilder()
    builder.add_item(PipelineItem("0", url_summarizer_agent))
    builder.add_item(PipelineItem("1", text_gloss_generator_tool))
    builder.add_item(PipelineItem("2", list_to_string_tool))
    builder.add_engine_tuple("0", "1")
    builder.add_engine_tuple("1", "2")
    pipeline_object = builder.build()
    pipeline = MultiPathPipeline(pipeline_object)

    output = pipeline.execute({"url": "https://en.wikipedia.org/wiki/United_States_Patent_and_Trademark_Office"})
    print(f"FINAL OUTPUT: {str(output)}")