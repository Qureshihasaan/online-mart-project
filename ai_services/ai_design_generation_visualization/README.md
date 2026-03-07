# 🎨 AI Design Generation & Visualization

> AI-powered microservice that generates designs from text prompts and visualizes them on real products — built with FastAPI, OpenAI Agents SDK, and OpenRouter.

Part of the **Online Mart** platform's AI services layer.

---

## ✨ Features

- **Text-to-Design Generation** — Describe a design in natural language and get a print-ready image
- **Product Visualization** — Automatically apply generated designs onto product images (t-shirts, mugs, phone cases, etc.)
- **Color Enhancement** — AI-powered post-processing that harmonizes design colors with the product
- **Reference Image Support** — Optionally provide a style-reference image to guide the generation
- **Full Pipeline & Modular Endpoints** — Run the complete pipeline, or use individual steps independently

---

## 🏗️ Architecture

The service is built around a **3-stage AI agent pipeline** orchestrated by a coordinator:

```
┌─────────────────────────────────────────────────────────────────┐
│                        Coordinator                              │
│                    (coordinator.py)                              │
│                                                                 │
│   ┌──────────────┐   ┌───────────────────┐   ┌──────────────┐  │
│   │ Design Agent  │──▶│ Visualization     │──▶│ Enhancement  │  │
│   │ (Flux Model)  │   │ Agent (Gemini)    │   │ (Flux Model) │  │
│   └──────────────┘   └───────────────────┘   └──────────────┘  │
│     Text → Design      Design + Product       Color & Lighting  │
│                         → Mockup               Enhancement      │
└─────────────────────────────────────────────────────────────────┘
```

| Agent | Role | Model |
|-------|------|-------|
| **Design Generator** | Creates print-ready designs from text prompts using the OpenAI Agents SDK with function tools | Flux (via OpenRouter) |
| **Product Visualizer** | Composites the design onto a product image with proper perspective and contours | Gemini Image Model |
| **Color Enhancer** | Enhances color harmony, contrast, and lighting for a commercial-quality result | Flux (via OpenRouter) |

---

## 📂 Project Structure

```
ai_design_generation_visualization/
├── main.py                  # FastAPI app — REST endpoints
├── model.py                 # Pydantic request/response schemas
├── config.py                # Environment variables & defaults
├── Dockerfile               # Container build
├── pyproject.toml           # Dependencies & project metadata
├── .env                     # API keys & model config (not committed)
├── ai_agents/
│   ├── __init__.py
│   ├── coordinator.py       # Orchestrates the 3-stage pipeline
│   ├── design_agent.py      # Design generation agent + image store
│   ├── visualization_agent.py  # Product mockup agent
│   ├── enhancement_agent.py    # Color enhancement agent
│   └── dynamic_instruction.md  # Agent system prompt (loaded at runtime)
└── output/                  # Generated images are saved here
```

---

## 🚀 API Endpoints

### `GET /health`

Health-check endpoint.

```json
{ "status": "ok", "service": "ai-product-visualization" }
```

---

### `POST /visualize`

**Full pipeline** — generate design → apply to product → enhance colors.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `prompt` | `string` | ✅ | Design description (e.g. `"floral pattern with gold accents"`) |
| `product_image` | `string` | ✅ | Base64-encoded product image |
| `product_type` | `string` | ✅ | Product type (e.g. `"t-shirt"`, `"mug"`, `"phone-case"`) |
| `product_color` | `string` | ✅ | Dominant product color (e.g. `"white"`, `"navy blue"`) |
| `reference_image` | `string` | ❌ | Optional base64 reference image for style guidance |

**Response:**

```json
{
  "design_image": "<base64>",
  "visualization_image": "<base64>",
  "enhanced_image": "<base64>",
  "description": "Generated a floral pattern design and applied it to a white t-shirt..."
}
```

---

### `POST /generate-design`

Generate a standalone design (no product application).

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `prompt` | `string` | ✅ | Design description |
| `reference_image` | `string` | ❌ | Optional base64 reference image |

**Response:**

```json
{
  "design_image": "<base64>",
  "description": "AI-generated description of the design",
  "image_url": "/output/design_abc123.png"
}
```

---

### `POST /apply-design`

Apply a **user-uploaded** design onto a product image (skips AI generation).

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `design_image` | `string` | ✅ | Base64-encoded design to apply |
| `product_image` | `string` | ✅ | Base64-encoded product image |
| `product_type` | `string` | ✅ | Product type |
| `product_color` | `string` | ✅ | Dominant product color |
| `prompt` | `string` | ❌ | Optional application instructions |

**Response:**

```json
{
  "visualization_image": "<base64>",
  "enhanced_image": "<base64>",
  "description": "Applied the uploaded design to a white t-shirt...",
  "image_url": "/output/enhanced_abc123.png"
}
```

---

### `GET /preview/{filename}`

Renders a saved output image in the browser with a minimal HTML viewer.

---

## ⚙️ Configuration

Create a `.env` file in the project root:

```env
# OpenRouter (required)
OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=qwen/qwen-2.5-72b-instruct

# Image generation model
FLUX_IMAGE_MODEL=black-forest-labs/flux-schnell
```

All configuration is loaded in `config.py` via `python-dotenv`.

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| **FastAPI** | REST API framework |
| **Uvicorn** | ASGI server |
| **OpenAI Agents SDK** | Agent orchestration with function tools |
| **OpenAI Python Client** | LLM & image model API calls |
| **OpenRouter** | LLM/image model gateway (Flux, Qwen, Gemini) |
| **Pydantic** | Request/response validation |
| **aiohttp** | Async HTTP requests for image generation |
| **python-dotenv** | Environment variable management |

---

## 🐳 Docker

### Build

```bash
docker build -t ai-design-visualization .
```

### Run

```bash
docker run -p 8000:8000 --env-file .env ai-design-visualization
```

The service is also included in the project's root `compose.yaml` for orchestrated deployment with other microservices.

---

## 🏃 Local Development

### Prerequisites

- Python ≥ 3.12
- [uv](https://docs.astral.sh/uv/) package manager

### Setup

```bash
# Install dependencies
uv sync

# Run the server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Interactive Docs

Once running, visit:

- **Swagger UI** — [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc** — [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🧪 Testing

Run the design agent standalone:

```bash
python ai_agents/design_agent.py "minimalist geometric pattern with blue and gold"
```

This generates a design and saves it to `output/design_preview.png`.

---

## 📜 License

Part of the **Online Mart** project.
