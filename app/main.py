"""FastAPI entry point for ScriptForge AI."""

import re
from contextlib import asynccontextmanager
from io import BytesIO
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from app.database import get_script, initialize_database, list_scripts, save_script
from app.models import HistoryItem, ScriptRequest, ScriptResponse
from app.services.exporter import build_pdf_export, build_text_export
from app.services.generator import generate_script


APP_DIR = Path(__file__).resolve().parent
STATIC_DIR = APP_DIR / "static"


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="ScriptForge AI API",
    version="1.0.0",
    description="Generate, save, and export structured YouTube video scripts.",
    lifespan=lifespan,
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health", tags=["System"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/generate", response_model=ScriptResponse, status_code=201, tags=["Scripts"])
def create_script(request: ScriptRequest) -> dict:
    try:
        generated = generate_script(request.topic, request.style.value, request.length.value)
        script_id = save_script(generated)
        saved = get_script(script_id)
        if saved is None:
            raise RuntimeError("Saved script could not be loaded")
        return saved
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail="Script generation failed. Please try again.") from error


@app.get("/api/scripts", response_model=list[HistoryItem], tags=["Scripts"])
def history(limit: int = Query(default=10, ge=1, le=50)) -> list[dict]:
    return list_scripts(limit)


@app.get("/api/scripts/{script_id}", response_model=ScriptResponse, tags=["Scripts"])
def script_detail(script_id: int) -> dict:
    script = get_script(script_id)
    if script is None:
        raise HTTPException(status_code=404, detail="Script not found")
    return script


def _download_name(topic: str, extension: str) -> str:
    safe_topic = re.sub(r"[^a-zA-Z0-9]+", "-", topic).strip("-").lower()[:55]
    return f"{safe_topic or 'youtube-script'}.{extension}"


@app.get("/api/scripts/{script_id}/download.txt", tags=["Exports"])
def download_text(script_id: int) -> StreamingResponse:
    script = get_script(script_id)
    if script is None:
        raise HTTPException(status_code=404, detail="Script not found")
    return StreamingResponse(
        BytesIO(build_text_export(script)),
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{_download_name(script["topic"], "txt")}"'},
    )


@app.get("/api/scripts/{script_id}/download.pdf", tags=["Exports"])
def download_pdf(script_id: int) -> StreamingResponse:
    script = get_script(script_id)
    if script is None:
        raise HTTPException(status_code=404, detail="Script not found")
    return StreamingResponse(
        BytesIO(build_pdf_export(script)),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{_download_name(script["topic"], "pdf")}"'},
    )

