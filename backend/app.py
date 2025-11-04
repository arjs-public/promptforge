"""PromptForge FastAPI application server module."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
from config import load_config
from ollama_client import generate_from_ollama, OllamaError
from craft import assemble_craft

from pathlib import Path
import logging

# configure logging early so DEBUG/INFO messages are emitted
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
# Quiet overly chatty third-party libraries while keeping app-level DEBUG logs.
logging.getLogger("charset_normalizer").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

app = FastAPI()
frontend_path = Path(__file__).parent.parent / "frontend"
if not frontend_path.exists():
    frontend_path = Path(__file__).parent / "frontend"

# Mount frontend static files under /static so they don't shadow API routes like /api/*
app.mount(
    "/static", StaticFiles(directory=str(frontend_path), html=True), name="static"
)


@app.get("/")
async def root():
    """Serve the frontend index.html at the site root.

    We use FileResponse instead of mounting at "/" to avoid StaticFiles
    shadowing our API routes (e.g. /api/config).
    """
    index_file = frontend_path / "index.html"
    return FileResponse(str(index_file))


from typing import Optional


class GenerateRequest(BaseModel):
    title: str = ""
    context: str = ""
    ai_role: str = ""
    additional_info: str = ""
    output_format: str = ""
    target_audience: str = ""
    model: Optional[str] = None


config = load_config()


@app.post("/api/generate")
async def generate(req: GenerateRequest):
    # use module logger so messages follow our configured format/level
    # logger.info("Processing request: %s", req)
    # logger.debug("Processing request (debug): %s", req)
    crafted = assemble_craft(req.model_dump())
    if not crafted or (isinstance(crafted, str) and not crafted.strip()):
        # logger.info("Crafted prompt empty; insufficient input")
        return JSONResponse(
            status_code=400,
            content={"ok": False, "error": "Not enough information is given."},
        )

    try:
        ollama_resp = generate_from_ollama(
            crafted,
            model=(req.model or config.get("default_model")),
            ollama_url=config.get("ollama_url"),
        )
        # logger.debug("Ollama response: %s", ollama_resp)
    except OllamaError as e:
        # logger.exception("Ollama call failed")
        return JSONResponse(status_code=502, content={"ok": False, "error": str(e)})
    return {
        "ok": True,
        "data": {"crafted_prompt": crafted, "ollama_response": ollama_resp},
    }


@app.get("/api/config")
async def get_config():
    safe = {k: v for k, v in config.items() if k not in ("api_key",)}
    return {"ok": True, "data": safe}


# Catch-all to serve frontend static files (preserve API routes precedence).
# If a requested file exists under the frontend directory, return it.
# Otherwise fall back to index.html so SPA routing works.
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    # don't interfere with API routes (they're already matched before this handler)
    requested = frontend_path / full_path
    if requested.exists() and requested.is_file():
        return FileResponse(str(requested))
    # fall back to index.html for SPA
    index_file = frontend_path / "index.html"
    return FileResponse(str(index_file))


if __name__ == "__main__":
    # When using reload or multiple workers, uvicorn requires an import string
    # (module:app) so it can re-import the app in the child processes. Use the
    # module import string to avoid the warning and preserve debug logging.
    uvicorn.run(
        "app:app",
        host=config.get("bind", "0.0.0.0"),
        port=int(config.get("port", 11435)),
        reload=False,
        workers=1,
        log_level="info",
    )
