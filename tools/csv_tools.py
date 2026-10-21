"""
Herramientas de acceso a los ficheros CSV de clientes.
Usadas por los sub-agentes de contraseña y servicios.
"""

import csv
import logging
import secrets
import string
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

logger = _make_logger("tv_agent.csv_tools", "csv_tools.log")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_BASE_DIR = Path(__file__).resolve().parent.parent   # tv_agent/
_FICHEROS  = _BASE_DIR / "ficheros"
_CSV_CRED  = _FICHEROS / "cliente_credencial 1.csv"
_CSV_SVC   = _FICHEROS / "usuarios_servicios.csv"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _generar_password(longitud: int = 10) -> str:
    chars = string.ascii_letters + string.digits
    return "".join(secrets.choice(chars) for _ in range(longitud))

# ---------------------------------------------------------------------------
# Herramientas exportadas al agente
# ---------------------------------------------------------------------------

def verificar_cliente(dni: str, login: str) -> str:
    """Verifica que el cliente existe en el sistema a partir de su DNI y número
    de teléfono fijo (login). Devuelve confirmación o mensaje de error.

    Args:
        dni:   Número de DNI del cliente, por ejemplo '95822412L'.
        login: Número de teléfono fijo del cliente, por ejemplo '985822412'.

    Returns:
        Cadena de texto con el resultado de la verificación.
    """
    dni_norm  = dni.strip().upper()
    login_norm = login.strip()
    logger.info("[verificar_cliente] DNI=%s login=%s", dni_norm, login_norm)

    try:
        with open(_CSV_CRED, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if (row["DNI"].strip().upper() == dni_norm
                        and row["login"].strip() == login_norm):
                    logger.info("[verificar_cliente] Cliente ENCONTRADO: DNI=%s", dni_norm)
                    return (
                        f"CLIENTE_VERIFICADO: El cliente con DNI={dni_norm} y teléfono "
                        f"{login_norm} existe en el sistema y está correctamente identificado."
                    )
    except FileNotFoundError:
        logger.error("[verificar_cliente] No se encontró el fichero: %s", _CSV_CRED)
        return f"ERROR_FICHERO: No se encontró el fichero de clientes en {_CSV_CRED}."
    except Exception as exc:
        logger.exception("[verificar_cliente] Error inesperado")
        return f"ERROR: {exc}"

    logger.warning("[verificar_cliente] Cliente NO encontrado: DNI=%s login=%s", dni_norm, login_norm)
    return (
        f"CLIENTE_NO_ENCONTRADO: No existe ningún cliente con DNI={dni_norm} y "
        f"teléfono {login_norm}. Por favor, revisa los datos proporcionados."
    )


def restablecer_contrasena(dni: str) -> str:
    """Genera una nueva contraseña aleatoria para el cliente y la actualiza en
    el fichero CSV. Solo debe llamarse tras verificar al cliente.

    Args:
        dni: Número de DNI del cliente, por ejemplo '95822412L'.

    Returns:
        Cadena con la nueva contraseña generada o mensaje de error.
    """
    dni_norm = dni.strip().upper()
    logger.info("[restablecer_contrasena] Iniciando restablecimiento para DNI=%s", dni_norm)

    nueva_pass = _generar_password(10)

    try:
        rows: list[dict] = []
        fieldnames: list[str] = []
        found = False

        with open(_CSV_CRED, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = list(reader.fieldnames or [])
            for row in reader:
                if row["DNI"].strip().upper() == dni_norm:
                    row["contraseña"] = nueva_pass
                    found = True
                    logger.debug("[restablecer_contrasena] Fila actualizada en memoria DNI=%s", dni_norm)
                rows.append(dict(row))

        if not found:
            logger.warning("[restablecer_contrasena] DNI no encontrado: %s", dni_norm)
            return f"ERROR: No se encontró el cliente con DNI={dni_norm} para actualizar la contraseña."

        with open(_CSV_CRED, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        logger.info("[restablecer_contrasena] CSV actualizado OK. DNI=%s", dni_norm)
        return (
            f"CONTRASEÑA_RESTABLECIDA: La nueva contraseña del cliente con DNI={dni_norm} "
            f"es: **{nueva_pass}**. El fichero CSV ha sido actualizado correctamente. "
            f"Comunica esta contraseña al cliente y recuérdale que debe cambiarla en su "
            f"próximo acceso."
        )

    except FileNotFoundError:
        logger.error("[restablecer_contrasena] Fichero no encontrado: %s", _CSV_CRED)
        return f"ERROR_FICHERO: No se encontró el fichero {_CSV_CRED}."
    except Exception as exc:
        logger.exception("[restablecer_contrasena] Error inesperado")
        return f"ERROR: {exc}"


def comprobar_servicio(dni: str, servicio: str) -> str:
    """Comprueba si el cliente tiene contratado un servicio de valor añadido
    (NETFLIX, HBO, PRIME).

    Args:
        dni:      Número de DNI del cliente, por ejemplo '95822412L'.
        servicio: Nombre del servicio: 'NETFLIX', 'HBO' o 'PRIME'.

    Returns:
        Cadena indicando si el cliente tiene o no el servicio.
    """
    dni_norm = dni.strip().upper()

    # Normalizar alias habituales
    _alias = {
        "HBO MAX": "HBO", "HBOMAX": "HBO",
        "AMAZON PRIME": "PRIME", "AMAZON PRIME VIDEO": "PRIME", "PRIME VIDEO": "PRIME",
    }
    svc_norm = _alias.get(servicio.strip().upper(), servicio.strip().upper())

    logger.info("[comprobar_servicio] DNI=%s servicio=%s", dni_norm, svc_norm)

    try:
        with open(_CSV_SVC, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if (row["DNI"].strip().upper() == dni_norm
                        and row["servicio"].strip().upper() == svc_norm):
                    logger.info("[comprobar_servicio] Servicio %s ACTIVO para DNI=%s", svc_norm, dni_norm)
                    return (
                        f"SERVICIO_ACTIVO: El cliente con DNI={dni_norm} SÍ tiene "
                        f"contratado el servicio {svc_norm}. Puedes proceder a gestionar "
                        f"la incidencia."
                    )
    except FileNotFoundError:
        logger.error("[comprobar_servicio] Fichero no encontrado: %s", _CSV_SVC)
        return f"ERROR_FICHERO: No se encontró el fichero de servicios en {_CSV_SVC}."
    except Exception as exc:
        logger.exception("[comprobar_servicio] Error inesperado")
        return f"ERROR: {exc}"

    logger.warning("[comprobar_servicio] Servicio %s NO contratado para DNI=%s", svc_norm, dni_norm)
    return (
        f"SERVICIO_NO_CONTRATADO: El cliente con DNI={dni_norm} NO tiene "
        f"contratado el servicio {svc_norm}. No es posible gestionar la incidencia "
        f"de acceso ya que el servicio no está incluido en su tarifa."
    )
