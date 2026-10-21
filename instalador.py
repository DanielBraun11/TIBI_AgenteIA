"""
Instalador de MasOrange TV Agent — TIBI
=======================================
Configura el entorno virtual, instala las dependencias y crea el fichero .env
con tu token personal del proxy corporativo LiteLLM.

Uso:
  python instalador.py
"""

import os
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent


# ─────────────────────────────────────────────────────────────────────────────
# UTILIDADES DE PRESENTACIÓN
# ─────────────────────────────────────────────────────────────────────────────

def _h(text: str):
    """Imprime un encabezado de sección."""
    print()
    print("─" * 60)
    print(f"  {text}")
    print("─" * 60)


def _ok(text: str):
    print(f"  ✅  {text}")


def _info(text: str):
    print(f"  ℹ️   {text}")


def _warn(text: str):
    print(f"  ⚠️   {text}")


def _err(text: str):
    print(f"  ❌  {text}")


# ─────────────────────────────────────────────────────────────────────────────
# PASOS DE INSTALACIÓN
# ─────────────────────────────────────────────────────────────────────────────

def check_python():
    v = sys.version_info
    if v.major < 3 or (v.major == 3 and v.minor < 10):
        _err(f"Se necesita Python 3.10 o superior (tienes {v.major}.{v.minor}.{v.micro}).")
        _info("Descárgalo en https://www.python.org/downloads/")
        sys.exit(1)
    _ok(f"Python {v.major}.{v.minor}.{v.micro} encontrado.")


