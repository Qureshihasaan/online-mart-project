import asyncio
import logging
import os
import sys
from typing import Any, Dict, List, Optional
import aiohttp
from dotenv import load_dotenv
from agents import (
    Agent,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    Runner,
    function_tool,
    set_tracing_disabled,
)
from . import dynamic_instruction


load_dotenv()

# Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL", "http://order_services:8003")
# INVENTORY_SERVICE_URL = os.getenv("INVENTORY_SERVICE_URL", "http://inventory_services:8000")
# KB_SERVICE_URL = os.getenv("KB_SERVICE_URL", "")
# VISUALIZER_URL = os.getenv("VISUALIZER_URL", "")
# SUPPORT_SERVICE_URL = os.getenv("SUPPORT_SERVICE_URL", "")
# DYNAMIC_INSTRUCTIONS = os.getenv("DYNAMIC_INSTRUCTIONS", "")

BASE_URL = os.getenv(
    "GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/"
)

set_tracing_disabled(disabled=True)

# Logging setup
logging.basicConfig(level=os.getenv("AI_CHATBOT_LOG_LEVEL", "INFO"))
logger = logging.getLogger("ai_chatbot")

# HTTP config
DEFAULT_TIMEOUT = aiohttp.ClientTimeout(total=10)
RETRY_ATTEMPTS = 2
RETRY_BACKOFF = 1.0  # seconds

@function_tool
async def get_order_status(order_id: str) -> Dict[str, Any]:
    """
    Fetch single order from Order Service.
    Mapped to: GET {ORDER_SERVICE_URL}/get_single_order?order_id={order_id}
    Returns standardized dict: {"success": bool, "order": {...}} or error dict.
    """
    if not order_id:
        return {"success": False, "error": "order_id_required"}

    url = f"{ORDER_SERVICE_URL.rstrip('/')}/get_single_order"
    logger.info("get_order_status -> %s (order_id=%s)", url, order_id)
    resp = await _http_get_json(url, params={"order_id": order_id})
    if isinstance(resp, dict) and resp.get("success") is False:
        return resp
    # If Order service returns the order object directly, unify shape
    return {"success": True, "order": resp}


@function_tool
async def search_knowledge_base(query: str, scope: str = "policies") -> Dict[str, Any]:
    """
    Knowledge base is not implemented in the repository.
    Return a not-implemented response so the agent handles it gracefully.
    """
    logger.info("search_knowledge_base called locally but KB is not implemented")
    return {
        "success": False,
        "error": "kb_unavailable",
        "message": "Knowledge base service is not available. Please ask clarifying questions or request escalation to support.",
    }


@function_tool
async def visualize_design(description: str, design_file_url: Optional[str] = None) -> Dict[str, Any]:
    """
    Visualizer is not implemented in this repo.
    Return an informative response instructing the agent to ask user for upload/confirmation.
    """
    logger.info("visualize_design called but visualizer not present")
    return {
        "success": False,
        "error": "visualizer_unavailable",
        "message": "Visualizer service is not available. Request the user to upload their design and confirm product/size, or offer to create a support summary for manual handling.",
    }


@function_tool
async def create_support_ticket(issue_description: str, priority: str = "normal") -> Dict[str, Any]:
    """
    Ticket creation endpoint not present in the notification service in this repo.
    Return an actionable suggestion the agent can present to the user.
    """
    logger.info("create_support_ticket called but support API not present")
    return {
        "success": False,
        "error": "support_unavailable",
        "message": "Automatic ticket creation is not available. I can prepare a support summary for you to send, or escalate to a human agent.",
    }


# ---------------------------
# Agent run logic
# ---------------------------


async def run_agent_for_prompt(prompt: str) -> Any:
    """
    Compose OpenAI/Gemini client, model and agent, then run the agent with provided prompt.
    Returns the raw result object from Runner.run (may expose .final_output).
    """
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not configured")

    external_client: AsyncOpenAI = AsyncOpenAI(
        api_key=GEMINI_API_KEY, base_url=BASE_URL
    )
    model = OpenAIChatCompletionsModel(
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        openai_client=external_client,
    )
 
    agent = Agent(name="Takhleeq Support Agent", model=model, instructions="dynamic_instruction")

    logger.info("Running agent for prompt (len=%d)", len(prompt or ""))
    result = await Runner.run(agent, input=prompt)
    logger.info("Agent run completed")
    return result


async def main(prompt: Optional[str] = None) -> int:
    """
    CLI-friendly entrypoint. Returns exit code 0 on success, non-zero on misconfiguration/errors.
    - If prompt is None and running interactively, prompts the user via input().
    - In non-interactive contexts you should call main(prompt='...') programmatically.
    """
    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY not set. Please set it in environment or .env")
        return 1

    if prompt is None:
        if sys.stdin.isatty():
            try:
                prompt = input("How can I help you? ")
            except (EOFError, KeyboardInterrupt):
                logger.info("No interactive input provided.")
                return 1
        else:
            logger.error(
                "No prompt provided and not running interactively. Use main(prompt=...) for non-interactive runs."
            )
            return 1

    try:
        result = await run_agent_for_prompt(prompt)
        # Try to display final_output if available
        try:
            print(getattr(result, "final_output", result))
        except Exception:
            print(result)
    except Exception as exc:
        logger.exception("Agent execution failed: %s", exc)
        return 1

    return 0


if __name__ == "__main__":
    # Allow passing a prompt via CLI args as convenience
    cli_prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
    exit_code = asyncio.run(main(prompt=cli_prompt))
    sys.exit(exit_code)
