"""
MasOrange TV Agent — punto de entrada.

Modos:
  python main.py          → lanza el servidor FastAPI (interfaz TV + API)
  python main.py run      → modo CLI interactivo (ADK terminal)
  python main.py web      → UI web de depuración de ADK
"""

import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

os.environ.setdefault("PYTHONUTF8", "1")
os.environ.setdefault("NO_PROXY", "*")

# Cargar .env
_ROOT = Path(__file__).resolve().parent
for _p in [_ROOT / ".env", _ROOT.parent / ".env"]:
    if _p.exists():
        load_dotenv(_p)
        break


def run_server():
    """Lanza el servidor FastAPI con la interfaz TV en http://localhost:8000"""
    print("=" * 60)
    print("  MasOrange TV Agent — Servidor Web")
    print("=" * 60)
    print()
    print("  🌐  Interfaz TV :  http://localhost:8000")
    print("  📡  API chat    :  http://localhost:8000/api/chat")
    print("  ❤️   Health      :  http://localhost:8000/health")
    print()
    print("  Pulsa Ctrl+C para detener.")
    print()

    env = dict(os.environ, PYTHONUTF8="1", NO_PROXY="*")
    subprocess.run(
        [sys.executable, "-m", "uvicorn", "server:api",
         "--host", "0.0.0.0", "--port", "8000", "--reload"],
        env=env,
        cwd=str(_ROOT),
    )


def run_cli():
    """Modo terminal interactivo (adk run app)."""
    print("\nIniciando agente en modo terminal interactivo (ADK CLI)...")
    subprocess.run(
        [sys.executable, "-m", "google.adk.cli", "run", "app"],
        env=dict(os.environ, PYTHONUTF8="1", NO_PROXY="*"),
        cwd=str(_ROOT),
    )


def run_adk_web():
    """UI web de depuración de ADK en http://127.0.0.1:8000"""
    print("\nIniciando interfaz web de depuración ADK...")
    subprocess.run(
        [sys.executable, "-m", "google.adk.cli", "web", "app"],
        env=dict(os.environ, PYTHONUTF8="1", NO_PROXY="*"),
        cwd=str(_ROOT),
    )


def main():
    print("=" * 60)
    print("  MasOrange TV Agent — Google ADK + Claude")
    print("=" * 60)

    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode in ("server", "web-tv"):
            run_server()
        elif mode == "run":
            run_cli()
        elif mode in ("web", "adk-web"):
            run_adk_web()
        else:
            print(f"Modo desconocido: {mode}")
            print("Uso: python main.py [server|run|web]")
        return

    # Menú interactivo
    print()
    print("  1. Servidor web TV (interfaz HTML + API)  [recomendado]")
    print("  2. Terminal ADK (adk run)")
    print("  3. UI depuración ADK (adk web)")
    print("  4. Salir")
    print()

    try:
        choice = input("  Elige una opción (1-4): ").strip()
        if choice == "1":
            run_server()
        elif choice == "2":
            run_cli()
        elif choice == "3":
            run_adk_web()
        elif choice == "4":
            print("Hasta luego.")
        else:
            print("Opción no válida. Lanzando servidor web por defecto…")
            run_server()
    except (KeyboardInterrupt, EOFError):
        print("\nSaliendo…")


if __name__ == "__main__":
    main()
