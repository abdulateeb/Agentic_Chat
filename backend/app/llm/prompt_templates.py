"""
Prompt templates for interacting with the Gemini LLM.
Provides structured, reusable prompts for the core agent tasks: planning and synthesis.
"""

# This is the master prompt for the planning phase. It instructs the LLM to act as an SRE
# and to respond with a structured JSON object representing the execution plan.
# This level of detail is crucial for getting reliable, parsable output from the LLM.
PLANNER_PROMPT_TEMPLATE = """
You are a helpful and intelligent assistant. Your goal is to answer the user's query.

Analyze the user's query. You have two options:

1.  **Direct Answer:** If the query is a general question, a greeting, or something that does not require accessing external tools (like metrics, logs, or incidents), then you should answer it directly. To do this, respond ONLY with a valid JSON object with a single key: "direct_answer".
    Example for a direct answer:
    {
      "direct_answer": "I am a large language model trained by Google. How can I help you with your SRE tasks today?"
    }

2.  **Execution Plan:** If the query requires you to fetch data or perform an action using tools, then you must create a step-by-step execution plan. To do this, respond ONLY with a valid JSON object representing a directed acyclic graph (DAG) with two keys: "nodes" and "edges".

    **Node Schema for a Plan:**
    - "id": A unique string identifier (e.g., "n_1").
    - "label": A short, human-readable title (e.g., "Fetch P99 Latency").
    - "type": Must be 'tool'.
    - "data": An object containing:
      - "description": A clear description of the step.
      - "tool_name": The specific tool to use (e.g., 'metrics_tool', 'logs_tool').
      - "parameters": A dictionary of parameters for the tool.

    **Edge Schema:**
    Each edge in the "edges" list defines a dependency:
    - "from": The "id" of the source node.
    - "to": The "id" of the destination node.
    An edge from node A to node B means B cannot start until A is complete.
    If two nodes can run in parallel, do not create an edge between them.

**User Query:**
"{user_query}"

Now, generate the JSON execution plan for the user query.
"""

def get_planner_prompt(user_query: str) -> str:
    """Return formatted planner prompt."""

    return PLANNER_PROMPT_TEMPLATE.format(user_query=user_query)

# --- ADD THIS ENTIRE BLOCK TO THE END OF THE FILE ---

# Prompt for synthesizing a final answer from collected data.
SYNTHESIZER_PROMPT_TEMPLATE = """
You are an expert Site Reliability Engineer (SRE) assistant. Your task is to synthesize a final, comprehensive, and human-readable answer based on a user's query and the data collected from various tools.

Analyze the provided context, which includes the original query and a list of tool execution results.
Structure your response clearly. Start with a direct, concise answer to the user's question. Then, provide a detailed explanation supported by the evidence from the tool results.
If applicable, conclude with a list of actionable recommendations.

**Original User Query:**
{user_query}

**Collected Data (Tool Results):**
{collected_data}

**Your Final Synthesized Response:**
"""

def get_synthesizer_prompt(user_query: str, collected_data: list) -> str:
    """
    Formats the synthesizer prompt with the query and collected data.

    Args:
        user_query: The original user's question.
        collected_data: A list of dictionaries, where each dict is a tool result.

    Returns:
        A fully formatted prompt string for the synthesis LLM call.
    """
    import json
    # Pretty-print the JSON for better readability by the LLM
    data_str = json.dumps(collected_data, indent=2)
    return SYNTHESIZER_PROMPT_TEMPLATE.format(user_query=user_query, collected_data=data_str)
