"""
Design Generation Agent
-----------------------
Uses OpenAI Agents SDK with OpenRouter for reasoning and
image generation via the chat completions API (Flux model).

Image data is stored in a module-level dict to avoid passing
large base64 strings through the LLM context window.
"""

from __future__ import annotations

import re
import uuid
import asyncio
import base64
import os
import sys
import re as _re
from openai import AsyncOpenAI
from agents import Agent, Runner, function_tool, set_tracing_disabled
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel

import config

# Disable tracing (no direct OpenAI key for trace uploading)
set_tracing_disabled(True)

# ---------------------------------------------------------------------------
# Shared OpenRouter client & model (imported by other agents)
# ---------------------------------------------------------------------------

openrouter_client = AsyncOpenAI(
    base_url=config.OPENROUTER_BASE_URL,
    api_key=config.OPENROUTER_API_KEY,
)



external_client = AsyncOpenAI(
    base_url=config.OPENROUTER_BASE_URL,
    api_key=config.OPENROUTER_API_KEY,
)

model = OpenAIChatCompletionsModel(
    model=config.OPENROUTER_MODEL,
    openai_client=external_client,
)


# ---------------------------------------------------------------------------
# Image store — avoids sending base64 through the LLM context
# ---------------------------------------------------------------------------

_image_store: dict[str, str] = {}


def store_image(b64_data: str) -> str:
    """Store base64 image data and return a short reference ID."""
    ref_id = str(uuid.uuid4())[:8]
    _image_store[ref_id] = b64_data
    return ref_id


def get_image(ref_id: str) -> str | None:
    """Retrieve stored image data by reference ID."""
    return _image_store.pop(ref_id, None)

def peek_image(ref_id: str) -> str | None:
    """Check stored image data by reference ID without removing it."""
    return _image_store.get(ref_id)


# ---------------------------------------------------------------------------
# Helper — generate image via OpenRouter chat completions
# ---------------------------------------------------------------------------

async def generate_image_via_openrouter(prompt: str, image_b64: str | None = None) -> str | None:
    """Call an OpenRouter image model via chat completions and return base64.

    OpenRouter image models are accessed through the normal chat completions
    endpoint.  The response contains the image in the ``message.images`` field
    as a data-URL (data:image/png;base64,...), NOT in ``message.content``.

    Returns:
        Base64-encoded image string (without the data-URL prefix), or None.
    """
    if image_b64:
        # Use image-to-image model
        model = config.FLUX_IMAGE_MODEL
        def _format_image_url(b64_data: str) -> str:
            if b64_data.startswith("data:"):
                return b64_data
            return f"data:image/jpeg;base64,{b64_data}"
        messages = [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": _format_image_url(image_b64)}}
            ]
        }]
        print(f"DEBUG: Using model {model} for image generation")
        try:
            response = await external_client.chat.completions.create(
                model=model,
                messages=messages,
            )
            msg = response.choices[0].message
            content = msg.content
            if content:
                match = re.search(r"data:image/[^;]+;base64,([A-Za-z0-9+/=]+)", content)
                if match:
                    return match.group(1)
                stripped = content.strip()
                if len(stripped) > 200 and re.match(r"^[A-Za-z0-9+/=\s]+$", stripped):
                    return stripped.replace("\n", "").replace(" ", "")
            return None
        except Exception as e:
            import traceback
            traceback.print_exc()
            return None
    else:
        # Use text-to-image model (Flux)
        model = config.FLUX_IMAGE_MODEL
        import aiohttp
        headers = {
            "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
        }
        
        print(f"DEBUG: Using native OpenRouter payload for {model}")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(config.OPENROUTER_BASE_URL + "/chat/completions", headers=headers, json=payload) as resp:
                    resp_json = await resp.json()
                    if "choices" in resp_json and len(resp_json["choices"]) > 0:
                        msg = resp_json["choices"][0].get("message", {})
                        images = msg.get("images")
                        if images and len(images) > 0:
                            url = images[0].get("image_url", {}).get("url", "")
                            if url:
                                match = re.search(r"base64,(.+)", url)
                                if match:
                                    return match.group(1)
                        content = msg.get("content", "")
                        if content:
                            match = re.search(r"data:image/[^;]+;base64,([A-Za-z0-9+/=]+)", content)
                            if match:
                                return match.group(1)
                            stripped = content.strip()
                            if len(stripped) > 200 and re.match(r"^[A-Za-z0-9+/=\s]+$", stripped):
                                return stripped.replace("\n", "").replace(" ", "")
                    print(f"DEBUG Error - OpenRouter returned {resp_json}")
                    return None
        except Exception as e:
            import traceback
            traceback.print_exc()
            return None


