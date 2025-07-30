# 📘 **Forgen API - For Generative AI Interfacing**


# 📘 **Forgen - Agent Package Documentation**

## Overview
The `forgen.agent` package provides a modular and structured way to build AI-driven agents by defining **GenerativeNodes**, connecting them into **Agents**, and constructing tools that interact within this system.

This package includes:
- **`AgentBuilder`** - Constructs agents by chaining different phases together.
- **`ToolBuilder`** - Creates tools with input/output processing.
- **`Agent`** - Represents a sequence of `GenerativeNode` objects.
- **`AgentPipeline`** - Manages execution flow and dependencies.
- **`Tool`** - A modular processing unit akin to an agent.

---

## 📌 **Modules**

### **1️⃣ `builder.py`** - Agent and Tool Construction
This module provides `AgentBuilder` and `ToolBuilder` classes to construct AI-driven agent architectures.

#### 🏗️ **Class: `AgentBuilder`**
Builds an agent by defining a sequence of **GenerativeNodes**, where each node consists of:
- `InputPhase` (Preprocessing)
- `GenerationPhase` (AI/Processing)
- `OutputPhase` (Postprocessing)

##### 🔹 **`__init__(agent_name: str, openai_client=None)`**
**Initializes the agent builder.**
- `agent_name (str)`: Name of the agent.
- `openai_client (Optional)`: OpenAI client for text generation (if applicable).

##### 🔹 **`set_global_input_schema(input_schema: dict)`**
Sets the input schema for the entire agent.

##### 🔹 **`set_global_output_schema(output_schema: dict)`**
Sets the output schema for the entire agent.

##### 🔹 **`add_node(...)`**
Adds a **processing node** to the agent.
- `generation_function (callable)`: Function to generate output.
- `code_input (callable, optional)`: Function for input preprocessing.
- `code_output (callable, optional)`: Function for output postprocessing.
- `input_data (dict, optional)`: Initial input data.
- `generation_input_schema (dict, optional)`: Schema for generation input.
- `generation_output_schema (dict, optional)`: Schema for generation output.
- `max_tries (int, optional)`: Retry attempts for generation.

##### 🔹 **`build() -> Agent`**
Constructs the agent and returns an instance of `Agent`.

---

#### 🛠️ **Class: `ToolBuilder`**
Builds a **Tool**, which is a modular processing unit for the agent.

##### 🔹 **`__init__(tool_name: str = None, input_schema: dict = None, output_schema: dict = None)`**
Initializes a tool with optional schemas.

##### 🔹 **`set_tool(...)`**
Defines a tool's core behavior.
- `tool_fn (callable)`: Function to be executed.
- `input_schema (dict)`: Expected input structure.
- `output_schema (dict)`: Expected output structure.
- `preprocessing (callable, optional)`: Function for preprocessing.
- `postprocessing (callable, optional)`: Function for postprocessing.
- `forced_interface (bool, optional)`: Enforce schema validation.

##### 🔹 **`build() -> Tool`**
Constructs and returns a `Tool`.

---

### **2️⃣ `agent.py`** - Core Agent Execution

#### 🤖 **Class: `Agent`**
An **Agent** is a collection of **GenerativeNodes** that process data sequentially.

##### 🔹 **`__init__(agent_name: str, agent_nodes: List[GenerativeNode])`**
Initializes an agent with:
- `agent_name (str)`: Name of the agent.
- `agent_nodes (List[GenerativeNode])`: Ordered nodes to be executed.

##### 🔹 **`execute(input_data: dict = None) -> list`**
Executes the agent sequentially, processing data through all nodes.

---

### **3️⃣ `node.py`** - Node Definition

Defines an **GenerativeNode**, which consists of:
- `InputPhase`
- `GenerationPhase`
- `OutputPhase`

Each **node** processes input → generates output → formats output.

---

### **4️⃣ `tool.py`** - Tool Execution and Processing

