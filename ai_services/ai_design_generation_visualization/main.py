"""
AI Product Visualization — FastAPI Application
===============================================
Exposes REST endpoints for generating designs and visualizing
them on products using the OpenAI Agents SDK pipeline.
"""
from __future__ import annotations
import uvicorn
import base64
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

import config
from model import (
    DesignRequest,
    DesignResponse,
    GenerateDesignRequest,
    GenerateDesignResponse,
    ApplyDesignRequest,
    ApplyDesignResponse,
)
from ai_agents.coordinator import run_full_pipeline, run_design_only, run_apply_design


# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="AI Product Visualization",
    description=(
        "Generate designs from text prompts and visualize them on products "
        "with AI-powered color enhancement."
    ),
    version="0.1.0",
)

# CORS — allow all origins during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve saved output images
app.mount("/output", StaticFiles(directory=str(config.OUTPUT_DIR)), name="output")


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _save_image(b64_data: str, label: str) -> str:
    """Persist a base64 image to the output directory. Returns the filename."""
    filename = f"{label}_{uuid.uuid4().hex[:8]}.png"
    filepath = config.OUTPUT_DIR / filename
    filepath.write_bytes(base64.b64decode(b64_data))
    return filename


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/health")
async def health_check():
    """Health-check endpoint."""
    return {"status": "ok", "service": "ai-product-visualization"}


@app.post("/visualize", response_model=DesignResponse)
async def visualize(request: DesignRequest):
    """Full pipeline: generate design → apply to product → enhance colors."""
    try:
        result = await run_full_pipeline(
            prompt=request.prompt,
            product_image_b64=request.product_image,
            product_type=request.product_type,
            product_color=request.product_color,
            reference_image_b64=request.reference_image,
        )

        # Persist images
        _save_image(result["design_image"], "design")
        _save_image(result["visualization_image"], "visualization")
        _save_image(result["enhanced_image"], "enhanced")

        return DesignResponse(
            design_image=result["design_image"],
            visualization_image=result["visualization_image"],
            enhanced_image=result["enhanced_image"],
            description=result["description"],
        )

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/generate-design", response_model=GenerateDesignResponse)
async def generate_design_endpoint(request: GenerateDesignRequest):
    """Generate a design from a text prompt (no product application)."""
    try:
        result = await run_design_only(
            prompt=request.prompt,
            reference_image_b64=request.reference_image,
        )

        filename = _save_image(result["design_image"], "design")
        image_url = f"/output/{filename}"

        return GenerateDesignResponse(
            design_image=result["design_image"],
            description=result["description"],
            image_url=image_url,
        )

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/apply-design", response_model=ApplyDesignResponse)
async def apply_design_endpoint(request: ApplyDesignRequest):
    """Apply a user-uploaded design onto a product image (skip AI generation)."""
    try:
        result = await run_apply_design(
            design_image_b64=request.design_image,
            product_image_b64=request.product_image,
            product_type=request.product_type,
            product_color=request.product_color,
            prompt=request.prompt,
        )

        _save_image(result["visualization_image"], "visualization")
        filename = _save_image(result["enhanced_image"], "enhanced")
        image_url = f"/output/{filename}"

        return ApplyDesignResponse(
            visualization_image=result["visualization_image"],
            enhanced_image=result["enhanced_image"],
            description=result["description"],
            image_url=image_url,
        )

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/preview/{filename}", response_class=HTMLResponse)
async def preview_image(filename: str):
    """View a generated image in the browser."""
    filepath = config.OUTPUT_DIR / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    return f"""
    <html>
    <head><title>Design Preview</title></head>
    <body style="margin:0; display:flex; justify-content:center;
                 align-items:center; min-height:100vh; background:#111">
        <img src="/output/{filename}" style="max-width:90vw; max-height:90vh" />
    </body>
    </html>
    """


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
