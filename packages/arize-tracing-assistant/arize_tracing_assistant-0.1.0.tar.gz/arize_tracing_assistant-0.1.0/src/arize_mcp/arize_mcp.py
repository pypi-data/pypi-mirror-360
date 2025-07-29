from mcp.server.fastmcp import FastMCP  # type: ignore
from pathlib import Path
import requests
import json

mcp = FastMCP("Arize-MCP-Tracing-Assistant")

RUNLLM_MCP_URL = "https://mcp.runllm.com/mcp/"  # Change to your MCP endpoint if needed
RUNLLM_HEADERS = {
    "assistant-name": "arize-ax",  # Adjust if your assistant name is different
    "Content-Type": "application/json",  # MCP servers use JSON-RPC 2.0 payloads
    "Accept": "application/json, text/event-stream",  # Request SSE streaming
}


LANG_MAP = {
    "python": "python",
    "py": "python",
    "javascript": "typescript",
    "js": "typescript",
    "typescript": "typescript",
    "ts": "typescript",
}


FRAMEWORK_MAP = {
    "agno": "agno",
    "amazon-bedrock": "amazon-bedrock",
    "aws-bedrock": "amazon-bedrock",
    "aws-bedrock-agents": "amazon-bedrock",
    "bedrock": "amazon-bedrock",
    "anthropic": "anthropic",
    "autogen": "autogen",
    "beeai": "beeai",
    "crewai": "crewai",
    "dspy": "dspy",
    "google-gen-ai": "google-gen-ai",
    "google-genai": "google-gen-ai",
    "groq": "groq",
    "guardrails-ai": "guardrails-ai",
    "guardrails": "guardrails-ai",
    "haystack": "haystack",
    "hugging-face-smolagents": "hugging-face-smolagents",
    "smolagents": "hugging-face-smolagents",
    "instructor": "instructor",
    "langchain": "langchain",
    "langflow": "langflow",
    "langgraph": "langgraph",
    "litellm": "litellm",
    "llamaindex": "llamaindex",
    "llama-index": "llamaindex",
    "llamaindex-workflows": "llamaindex",
    "llama-index-workflows": "llamaindex",
    "mistralai": "mistralai",
    "model-context-protocol": "model-context-protocol",
    "openai": "openai",
    "open-ai": "openai",
    "openai-agents": "openai-agents",
    "prompt-flow": "prompt-flow",
    "together": "together",
    "together-ai": "together",
    "togetherai": "together",
    "vercel": "vercel",
    "vertexai": "vertexai",
    "vertex-ai": "vertexai",
    "vertex": "vertexai",
}

PROMPT_ARIZE = """
You are about to receive code snippets that demonstrate how to export OpenTelemetry/OpenInference traces either AUTOMATICALLY (framework-specific) or MANUALLY (framework-agnostic).

• Arize ⟶ commercial SaaS built on OpenTelemetry / OpenInference  
• Phoenix ⟶ open-source sibling; identical ingestion format  
• Auto-instrumentation = framework-specific, minimal code  
• Manual instrumentation = framework-agnostic, maximum control

```txt
=== AUTO INSTRUMENTATION EXAMPLE ({framework}) ===
{auto_inst_example}

=== MANUAL INSTRUMENTATION EXAMPLE 1: SEND TRACES ===
{send_traces_example}

=== MANUAL INSTRUMENTATION EXAMPLE 2: SEND TRACES FROM AN STREAMLIT APP ===
{manual_inst_example}
```
"""

PROMPT_PHOENIX = """
You are about to receive code snippets that demonstrate how to export OpenTelemetry/OpenInference traces either AUTOMATICALLY (framework-specific) or MANUALLY (framework-agnostic).

• Arize = commercial AI observability platform built on OpenTelemetry / OpenInference  
• Phoenix =open-source sibling; almost identical ingestion format  
• Auto instrumentation = framework-specific open inference instrumentors, minimal code  
• Manual instrumentation = framework-agnostic, maximum control, more code

```txt
=== PHOENIX SETUP ===
{phoenix_setup}

=== AUTO INSTRUMENTATION EXAMPLE ({framework}) ===
{auto_inst_example}

=== MANUAL INSTRUMENTATION EXAMPLE 1: SEND TRACES ===
{send_traces_example}

=== MANUAL INSTRUMENTATION EXAMPLE 2: SEND TRACES FROM AN STREAMLIT APP ===
{manual_inst_example}
```
"""