# ---------------------------------------------------------------------------
# Custom tool — generate design image
# ---------------------------------------------------------------------------

@function_tool
async def generate_design_image(prompt: str, reference_image_id: str | None = None) -> str:
    """Generate a design image based on a text prompt.

    Uses an image-generation model to create a high-quality design.

    Args:
        prompt: Detailed description of the design to generate, including
                style, colors, patterns, and any specific elements.
        reference_image_id: Optional reference ID for guiding the design if provided by the user.

    Returns:
        A short reference ID for the generated image.
    """
    full_prompt = (
        f"CRITICAL INSTRUCTION: You must strictly follow the user's design description. "
        f"Do NOT hallucinate or add structural elements, subjects, or themes that are not explicitly requested. "
        f"Create a high-quality, production-ready design suitable for printing "
        f"on physical products. The design should be clean, isolated on a white "
        f"or transparent background, detailed, and vibrant. "
        f"Design description: {prompt}"
    )

    image_b64 = None
    if reference_image_id:
        ref_id = reference_image_id.split(':')[-1]
        image_b64 = peek_image(ref_id)

    result = await generate_image_via_openrouter(full_prompt, image_b64=image_b64)
    if not result:
        return "ERROR: Image generation failed — no image data was returned."

    ref_id = store_image(result)
    return f"IMAGE_GENERATED:{ref_id}"


# ---------------------------------------------------------------------------
# Agent definition
# ---------------------------------------------------------------------------

# Read instructions from the markdown file
_instruction_file = os.path.join(os.path.dirname(__file__), "dynamic_instruction.md")
with open(_instruction_file, "r", encoding="utf-8") as f:
    dynamic_instruction = f.read()

design_agent = Agent(
    name="Design Generator",
    instructions=dynamic_instruction,
    tools=[generate_design_image],
    model=model,
)

print("Loaded Instructions Length:", len(dynamic_instruction))

# ---------------------------------------------------------------------------
# Public helper
# ---------------------------------------------------------------------------

async def generate_design(prompt: str, reference_image: str | None = None):
    """Run the design agent and return the RunResult.

    Args:
        prompt: Text description of the desired design.
        reference_image: Optional base64-encoded reference image.

    Returns:
        The RunResult from the agent.
    """
    user_message = f"Generate a design based on this description: {prompt}"

    if reference_image:
        ref_id = store_image(reference_image)
        user_message += (
            f"\n\nI am also providing a reference image for style guidance. "
            f"Its reference ID is IMAGE_REFERENCE:{ref_id}. "
            f"Ensure you pass this reference ID to the generate_design_image tool."
        )

    result = await Runner.run(design_agent, input=user_message)
    return result


if __name__ == "__main__":
    

    # Allow passing a prompt as a CLI argument
    prompt = " ".join(sys.argv[1:]) or "minimalist geometric pattern with blue and gold"

    async def _main():
        print(f"Generating design: {prompt!r} ...")
        result = await generate_design(prompt=prompt)

        # Find IMAGE_GENERATED reference in the result
        ref_pattern = _re.compile(r"IMAGE_GENERATED:([a-f0-9]{8})")
        b64_data = None

        for item in result.new_items:
            if hasattr(item, "output") and isinstance(item.output, str):
                m = ref_pattern.search(item.output)
                if m:
                    b64_data = get_image(m.group(1))
                    break

        if not b64_data:
            print("ERROR: No image was generated.")
            return

        # Save the image
        os.makedirs("output", exist_ok=True)
        out_path = os.path.abspath("output/design_preview.png")
        with open(out_path, "wb") as f:
            f.write(base64.b64decode(b64_data))

        print(f"Design saved to: {out_path}")
        print(f"Description: {result.final_output}")

        # Open the image (Windows)
        os.startfile(out_path)

    asyncio.run(_main())