def ask_token() -> str:
    _h("🔑  Token / API Key del modelo de IA")
    print()
    print("  Puedes usar cualquiera de estas 3 opciones:")
    print("  1) [PORTÁTIL PERSONAL - 100% GRATIS SIN TARJETA] Google AI Studio (Gemini):")
    print("     Entra con tu Gmail en https://aistudio.google.com/apikey")
    print("     Pulsa 'Create API key' y pega tu clave (empieza por AIza...).")
    print()
    print("  2) [PORTÁTIL PERSONAL - 100% GRATIS SIN TARJETA] Groq Cloud (Llama 3.3 70B):")
    print("     Entra en https://console.groq.com/keys y pega tu clave (empieza por gsk_...).")
    print()
    print("  3) [RED CORPORATIVA MASORANGE] Proxy LiteLLM:")
    print("     Introduce tu token corporativo (empieza por sk-...).")
    print()

    while True:
        try:
            token = input("  Introduce tu API Key (AIza... / gsk_... / sk-...): ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            _warn("Instalación cancelada por el usuario.")
            sys.exit(0)

        if token:
            return token
        _warn("El token no puede estar vacío. Inténtalo de nuevo.")


def create_env(token: str):
    env_path = ROOT / ".env"
    if token.startswith("AIza"):
        content = (
            "# ──────────────────────────────────────────────────────────────\n"
            "#  MasOrange TV Agent — Modo Personal Gratuito (Google AI Studio)\n"
            "# ──────────────────────────────────────────────────────────────\n\n"
            "OFFLINE_MODE=false\n"
            f"GEMINI_API_KEY={token}\n"
            f"GOOGLE_API_KEY={token}\n"
            "GEMINI_MODEL=gemini-2.5-flash\n"
        )
    elif token.startswith("gsk_"):
        content = (
            "# ──────────────────────────────────────────────────────────────\n"
            "#  MasOrange TV Agent — Modo Personal Gratuito (Groq Cloud)\n"
            "# ──────────────────────────────────────────────────────────────\n\n"
            "OFFLINE_MODE=false\n"
            f"GROQ_API_KEY={token}\n"
            "GROQ_MODEL=groq/llama-3.3-70b-versatile\n"
        )
    else:
        content = (
            "# ──────────────────────────────────────────────────────────────\n"
            "#  MasOrange TV Agent — variables de entorno\n"
            "#  Generado por el instalador. NO compartas ni subas este fichero.\n"
            "# ──────────────────────────────────────────────────────────────\n"
            "\n"
            "OFFLINE_MODE=false\n"
            "\n"
            "# Proxy corporativo LiteLLM → Claude\n"
            f"ANTHROPIC_AUTH_TOKEN={token}\n"
            "ANTHROPIC_BASE_URL=https://llm.tools.cloud.masorange.es\n"
            "ANTHROPIC_MODEL=anthropic/claude-sonnet-4-5\n"
            "\n"
            "# (Opcional) Desactiva betas experimentales de Claude Code\n"
            "CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1\n"
        )
    env_path.write_text(content, encoding="utf-8")
    _ok("Fichero .env creado con tu token.")


def create_venv() -> Path:
    venv_path = ROOT / ".venv"
    if venv_path.exists():
        _info("El entorno virtual ya existe — se actualizarán las dependencias.")
    else:
        print("  ⚙️   Creando entorno virtual (.venv)… ", end="", flush=True)
        subprocess.run(
            [sys.executable, "-m", "venv", str(venv_path)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print("listo.")
    return venv_path


def install_deps(venv_path: Path):
    reqs = ROOT / "requirements.txt"
    if not reqs.exists():
        _warn("No se encontró requirements.txt — se omite la instalación de paquetes.")
        return

    pip_exe = (
        venv_path / "Scripts" / "pip.exe"
        if sys.platform == "win32"
        else venv_path / "bin" / "pip"
    )

    print()
    print("  📦  Instalando dependencias (puede tardar unos minutos)…")
    result = subprocess.run(
        [str(pip_exe), "install", "-r", str(reqs), "--quiet"],
        capture_output=False,
    )
    if result.returncode != 0:
        _err("Hubo un error instalando las dependencias.")
        _info("Revisa tu conexión a internet y vuelve a ejecutar el instalador.")
        sys.exit(1)
    _ok("Dependencias instaladas correctamente.")


def create_launcher(venv_path: Path):
    """Crea un script de lanzamiento fácil de ejecutar."""
    if sys.platform == "win32":
        launcher = ROOT / "Iniciar TIBI.bat"
        content = (
            "@echo off\n"
            "chcp 65001 > nul\n"
            'cd /d "%~dp0"\n'
            "echo.\n"
            "echo  =========================================\n"
            "echo   MasOrange TV Agent ^(TIBI^) arrancando...\n"
            "echo  =========================================\n"
            "echo.\n"
            "echo  Interfaz web: http://localhost:8000\n"
            "echo  Pulsa Ctrl+C para detener.\n"
            "echo.\n"
            '.venv\\Scripts\\python.exe main.py server\n'
            "pause\n"
        )
        launcher.write_text(content, encoding="utf-8")
        _ok(f"Lanzador creado: '{launcher.name}'")
    else:
        launcher = ROOT / "iniciar_tibi.sh"
        content = (
            "#!/bin/bash\n"
            'cd "$(dirname "$0")"\n'
            "echo ''\n"
            "echo ' MasOrange TV Agent (TIBI) arrancando...'\n"
            "echo ' Interfaz web: http://localhost:8000'\n"
            "echo ''\n"
            ".venv/bin/python main.py server\n"
        )
        launcher.write_text(content, encoding="utf-8")
        launcher.chmod(0o755)
        _ok(f"Lanzador creado: '{launcher.name}'")

    return launcher


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print()
    print("=" * 60)
    print("   📺  MasOrange TV Agent — TIBI  — Instalador")
    print("=" * 60)

    _h("1/4  Verificando Python")
    check_python()

    token = ask_token()

    _h("2/4  Creando configuración (.env)")
    create_env(token)

    _h("3/4  Preparando entorno Python")
    venv_path = create_venv()
    install_deps(venv_path)

    _h("4/4  Creando acceso directo")
    launcher = create_launcher(venv_path)

    print()
    print("=" * 60)
    print("   🎉  ¡Instalación completada con éxito!")
    print("=" * 60)
    print()
    print("  Para iniciar el agente:")
    if sys.platform == "win32":
        print(f"  → Haz doble clic en '{launcher.name}'")
        print("    o ejecuta:  .venv\\Scripts\\python.exe main.py")
    else:
        print(f"  → Ejecuta:  ./{launcher.name}")
    print()
    print("  La interfaz TV estará disponible en:")
    print("  → http://localhost:8000")
    print()

    if sys.platform == "win32":
        try:
            input("  Pulsa ENTER para salir… ")
        except (EOFError, KeyboardInterrupt):
            pass


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Instalación cancelada.")
    except subprocess.CalledProcessError as exc:
        _err(f"Error durante la instalación: {exc}")
        _info("Asegúrate de tener conexión a internet y Python 3.10+.")
        if sys.platform == "win32":
            try:
                input("\n  Pulsa ENTER para salir… ")
            except (EOFError, KeyboardInterrupt):
                pass
        sys.exit(1)