ROOT = Path(__file__).resolve().parents[0]
REFS_DIR = ROOT / "refs"
AUTO_INST_EXAMPLES_DIR = REFS_DIR / "auto_inst_examples"
ADVANCED_DOCS_DIR = REFS_DIR / "advanced_tracing_docs"
MANUAL_INST_EXAMPLES_DIR = REFS_DIR / "manual_inst_examples"


def normalize_lang(lang: str) -> str:
    return LANG_MAP.get(lang.lower(), "python")  # Default to Python if not found


def normalize_framework(framework: str) -> str:
    return FRAMEWORK_MAP.get(
        framework.replace("_", "-").lower(), "openai"
    )  # Default to OpenAI if not found


def get_manual_tracing_examples(product: str) -> str:
    """
    Get manual instrumentation examples for Arize or Phoenix. Defaults to Arize.
    """

    if product not in ["arize", "phoenix"]:
        product = "arize"

    file_name = f"app_manually_instrumented_{product}.md"
    path = MANUAL_INST_EXAMPLES_DIR / file_name

    if not path.exists():
        path = MANUAL_INST_EXAMPLES_DIR / "app_manually_instrumented_arize.md"

    if not path.exists():
        return (
            "Manual instrumentation examples could not be located. Please ensure the 'manual_inst_examples' "
            "directory is present and contains the required markdown files."
        )

    return path.read_text(encoding="utf-8")


def get_send_traces_examples(product: str) -> str:
    """
    Get send traces examples for Arize or Phoenix. Defaults to Arize.
    """

    if product not in ["arize", "phoenix"]:
        product = "arize"

    file_name = f"send_traces_{product}.md"
    path = MANUAL_INST_EXAMPLES_DIR / file_name

    if not path.exists():
        path = MANUAL_INST_EXAMPLES_DIR / "send_traces_arize.md"

    if not path.exists():
        return (
            "Send-traces examples could not be located. Please ensure the 'manual_inst_examples' directory "
            "contains the required markdown files."
        )

    return path.read_text(encoding="utf-8")


def get_auto_tracing_example(product: str, framework: str, language: str) -> str:
    """
    Get auto instrumentation examples for Arize or Phoenix. Defaults to Arize
    """
    lang = normalize_lang(language)
    framework = normalize_framework(framework)  # type: ignore

    path = AUTO_INST_EXAMPLES_DIR / product / framework / f"{lang}.md"

    if not path.exists():
        return (
            "Examples not found for the given framework/language combination. Defaulting to python and openai"
            "Please ensure you provide a valid pair or use manual instrumentation with open telemetry."
        )
    return path.read_text(encoding="utf-8")


@mcp.tool()
def get_arize_tracing_docs(framework: str, language: str) -> str:
    """
    Get docs and examples to instrument an app and send traces/spans to Arize.
    If the framework is not in the list use manual instrumentation with open telemetry.

    Parameters
    ----------
    framework : str
        LLM provider or framework. One of:
        ["agno", "amazon-bedrock", "anthropic", "autogen", "beeai", "crewai", "dspy", "google-gen-ai", "groq", "guardrails-ai", "haystack",
        "hugging-face-smolagents", "instructor", "langchain", "langflow", "langgraph", "litellm", "llamaindex", "mistralai", "openai", "openai-agents", "prompt-flow",
        "together", "vercel", "vertexai"]
    language : str
        Programming language: "python" or "typescript"

    Returns
    -------
    str
        Example code snippets for auto/manual instrumentation for Arize.
    """
    auto_inst_example = get_auto_tracing_example("arize", framework, language)
    manual_inst_example = get_manual_tracing_examples("arize")
    send_traces_example = get_send_traces_examples("arize")

    return PROMPT_ARIZE.format_map(
        {
            "auto_inst_example": auto_inst_example,
            "framework": framework,
            "send_traces_example": send_traces_example,
            "manual_inst_example": manual_inst_example,
        }
    )


