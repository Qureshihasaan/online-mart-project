"""Quick timing test: image generation vs agent separately."""
import asyncio
import time
import sys
sys.path.insert(0, ".")

import config


async def test():
    print(f"IMAGE_MODEL: {config.IMAGE_MODEL}")
    print(f"OPENROUTER_MODEL: {config.OPENROUTER_MODEL}")
    print()

    # Test 1: Direct image generation (no agent)
    print("TEST 1: Direct image generation via OpenRouter...")
    t1 = time.time()
    
    from ai_agents.design_agent import generate_image_via_openrouter
    result = await generate_image_via_openrouter("A red circle on white background")
    
    elapsed1 = time.time() - t1
    if result:
        print(f"  OK - Image generated in {elapsed1:.1f}s (length: {len(result)})")
    else:
        print(f"  FAIL after {elapsed1:.1f}s")
    print()

    # Test 2: Agent run (Qwen + tool call)
    print("TEST 2: Full agent run (Qwen + tool call)...")
    t2 = time.time()

    from ai_agents.design_agent import generate_design, get_image
    import re
    result2 = await generate_design("simple red flower")

    elapsed2 = time.time() - t2
    
    # Check if image was stored
    ref_pattern = re.compile(r"IMAGE_GENERATED:([a-f0-9]{8})")
    found_image = False
    for item in result2.new_items:
        if hasattr(item, "output") and isinstance(item.output, str):
            m = ref_pattern.search(item.output)
            if m:
                img = get_image(m.group(1))
                if img:
                    found_image = True
                    break
    
    if found_image:
        print(f"  OK - Agent completed in {elapsed2:.1f}s")
    else:
        print(f"  FAIL - Agent completed in {elapsed2:.1f}s but no image found")
    
    desc = str(result2.final_output)[:100]
    print(f"  Description: {desc}")


asyncio.run(test())