#### 🛠 **Class: `Tool`**
A **Tool** is a modular processing unit that follows the same structure as an agent but operates as a single component.

##### 🔹 **`__init__(...)`**
Initializes a `Tool` with input, operation, and output phases.
- `input (InputPhase)`: Preprocessing step.
- `operation (OperativePhase)`: Core function execution.
- `output (OutputPhase)`: Postprocessing step.
- `input_schema (dict)`: Schema for input validation.
- `output_schema (dict)`: Schema for output validation.
- `forced_interface (bool)`: Whether to allow schema-based mapping.

##### 🔹 **`execute(input_data: dict) -> dict`**
Processes data through the input, operation, and output phases.

---

#### 📌 **Class: `InputPhase`**
Handles input validation and preprocessing.

##### 🔹 **`process_input() -> dict`**
Validates input and applies preprocessing.

---

#### 📌 **Class: `OperativePhase`**
Handles the main function execution.

##### 🔹 **`use_tool() -> dict`**
Executes the tool's primary function and returns output.

---

#### 📌 **Class: `OutputPhase`**
Handles output validation and postprocessing.

##### 🔹 **`format_output() -> dict`**
Applies postprocessing and validates output.

---

### **5️⃣ `pipeline/agent_pipeline.py`** - Pipeline Execution

#### 🔄 **Class: `AgentPipeline`**
Manages dependencies and execution order of `GenerativeNodes`.

##### 🔹 **`__init__(pipeline_object: dict)`**
Initializes a pipeline with an agent definition.

##### 🔹 **`execute(input_data: dict)`**
Runs the pipeline by resolving dependencies and executing nodes.

---

### **6️⃣ `pipeline/builder.py`** - Pipeline Construction

#### 🏗 **Class: `PipelineBuilder`**
Builds a **Pipeline**, which connects multiple `GenerativeNodes` in a structured sequence.

##### 🔹 **`set_master_input(master_input: dict)`**
Defines the initial input data for the pipeline.

##### 🔹 **`add_item(item: PipelineItem)`**
Adds an item (processing unit) to the pipeline.

##### 🔹 **`add_engine_tuple(source: str, target: str)`**
Defines a processing flow between pipeline components.

##### 🔹 **`build() -> dict`**
Constructs and returns a pipeline definition.

---

### **7️⃣ `pipeline/item.py`** - Pipeline Components

#### 🔹 **Class: `BaseModule`**
Abstract base class defining a pipeline component interface.

##### **Abstract Methods:**
- `input_schema`
- `output_schema`
- `execute()`

#### 🔹 **Class: `PipelineItem`**
Encapsulates an agent or tool as a component in a pipeline.

##### 🔹 **`__init__(id: str, agent_or_tool: BaseModule, ...)`**
Initializes a `PipelineItem` with:
- `id (str)`: Unique identifier.
- `agent_or_tool (BaseModule)`: An agent or tool to execute.
- `cust_input_schema (dict, optional)`: Custom input schema.
- `cust_output_schema (dict, optional)`: Custom output schema.

##### 🔹 **`execute(input_data: dict = None) -> dict`**
Executes the agent/tool with the given input.

---

## 🎯 **Usage Example: Creating an Agent**

```python
from forgen.tool.builder import AgentBuilder

# Initialize the AgentBuilder
builder = AgentBuilder(agent_name="TextProcessor")

# Define global schemas
builder.set_input_schema({"text": str})
builder.set_global_output_schema({"summary": str})


# Define generation function
def summarize_text(input_data):
    text = input_data["text"]
    return {"summary": text[:100]}  # Simple truncation


# Add processing node
builder.create_and_add_gen_node(generative_function=summarize_text)

# Build the agent
agent = builder.build()

# Execute the agent
result = agent.execute({"text": "This is a long article that needs summarization."})
print(result)  # {'summary': 'This is a long article that needs summarization.'}
```

---

This documentation provides a structured reference for **developers** working with the `forgen.agent` package. Let me know if you need any modifications! 🚀
