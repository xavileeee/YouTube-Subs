[![CI](https://github.com/YOUR_GITHUB/YOUR_REPO/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_GITHUB/YOUR_REPO/actions/workflows/ci.yml) [![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/) [![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

# YouTube-Subs (Plantilla) 🚀

Pequeña plantilla para descargar subtítulos (incluyendo autogenerados) de vídeos de YouTube y mostrar la transcripción en una aplicación web simple.

**Nota:** Reemplaza `YOUR_GITHUB` y `YOUR_REPO` en los badges por tu nombre de usuario y repositorio en GitHub para que los badges funcionen correctamente.

## ✅ Características
- Descarga subtítulos en **es**, **en**, **fr**, **de** (revisa subtítulos cargados y, si no existen, busca en los autogenerados).
- CLI mínima: `download_subs.py` (pasa la URL y el idioma).
- Aplicación web en **Flask** con selector de idioma y dos vistas: **Raw** (tal cual) y **Limpia** (sin marcas de tiempo ni etiquetas).
- Preparada para **GitHub Codespaces** / DevContainer (`.devcontainer/devcontainer.json`) y con tests básicos (`pytest`).

---

## 🛠️ Requisitos
- Python 3.10+ (o usa Codespaces / DevContainer)
- `pip install -r requirements.txt`
- `yt-dlp` (se instala en `requirements.txt`)

---

## 🚀 Uso rápido

### 💻 CLI (Línea de Comandos)

#### 1. Modo Interactivo (Asistente paso a paso)
Si ejecutas el script sin argumentos, se abrirá un asistente interactivo que te guiara a través de la URL, el idioma y las opciones de guardado:

```bash
python download_subs.py
```

#### 2. Modo Directo (Argumentos)
Descargar subtítulos directamente especificando la URL y opciones:

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

**Opciones disponibles del CLI:**
- `-l`, `--lang`: Código de idioma (`es`, `en`, `fr`, `de`, etc. Por defecto: `es`).
- `--clean-only`: Imprime únicamente la versión limpia (sin timestamps ni repeticiones).
- `--raw-only`: Imprime únicamente la versión original (raw).
- `-o`, `--output`: Guarda el resultado en la ruta de archivo `.txt` indicada.
- `-i`, `--interactive`: Inicia el asistente interactivo.

---

### 🌐 Aplicación Web

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

## 🧪 Tests
Ejecuta los tests con:

```bash
pytest -q
```

---

## 📦 Dev / Codespaces
El proyecto incluye `.devcontainer/devcontainer.json` configurado para instalar dependencias automáticamente y exponer el puerto 5000.
- En Codespaces: abre el repositorio y el contenedor instalará las dependencias.
- Localmente: crea un virtualenv y ejecuta `pip install -r requirements.txt`.

---

## ✅ Preparado para GitHub Template
Este repositorio está pensado como plantilla. Para publicar en GitHub:
1. Crea un nuevo repo (p. ej. `YouTube-Subs`) y sube todo.
2. Activa la opción "Template repository" si quieres que otros puedan crear repos desde ella.

---

## 📁 Archivos importantes
- `download_subs.py` — lógica de descarga y parsing de subtítulos.
- `app.py` — aplicación Flask.
- `templates/index.html` — interfaz web.
- `.devcontainer/devcontainer.json` — configuración para Codespaces.
- `.github/workflows/ci.yml` — CI básica con `pytest`.

---

## 🤝 Contribuciones
Pull requests y mejoras bienvenidas. Añade tests para nueva funcionalidad y actualiza la documentación.

---

## 📜 Licencia
MIT

