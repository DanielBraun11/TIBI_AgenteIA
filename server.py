"""
FastAPI backend para MasOrange TV Agent.
Sirve la interfaz HTML de la TV y expone el endpoint /api/chat
que conecta con el runner de Google ADK.
"""

import os
import sys
import uuid
import asyncio
import logging
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# ── UTF-8 + proxy ─────────────────────────────────────────────────────────────
os.environ.setdefault("PYTHONUTF8", "1")
os.environ.setdefault("NO_PROXY", "*")

# ── .env ─────────────────────────────────────────────────────────────────────
_ROOT = Path(__file__).resolve().parent
for _p in [_ROOT / ".env", _ROOT.parent / ".env"]:
    if _p.exists():
        load_dotenv(_p)
        break

# ── sys.path para importar app y tools ───────────────────────────────────────
sys.path.insert(0, str(_ROOT))

# ── Logging ───────────────────────────────────────────────────────────────────
_LOGS_DIR = _ROOT / "logs"
_LOGS_DIR.mkdir(parents=True, exist_ok=True)

_fmt = logging.Formatter(
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

def _setup_logger(name: str, filename: str) -> logging.Logger:
    lg = logging.getLogger(name)
    if lg.handlers:
        return lg
    lg.setLevel(logging.DEBUG)
    fh = logging.FileHandler(_LOGS_DIR / filename, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(_fmt)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(_fmt)
    lg.addHandler(fh)
    lg.addHandler(ch)
    return lg

logger = _setup_logger("tv_agent.server", "server.log")

# ── ADK ───────────────────────────────────────────────────────────────────────
from app.agent import app as adk_app, root_agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

session_service = InMemorySessionService()
runner = Runner(
    app=adk_app,
    session_service=session_service,
    auto_create_session=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# MODELOS PYDANTIC
# ─────────────────────────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str      = Field(..., description="Mensaje del usuario")
    session_id: str | None = Field(None, description="ID de sesión (se crea si no existe)")


class ChatResponse(BaseModel):
    reply: str        = Field(..., description="Respuesta del agente")
    session_id: str   = Field(..., description="ID de sesión activo")


# ─────────────────────────────────────────────────────────────────────────────
# FASTAPI APP
# ─────────────────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(application: FastAPI):
    logger.info("🚀 MasOrange TV Agent server arrancando…")
    yield
    logger.info("🛑 MasOrange TV Agent server detenido.")

api = FastAPI(
    title="MasOrange TV Agent API",
    description="Backend del agente de incidencias de MasOrange TV (Google ADK + Claude)",
    version="1.0.0",
    lifespan=lifespan,
)

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir la carpeta static/ para assets adicionales si los hubiera
_STATIC_DIR = _ROOT / "static"
_STATIC_DIR.mkdir(parents=True, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# RUTAS
# ─────────────────────────────────────────────────────────────────────────────

@api.get("/", include_in_schema=False)
async def serve_tv():
    """Sirve la interfaz HTML de la TV."""
    tv_html = _STATIC_DIR / "tv.html"
    if not tv_html.exists():
        raise HTTPException(status_code=404, detail="tv.html no encontrado en static/")
    return FileResponse(tv_html)


@api.get("/health")
async def health():
    active_model = (
        os.getenv("GEMINI_MODEL") if os.getenv("GEMINI_API_KEY")
        else os.getenv("GROQ_MODEL") if os.getenv("GROQ_API_KEY")
        else os.getenv("ANTHROPIC_MODEL", "anthropic/claude-sonnet-4-5")
    )
    return {
        "status": "online",
        "agent": root_agent.name,
        "model": active_model,
    }


# ─────────────────────────────────────────────────────────────────────────────
# HEARTBEAT WebSocket — cierra el servidor al cerrar la pestaña del navegador
# ─────────────────────────────────────────────────────────────────────────────
_shutdown_task: asyncio.Task | None = None
_SHUTDOWN_GRACE = 5   # segundos de espera antes de apagar (suficiente para un refresh)


async def _delayed_shutdown():
    """Espera unos segundos y apaga el proceso si nadie ha reconectado."""
    await asyncio.sleep(_SHUTDOWN_GRACE)
    logger.info("🛑 Sin clientes en %s s. Apagando servidor...", _SHUTDOWN_GRACE)
    os._exit(0)


@api.websocket("/ws/heartbeat")
async def ws_heartbeat(ws: WebSocket):
    """
    El navegador se conecta al cargar la página y envía pings cada 2 s.
    Al cerrar la pestaña el WebSocket se desconecta; si nadie reconecta en
    _SHUTDOWN_GRACE segundos, el servidor (y todos sus procesos) termina.
    Un simple refresh reconecta antes de que expire el temporizador.
    """
    global _shutdown_task

    await ws.accept()
    logger.info("🟢 [heartbeat] Cliente conectado — cancelando apagado pendiente.")

    # Cancelar cualquier apagado programado (por si es un refresh)
    if _shutdown_task and not _shutdown_task.done():
        _shutdown_task.cancel()
        _shutdown_task = None

    try:
        while True:
            await ws.receive_text()   # espera pings del cliente
    except (WebSocketDisconnect, Exception):
        logger.info("🔴 [heartbeat] Cliente desconectado — programando apagado en %s s.", _SHUTDOWN_GRACE)
        _shutdown_task = asyncio.create_task(_delayed_shutdown())


@api.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """
    Recibe un mensaje del usuario, lo pasa al agente ADK y devuelve la respuesta.
    Mantiene el contexto de conversación por session_id.
    """
    session_id = req.session_id or str(uuid.uuid4())
    logger.info("📨 [chat] session=%s msg=%.80s", session_id[:8], req.message)

    content_msg = types.Content(
        role="user",
        parts=[types.Part(text=req.message)],
    )

    raw_response = ""
    try:
        async for event in runner.run_async(
            user_id="tv_user",
            session_id=session_id,
            new_message=content_msg,
        ):
            # Capturar texto de cualquier evento que lo incluya
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        raw_response += part.text

    except Exception as exc:
        logger.exception("Error en el runner ADK")
        raise HTTPException(status_code=500, detail=f"Error en el agente: {exc}")

    if not raw_response.strip():
        raw_response = (
            "Lo siento, no obtuve respuesta del agente. "
            "Por favor, inténtalo de nuevo."
        )

    logger.info("📤 [chat] session=%s reply=%.80s", session_id[:8], raw_response)
    return ChatResponse(reply=raw_response, session_id=session_id)


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "server:api",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info",
    )