@mcp.tool()
def get_arize_advanced_tracing_docs(language="python", content="ALL"):
    """
    Get advanced docs and examples to manually instrument an app and send traces/spans to Arize.

     Parameters
    ----------:
    language: str
        "python" or "typescript" or "javascript"
    content: str
         "ALL" or section name:
        - SETUP: Installation and configuration
        - AUTO: Auto-instrumentation
        - HYBRID: Auto-instrumentation with context helpers and enrichment
        - MANUAL: Manual instrumentation
        - SEMANTIC: Setting span kinds and attributes
        - EVENTS: Tracing events, exceptions, errors, status
        - CONTEXT: Context propagation between spans, services and processes
        - PROMPT: Tracing prompt templates and prompt versioning
        - MASK: Masking and redaction of sensitive data in spans
        - EVAL: Sending evaluations to Arize

    Returns:
    str
        Docs and code snippets for advanced instrumentation.
    """

    # Normalise language input – treat JS → TS for docs purposes
    lang = language.lower()
    if lang in {"javascript", "js"}:
        lang = "typescript"
    elif lang not in {"python", "typescript"}:
        lang = "python"

    file_path = ADVANCED_DOCS_DIR / f"tracing_summary_{lang}.md"

    if not file_path.exists():
        return (
            "Advanced tracing docs not found for the given language. Defaulting to python. "
            "Please ensure you provide a valid language or consult the README for supported options."
        )

    full_content = file_path.read_text(encoding="utf-8")

    # If caller wants the entire document, return early.
    if content.upper() == "ALL":
        return full_content

    section_marker = f"[SECTION:{content.upper()}]"

    if section_marker not in full_content:
        return f"Section {content} not found in the documentation for {lang}."

    # Find section start
    start_idx = full_content.find(section_marker)

    # Find next section or end of content
    next_section_idx = full_content.find("\n[SECTION:", start_idx + 1)
    if next_section_idx == -1:
        # No next section, return to end
        return full_content[start_idx:]
    else:
        return full_content[start_idx:next_section_idx]


def get_phoenix_tracing_example(framework: str, language: str) -> str:
    """
    Get examples to instrument an app and send traces/spans to Phoenix.
    If the framework is not in the list use manual instrumentation with open telemetry.

    Parameters
    ----------
    framework : str
        LLM provider or framework. One of:
        ["agno", "amazon-bedrock", "anthropic", "autogen", "beeai", "crewai", "dspy", "google-gen-ai", "groq", "guardrails-ai", "haystack",
        "hugging-face-smolagents", "instructor", "langchain", "langflow", "langgraph", "litellm", "llamaindex", "mistralai", "openai", "openai-agents", "prompt-flow",
        "together", "vercel", "vertexai"]
    language : str
        Programming language: "python" or "typescript". Defaults to "python".

    Returns
    -------
    str
        Example code snippets for auto/manual instrumentation for Phoenix.
    """
    auto_inst_example = get_auto_tracing_example("phoenix", framework, language)
    manual_inst_example = get_manual_tracing_examples("phoenix")
    send_traces_example = get_send_traces_examples("phoenix")

    setup_path = AUTO_INST_EXAMPLES_DIR / "phoenix" / "phoenix_setup.md"
    phoenix_setup = setup_path.read_text(encoding="utf-8")

    return PROMPT_PHOENIX.format_map(
        {
            "phoenix_setup": phoenix_setup,
            "auto_inst_example": auto_inst_example,
            "framework": framework,
            "manual_inst_example": manual_inst_example,
            "send_traces_example": send_traces_example,
        }
    )


@mcp.tool()
def arize_support(question: str) -> str:
    """

    Answer precise questions about Arize and Arize instrumentation. Send any question about Arize to the assistant. Use this tool when the info provided by get_arize_tracing_docs and get_arize_advanced_tracing_docs is not enough.
    Or when the question about Arize is not related to tracing.

    Parameters
    ----------
    message : str
        Question to send to the assistant.

    Returns
    -------
    str
        Curated and specific answers about Arize and Arize instrumentation.
    """

    # Build JSON-RPC request payload
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "chat",
            "arguments": {"message": question},
        },
    }

    # Send POST request with streaming enabled (Server-Sent Events)
    with requests.post(
        RUNLLM_MCP_URL, json=payload, headers=RUNLLM_HEADERS, stream=True, timeout=60
    ) as resp:
        resp.raise_for_status()

        response_chunks = []
        for line in resp.iter_lines(decode_unicode=True):
            # SSE lines start with "data:"
            if not line or not line.startswith("data:"):
                continue

            # Parse the JSON-RPC payload contained after the „data:“ prefix
            try:
                msg = json.loads(line[len("data:") :].strip())
            except json.JSONDecodeError:
                continue

            # We only care about the *final* result for our request id.
            if msg.get("id") == 1 and "result" in msg:
                for part in msg["result"].get("content", []):
                    if part.get("type") == "text":
                        response_chunks.append(part.get("text", ""))
                break  # Exit the SSE loop once we have the result

    return "\n".join(response_chunks)


if __name__ == "__main__":
    mcp.run(transport="stdio")
