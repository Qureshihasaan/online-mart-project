import asyncio
import os
from dotenv import load_dotenv
from pinecone import Pinecone
from agents import (
    Agent,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    run_demo_loop,
    set_tracing_disabled,
    function_tool,
    Runner
)

load_dotenv()

# gemini_api_key = os.getenv("GEMINI_API_KEY")

openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
pinecone_api_key = os.getenv("PINECONE_API_KEY")

# if gemini_api_key:
#     print("Gemini API Key loaded.")
if openrouter_api_key:
    print("Openrouter API Key loaded.")
if pinecone_api_key:
    print("Pinecone API Key loaded.")

# Pinecone index for RAG
INDEX_NAME = "ai-vector-embeddings"
NAMESPACE = "example_namespace"

pc = Pinecone(api_key=pinecone_api_key)
# dense_index = pc.Index(INDEX_NAME) if pc.has_index(INDEX_NAME) else None
# if not pc.has_index(INDEX_NAME):
#     pc.create_index_for_model(
#         name=INDEX_NAME,
#         cloud= "aws",
#         region="us-east-1",
#         embed= {
#             "model" : "llama-text-embed-v2",
#             "field_map": {"text":"chunk_text"}
#          }
#     )

dense_index = pc.Index(INDEX_NAME)

@function_tool
def search_knowledge_base(query: str) -> str:
    """Search the Takhleeq knowledge base for relevant information.
    Call this when you need to answer questions about Takhleeq, policies, or documented facts.
    Args:
        query: The search question or topic to look up (e.g. "What is Takhleeq?", "refund policy").
    """
    if dense_index is None:
        return "Knowledge base is not available (index not found)."
    try:
        result = dense_index.search(
            namespace=NAMESPACE,
            query={
                "top_k": 100,
                "inputs": {"text": query},
            },
            rerank={
                "model": "bge-reranker-v2-m3",
                "top_n": 100,
                "rank_fields": ["chunk_text"],
            },
        )
        hits = result.get("result", {}).get("hits", [])
        if not hits:
            return "No relevant passages found in the knowledge base."
        parts = []
        for i, hit in enumerate(hits, 1):
            text = hit.get("fields", {}).get("chunk_text", "")
            if text:
                parts.append(f"[{i}] {text.strip()}")
        return "\n\n".join(parts) if parts else "No relevant passages found."
    except Exception as e:
        return f"Search failed: {e}"


external_client = AsyncOpenAI(
    api_key=openrouter_api_key,
    # base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    base_url="https://openrouter.ai/api/v1"
)

model = OpenAIChatCompletionsModel(
    # model="gemini-2.0-flash",
    model="google/gemini-2.0-flash-001",
    openai_client=external_client,
)

set_tracing_disabled(disabled=True)


RAG_INSTRUCTIONS = """
You are the Takhleeq AI Assistant, a helpful and friendly assistant for Takhleeq.
Use the `search_knowledge_base` tool to look up information from the knowledge base when needed.

If the user asks about:
- What Takhleeq is
- What Takhleeq does
- Takhleeq’s services, products, or offerings
- Policies, guidelines, or procedures
- Any factual information documented in the knowledge base

...then you MUST use the `search_knowledge_base` tool first to find relevant passages and base your answer on those.

If the user asks:
- A question that is not about Takhleeq or its knowledge base
- Something outside the scope of the knowledge base
- A casual, conversational, or unrelated question

...then you may answer directly without using the tool.

Always be friendly, clear, and concise. If you can’t find relevant information in the knowledge base, say so honestly.
"""


agent = Agent(
    name="Takhleeq AI Assistant",
    instructions=RAG_INSTRUCTIONS,
    model=model,
    tools=[search_knowledge_base],
)
result = Runner.run_sync(agent, input=input("Enter your question: "))



if __name__ == "__main__":
    print("Takhleeq AI Assistant — type 'quit' or 'exit' to end.\n")
    asyncio.run(run_demo_loop(result.final_output))
