# PaperSoul 📄

**API de extracción de texto desde archivos PDF con detección de duplicados.**

Proyecto académico — Universidad Tecnológica Nacional, Facultad Regional San Rafael  
Ingeniería en Sistemas de la Información · Desarrollo de Software 2026

---

## Descripción

PaperSoul es una API REST construida con FastAPI que permite subir archivos PDF, extraer su contenido de texto y persistirlo en MongoDB. Implementa detección de duplicados mediante hashes SHA-256, validación completa del archivo y extracción con fallback OCR para documentos escaneados.

---

## Stack tecnológico

- **Python 3.13** — lenguaje principal
- **FastAPI** — framework web async
- **uv** — gestor de paquetes y entornos virtuales
- **MongoDB 8.2** — base de datos no relacional
- **Motor + Beanie** — driver async y ODM para MongoDB
- **PyMuPDF** — extracción de texto de PDFs digitales
- **Tesseract OCR + pdf2image** — extracción de texto de PDFs escaneados
- **Docker + Docker Compose** — contenerización del entorno completo

---

## Metodología y principios

- **TDD** — tests escritos antes que el código
- **Clean Code** — nombres descriptivos, funciones pequeñas, sin comentarios obvios
- **SOLID, DRY, KISS, YAGNI**
- **12 Factor App** — código base, dependencias, configuración
- **Arquitectura de tres capas** — Presentación, Negocio, Datos

---

## Estructura del proyecto

```
.
├── app/
│   ├── main.py                          # Punto de entrada FastAPI
│   ├── core/
│   │   ├── config.py                    # Settings con Pydantic Settings
│   │   ├── exceptions.py                # Excepciones de dominio
│   │   └── logging.py                   # Configuración de logging
│   ├── db/
│   │   └── database.py                  # Conexión MongoDB con Motor + Beanie
│   ├── models/
│   │   ├── user.py                      # Documento MongoDB para usuarios
│   │   └── pdf_document.py              # Documento MongoDB para PDFs
│   ├── schemas/
│   │   ├── user.py                      # Schemas Pydantic para usuarios
│   │   └── pdf.py                       # Schemas Pydantic para PDFs
│   ├── repositories/
│   │   ├── base.py                      # Repositorio base genérico
│   │   ├── user_repository.py           # Repositorio de usuarios
│   │   └── pdf_repository.py            # Repositorio de PDFs (búsqueda por hash)
│   ├── services/
│   │   ├── user_service.py              # Lógica de negocio de usuarios
│   │   ├── pdf_extraction_service.py    # Extracción con PyMuPDF + OCR
│   │   ├── pdf_validator.py             # Validaciones del archivo PDF
│   │   └── hashing_service.py           # Hashes SHA-256 para deduplicación
│   ├── api/
│   │   └── v1/
│   │       ├── router.py                # Router principal API v1
│   │       └── endpoints/
│   │           └── pdf.py               # POST /api/v1/pdfs/extract
│   └── tests/
│       ├── conftest.py                  # Fixtures compartidos
│       ├── api/
│       │   ├── test_health.py
│       │   └── v1/endpoints/
│       │       └── test_pdf_endpoints.py
│       ├── repositories/
│       │   └── test_pdf_repository.py
│       └── services/
│           ├── pdf_validation_test.py
│           ├── test_hashing_service.py
│           ├── test_hashing_service_integration.py
│           └── test_pdf_extraction_service.py
├── Dockerfile                           # Imagen Docker de la API
├── docker-compose.yml                   # Entorno completo (api + mongodb + mongo-express)
├── pyproject.toml                       # Dependencias y configuración del proyecto
├── .env.example                         # Variables de entorno de referencia
└── uv.lock                              # Lock de dependencias
```

---

## Variables de entorno

Copiá `.env.example` a `.env` y completá los valores:

```bash
cp .env.example .env
```

| Variable | Descripción | Valor por defecto |
|---|---|---|
| `PROJECT_NAME` | Nombre de la aplicación | `PaperSoul` |
| `VERSION` | Versión de la API | `1.0.0` |
| `API_V1_STR` | Prefijo de la API | `/api/v1` |
| `MONGODB_URL` | URL de conexión a MongoDB | `mongodb://localhost:27017/fastapi_db` |
| `MONGODB_DATABASE` | Nombre de la base de datos | `fastapi_db` |
| `SECRET_KEY` | Clave secreta para JWT | — cambiar en producción — |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Expiración del token | `30` |
| `ALGORITHM` | Algoritmo JWT | `HS256` |
| `LOG_LEVEL` | Nivel de logging | `INFO` |
| `MAX_FILE_SIZE_BYTES` | Tamaño máximo del PDF en MB | `50` |
| `MIN_TEXT_LENGTH` | Mínimo de caracteres para considerar extracción exitosa | `10` |
| `MIN_DPI` | DPI para conversión de imágenes en OCR | `300` |
| `ROOT_USERNAME` | Usuario root de MongoDB | `admin` |
| `ROOT_PASSWORD` | Contraseña root de MongoDB | — cambiar en producción — |

