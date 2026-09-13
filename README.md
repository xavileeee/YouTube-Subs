[![CI](https://github.com/xavileeee/YouTube-Subs/actions/workflows/ci.yml/badge.svg)](https://github.com/xavileeee/YouTube-Subs/actions/workflows/ci.yml) [![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/) [![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

# YouTube-Subs 🚀

Aplicación web y herramienta CLI en Python para extraer, descargar y limpiar subtítulos (incluidos los autogenerados por IA) de vídeos de YouTube.

---

## ✅ Características

- Descarga subtítulos en cualquier idioma (**es**, **en**, **fr**, **de**, etc.), buscando primero subtítulos subidos manualmente y, en su defecto, autogenerados.
- **CLI Interactivo y Directo**: Asistente paso a paso o comandos de consola con múltiples opciones de formateo y exportación.
- **Aplicación Web (Flask)**: Interface web moderna y minimalista con vista previa Raw (original) y Limpia (párrafos formateados sin marcas de tiempo).
- **API REST (JSON)**: Endpoint programático `/api/fetch` para consumir el servicio de extracción desde otras aplicaciones o scripts.
- **Despliegue en Producción**: Configurado y desplegado en servidor Proxmox VE con WSGI `gunicorn` y supervisión `systemd`.

---

## 🛠️ Requisitos

- Python 3.10+ (o usa Codespaces / DevContainer)
- `pip install -r requirements.txt`

---

## 🚀 Uso del Proyecto

### 💻 1. CLI (Línea de Comandos)

#### Modo Interactivo (Asistente paso a paso)
Si ejecutas el script sin argumentos, se abrirá un asistente interactivo en la terminal:

```bash
python download_subs.py
```

#### Modo Directo (Argumentos)
```bash
# Uso básico (descarga en español y muestra versiones Raw y Limpia)
python download_subs.py "https://www.youtube.com/watch?v=VIDEO_ID"

# Especificar idioma y guardar el resultado en un archivo .txt
python download_subs.py "https://www.youtube.com/watch?v=VIDEO_ID" --lang en --output transcripcion.txt

# Mostrar solo la transcripción limpia
python download_subs.py "https://www.youtube.com/watch?v=VIDEO_ID" --clean-only

# Forzar el modo interactivo
python download_subs.py -i
```

**Opciones del CLI:**
- `-l`, `--lang`: Código de idioma (`es`, `en`, `fr`, `de`, etc. Por defecto: `es`).
- `--clean-only`: Imprime únicamente la versión limpia (sin timestamps ni repeticiones).
- `--raw-only`: Imprime únicamente la versión original (raw).
- `-o`, `--output`: Guarda el resultado en la ruta de archivo `.txt` indicada.
- `-i`, `--interactive`: Inicia el asistente interactivo.

#### Ejecutar CLI de forma remota en tu Servidor por SSH
Desde tu máquina local:
```bash
ssh -t root@192.168.1.122 "cd /opt/youtube-subs && ./venv/bin/python download_subs.py"
```

---

### 🌐 2. Aplicación Web

#### Producción
Acceso directo a la aplicación desplegada en producción:
- **[https://subs.xavilee.com](https://subs.xavilee.com)**

#### Desarrollo Local
Inicia la app Flask localmente:

```bash
python app.py
```
Abre `http://localhost:5555` en tu navegador.

---

### 🔌 3. API REST / JSON (Consumo Programático)

Puedes enviar peticiones `POST` a la API para recibir los subtítulos en formato JSON:

- **Endpoint**: `POST https://subs.xavilee.com/api/fetch`
- **Body (JSON)**: `{"url": "https://www.youtube.com/watch?v=VIDEO_ID", "lang": "es"}`

#### Ejemplo cURL:
```bash
curl -X POST https://subs.xavilee.com/api/fetch \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=VIDEO_ID", "lang": "es"}'
```

#### Ejemplo Python:
```python
import requests

response = requests.post(
    "https://subs.xavilee.com/api/fetch",
    json={"url": "https://www.youtube.com/watch?v=VIDEO_ID", "lang": "es"}
)
data = response.json()
print("Limpia:\n", data["cleaned"])
```

#### Respuesta de la API:
```json
{
  "success": true,
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "lang": "es",
  "raw": "...",
  "cleaned": "..."
}
```

---

## 🧪 Tests

Ejecuta las pruebas unitarias con `pytest`:

```bash
pytest
```

---

## 📁 Archivos Importantes

- `download_subs.py` — Lógica de extracción, deduplicación y CLI.
- `app.py` — Aplicación Flask y API REST JSON (`/api/fetch`).
- `templates/index.html` — Interfaz web responsive en Bootstrap 5.
- `tests/test_cleaning.py` — Pruebas unitarias del algoritmo de limpieza.

---

## 📜 Licencia

MIT
