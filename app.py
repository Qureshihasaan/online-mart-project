import os
import chainlit as cl
from dotenv import load_dotenv
from pinecone import Pinecone
from agents import (
    Agent,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    set_tracing_disabled,
    function_tool,
    Runner,
)

load_dotenv()

openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
pinecone_api_key = os.getenv("PINECONE_API_KEY")

# ── Pinecone setup ──────────────────────────────────────────
INDEX_NAME = "ai-vector-embeddings"
NAMESPACE = "example_namespace"

pc = Pinecone(api_key=pinecone_api_key)
dense_index = pc.Index(INDEX_NAME)


@function_tool
def search_knowledge_base(query: str) -> str:
    """Search the Takhleeq knowledge base for relevant information.
    Call this when you need to answer questions about Takhleeq, policies, or documented facts.
    Args:
        query: The search question or topic to look up.
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


# ── LLM setup (OpenRouter → Gemini) ────────────────────────
external_client = AsyncOpenAI(
    api_key=openrouter_api_key,
    base_url="https://openrouter.ai/api/v1",
)

model = OpenAIChatCompletionsModel(
    model="google/gemini-2.0-flash-001",
    openai_client=external_client,
)

set_tracing_disabled(disabled=True)

# ── Agent setup ─────────────────────────────────────────────
RAG_INSTRUCTIONS = """
You are the Takhleeq AI Assistant, a helpful and friendly assistant for Takhleeq.
Use the `search_knowledge_base` tool to look up information from the knowledge base when needed.

If the user asks about:
- What Takhleeq is
- What Takhleeq does
- Takhleeq's services, products, or offerings
- Policies, guidelines, or procedures
- Any factual information documented in the knowledge base

...then you MUST use the `search_knowledge_base` tool first to find relevant passages and base your answer on those.

If the user asks:
- A question that is not about Takhleeq or its knowledge base
- Something outside the scope of the knowledge base
- A casual, conversational, or unrelated question

...then you may answer directly without using the tool.

Always be friendly, clear, and concise. If you can't find relevant information in the knowledge base, say so honestly.
"""

agent = Agent(
    name="Takhleeq AI Assistant",
    instructions=RAG_INSTRUCTIONS,
    model=model,
    tools=[search_knowledge_base],
)


# ── Chainlit handlers ──────────────────────────────────────
@cl.on_chat_start
async def on_chat_start():
    """Send a welcome message and initialise session history."""
    cl.user_session.set("history", [])
    await cl.Message(
        content="👋 Welcome! I'm the **Takhleeq AI Assistant**. How can I help you today?"
    ).send()


@cl.on_message
async def on_message(message: cl.Message):
    """Run the agent on each user message and stream the reply."""
    history = cl.user_session.get("history", [])

    # Add the new user message to history
    history.append({"role": "user", "content": message.content})

    # Run the agent
    result = await Runner.run(agent, input=history)

    assistant_reply = result.final_output

    # Save the assistant reply to history
    history.append({"role": "assistant", "content": assistant_reply})
    cl.user_session.set("history", history)

    # Send the reply back to the UI
    await cl.Message(content=assistant_reply).send()