---

## Instalación y ejecución local

### Requisitos previos

- Python 3.13
- [uv](https://docs.astral.sh/uv/) instalado: `pip install uv`
- MongoDB corriendo localmente o con Docker

### 1 — Clonar el repositorio

```bash
git clone https://github.com/LautaroAllolio/pdf-extraxtext-project.git
cd pdf-extraxtext-project
```

### 2 — Instalar dependencias

```bash
uv sync
```

### 3 — Configurar variables de entorno

```bash
cp .env.example .env
```

Editá `.env` y configurá `MONGODB_URL` apuntando a tu instancia de MongoDB.

### 4 — Levantar la aplicación

```bash
uv run uvicorn app.main:app --reload
```

### 5 — Correr los tests

```bash
uv run pytest -v
```

---

## Ejecución con Docker Compose

La forma más simple de levantar el entorno completo (API + MongoDB + Mongo Express) con un solo comando.

### Requisitos previos

- [Docker](https://docs.docker.com/get-docker/) instalado
- [Docker Compose](https://docs.docker.com/compose/) instalado

### 1 — Configurar variables de entorno

```bash
cp .env.example .env
```

En el `.env`, configurá las credenciales de MongoDB:

```dotenv
ROOT_USERNAME=admin
ROOT_PASSWORD=tu_password_seguro
MONGODB_URL=mongodb://admin:tu_password_seguro@mongodb:27017/?authSource=admin
MONGODB_DATABASE=fastapi_db
```

### 2 — Levantar el entorno completo

```bash
docker compose up --build
```

### 3 — Detener el entorno

```bash
# Detener sin borrar datos
docker compose down

# Detener y borrar todos los datos (volumen incluido)
docker compose down -v
```

---

## URLs principales

Una vez levantada la aplicación:

| Servicio | URL | Descripción |
|---|---|---|
| **Swagger UI** | http://localhost:8000/docs | Documentación interactiva de la API |
| **ReDoc** | http://localhost:8000/redoc | Documentación alternativa |
| **Health Check** | http://localhost:8000/health | Estado del sistema |
| **Extraer texto PDF** | `POST http://localhost:8000/api/v1/pdfs/extract` | Endpoint principal |
| **Mongo Express** | http://localhost:8081 | Interfaz web para MongoDB |

---

## Flujo de extracción de texto

```
POST /api/v1/pdfs/extract
        │
        ▼
validate_pdf_complete()
  ├── Existencia del archivo
  ├── Tamaño (máx. 50 MB)
  ├── Extensión (.pdf)
  ├── Header binario (%PDF-)
  ├── No cifrado
  └── Tiene páginas
        │
        ▼
Detección de duplicados
  ├── pdf_hash → get_by_pdf_hash()  → duplicado encontrado → retorna existente
  └── no duplicado → continúa
        │
        ▼
PdfExtractionService.extract_text()
  ├── PyMuPDF → texto suficiente → method="pymupdf"
  └── texto insuficiente → Tesseract OCR → method="ocr"
        │
        ▼
Detección de duplicados por texto
  └── text_hash → get_by_text_hash() → duplicado encontrado → retorna existente
        │
        ▼
PdfRepository.create() → persiste en MongoDB
        │
        ▼
PdfExtractResponse { filename, extracted_text, extraction_method, page_count, pdf_hash, text_hash }
```

---

## Comandos útiles

```bash
# Instalar dependencias
uv sync

# Correr tests
uv run pytest -v

# Correr tests con cobertura
uv run pytest --cov=app --cov-report=html

# Linting
uv run ruff check .
uv run ruff format .

# Type checking
uv run mypy .

# Levantar con Docker Compose
docker compose up --build

# Ver logs de un servicio específico
docker compose logs api
docker compose logs mongodb
```

---

## Equipo

| Integrante | Email |
|---|---|
| Lautaro Allolio | 46546353@alumnos.frsr.utn.edu.ar |
| Lucas Gimenez | 46397633@alumnos.frsr.utn.edu.ar |
| Valentino Pasetti | 45875426@alumnos.frsr.utn.edu.ar |

---

**UTN FRSR · Ingeniería en Sistemas · Desarrollo de Software 2026**