# 💻 Guía Rápida de Instalación en Portátil Personal (100% Gratis y Sin Tarjeta)

> Como ya has hecho el `git clone` del repositorio, cuando vayas a instalarlo más tarde solo tienes que seguir estos **3 pasos rápidos** (tardarás menos de 2 minutos).

---

## Paso 0 (Opcional): Traerte este archivo si ya habías clonado antes
Si hiciste el `git clone` antes de crearse esta guía, abre la terminal dentro de la carpeta `TIBI_AgenteIA` y ejecuta:
```powershell
git pull origin main
```

---

## Paso 1: Conseguir tu API Key 100% Gratuita (30 segundos, cero datos bancarios)

Elige **una** de estas dos opciones gratuitas (ninguna pide tarjeta de crédito ni datos bancarios):

### Opción A — Google AI Studio (Recomendada, motor nativo `gemini-2.5-flash`)
1. Entra con tu cuenta de Gmail personal en: 👉 **[https://aistudio.google.com/apikey](https://aistudio.google.com/apikey)**
2. Haz clic en el botón azul **"Create API key"**.
3. Copia la clave generada (empieza por **`AIzaSy...`**).

### Opción B — Groq Cloud (Alternativa gratuita ultrarrápida con `llama-3.3-70b`)
1. Entra en: 👉 **[https://console.groq.com/keys](https://console.groq.com/keys)**
2. Inicia sesión gratis con Google/GitHub y pulsa **"Create API Key"**.
3. Copia la clave generada (empieza por **`gsk_...`**).

---

## Paso 2: Ejecutar el Instalador Automático

1. Entra en la carpeta **`TIBI_AgenteIA`** de tu portátil personal.
2. Haz doble clic en **`instalar.bat`** *(o abre una terminal en esa carpeta y escribe `.\instalar.bat`)*.
   - **¿Qué hará solo?**
     - Comprobará que tengas **Python 3.11 o 3.12** instalado en tu portátil *(si no lo tuvieras, descárgalo de [python.org/downloads](https://www.python.org/downloads/) marcando la casilla "Add Python to PATH")*.
     - Creará automáticamente el entorno virtual `.venv`.
     - Instalará todas las librerías de `requirements.txt`.
     - Al final te preguntará por pantalla: **`Introduce tu API KEY`**.
3. Pega tu clave **`AIzaSy...`** (o `gsk_...`) y pulsa **Enter**.
   - El script detectará por el prefijo qué proveedor es y creará el archivo `.env` automáticamente.

---

## Paso 3: Arrancar TIBI para la Demo

Cada vez que quieras abrir el proyecto:
- Haz doble clic en **`Iniciar TIBI.bat`** (o en `iniciar.bat`).
- Se levantará el servidor local en `http://localhost:8000` y se abrirá automáticamente tu navegador con la interfaz de **MasOrange TV** y el chat de **TIBI** listo para usar.

---

### 💡 Solución rápida si prefieres crear el `.env` a mano
Si en algún momento quieres cambiar de clave sin volver a ejecutar `instalar.bat`, basta con crear o editar el archivo llamado **`.env`** en la raíz de `TIBI_AgenteIA` con estas dos líneas:

```env
GEMINI_API_KEY=AIzaSy_PEGA_AQUI_TU_CLAVE
GEMINI_MODEL=gemini-2.5-flash
```
*(O si usas Groq)*:
```env
GROQ_API_KEY=gsk_PEGA_AQUI_TU_CLAVE
GROQ_MODEL=groq/llama-3.3-70b-versatile
```
