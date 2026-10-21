"""
Simulación de llamada a la plataforma Excalibur.
Genera un fichero de texto con los datos de la incidencia.
"""

import logging
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
_LOGS_DIR = Path(__file__).resolve().parent.parent / "logs"
_LOGS_DIR.mkdir(parents=True, exist_ok=True)

_log_formatter = logging.Formatter(
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

def _make_logger(name: str, filename: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(_LOGS_DIR / filename, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(_log_formatter)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(_log_formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger

logger = _make_logger("tv_agent.excalibur", "agente_servicios.log")

# ---------------------------------------------------------------------------
# Directorio de salida para llamadas a Excalibur
# ---------------------------------------------------------------------------
_EXCALIBUR_DIR = Path(__file__).resolve().parent.parent / "excalibur_calls"

# ---------------------------------------------------------------------------
# Herramienta exportada al sub-agente de servicios
# ---------------------------------------------------------------------------

def llamar_excalibur(dni: str, login: str, servicio: str) -> str:
    """Simula una llamada a la plataforma Excalibur para registrar una incidencia
    de acceso a un servicio de valor añadido. Escribe el registro en un fichero
    de texto y devuelve el número de ticket generado.

    Solo debe llamarse si se ha confirmado que el cliente tiene contratado
    el servicio indicado.

    Args:
        dni:      DNI del cliente, por ejemplo '95822412L'.
        login:    Número de teléfono fijo (login) del cliente, por ejemplo '985822412'.
        servicio: Servicio afectado: 'NETFLIX', 'HBO' o 'PRIME'.

    Returns:
        Cadena con el número de ticket generado y el resultado de la operación.
    """
    _EXCALIBUR_DIR.mkdir(parents=True, exist_ok=True)

    now = datetime.now()
    ts_str  = now.strftime("%Y%m%d_%H%M%S")
    ts_human = now.strftime("%Y-%m-%d %H:%M:%S")

    dni_norm = dni.strip().upper()
    svc_norm = servicio.strip().upper()

    ticket_id = f"EXC-{now.strftime('%Y%m%d')}-{dni_norm[-4:]}-{svc_norm[:3]}"
    filename  = f"excalibur_{ts_str}_{dni_norm}.txt"
    filepath  = _EXCALIBUR_DIR / filename

    contenido = f"""╔══════════════════════════════════════════════════════════════╗
║      LLAMADA A PLATAFORMA EXCALIBUR — INCIDENCIA DE SERVICIO  ║
╚══════════════════════════════════════════════════════════════╝

  Ticket ID     : {ticket_id}
  Timestamp     : {ts_human}
  Agente        : agente_servicios_vas (MasOrange TV)

  ─── DATOS DEL CLIENTE ──────────────────────────────────────
  DNI           : {dni_norm}
  Login (Tfno)  : {login.strip()}

  ─── SERVICIO AFECTADO ──────────────────────────────────────
  Servicio      : {svc_norm}
  Tipo incid.   : ACCESO / VALOR AÑADIDO

  ─── RESULTADO ──────────────────────────────────────────────
  Estado        : NOTIFICADO A EXCALIBUR
  Acción        : Revisión y reactivación de acceso al servicio
  SLA           : 2 horas (gestión prioritaria)

  El cliente recibirá confirmación de resolución por SMS al
  número {login.strip()} en un plazo máximo de 2 horas.

══════════════════════════════════════════════════════════════
"""

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(contenido)

        logger.info(
            "[llamar_excalibur] Ticket %s generado. Fichero: %s",
            ticket_id, filepath
        )
        return (
            f"EXCALIBUR_OK: La incidencia ha sido registrada en la plataforma Excalibur. "
            f"Número de ticket: **{ticket_id}**. "
            f"El equipo técnico revisará el acceso al servicio {svc_norm} en un plazo "
            f"máximo de 2 horas. El cliente recibirá confirmación por SMS al {login.strip()}. "
            f"Registro guardado en: {filename}."
        )

    except Exception as exc:
        logger.exception("[llamar_excalibur] Error al escribir fichero Excalibur")
        return f"ERROR_EXCALIBUR: No se pudo registrar la llamada a Excalibur: {exc}"
