# 🛡️ CyberGuardian

**Plataforma inteligente de detección de phishing y concientización ciudadana en ciberseguridad.**

CyberGuardian analiza mensajes, correos electrónicos y enlaces sospechosos utilizando Inteligencia Artificial (Groq) y heurísticas de seguridad para determinar si representan una amenaza real. El sistema devuelve un reporte detallado con nivel de riesgo, hallazgos, recomendaciones y una explicación educativa accesible para cualquier ciudadano.

> **Estado de la plataforma pública:** La versión web pública **todavía no está desplegada**. Actualmente el sistema funciona en instalación local. El despliegue en la nube es un objetivo planificado para una etapa futura del proyecto.

---

## Tabla de contenidos

1. [Problema que resuelve](#1-problema-que-resuelve)
2. [Objetivos](#2-objetivos)
3. [Funcionalidades implementadas](#3-funcionalidades-implementadas)
4. [Características principales](#4-características-principales)
5. [Tecnologías utilizadas](#5-tecnologías-utilizadas)
6. [Arquitectura del sistema](#6-arquitectura-del-sistema)
7. [Estructura del repositorio](#7-estructura-del-repositorio)
8. [Requisitos previos](#8-requisitos-previos)
9. [Instalación local](#9-instalación-local)
10. [Configuración de variables de entorno](#10-configuración-de-variables-de-entorno)
11. [Configuración de la API de Groq](#11-configuración-de-la-api-de-groq)
12. [Ejecución del backend](#12-ejecución-del-backend)
13. [Ejecución del frontend](#13-ejecución-del-frontend)
14. [Pruebas del proyecto](#14-pruebas-del-proyecto)
15. [Solución de problemas frecuentes](#15-solución-de-problemas-frecuentes)
16. [Consideraciones de seguridad](#16-consideraciones-de-seguridad)
17. [Estado actual del desarrollo](#17-estado-actual-del-desarrollo)
18. [Funcionalidades futuras](#18-funcionalidades-futuras)
19. [Preparación para despliegue público](#19-preparación-para-despliegue-público)
20. [Bot de Telegram](#20-bot-de-telegram)

---

## 1. Problema que resuelve

El phishing y la ingeniería social son las formas de fraude cibernético más frecuentes en América Latina. Los ciudadanos reciben mensajes de texto, correos electrónicos o mensajes de WhatsApp que imitan a bancos, organismos públicos o servicios conocidos para robar credenciales o datos personales.

La mayoría de las personas no tienen herramientas ni conocimientos para detectar si un mensaje es legítimo o fraudulento. CyberGuardian busca cerrar esa brecha ofreciendo un análisis accesible, inmediato y educativo.

---

## 2. Objetivos

- Detectar intentos de phishing en textos, URLs y mensajes en lenguaje natural.
- Proporcionar un nivel de riesgo cuantificable (0–100) y cualitativo (LOW / MEDIUM / HIGH / CRITICAL).
- Explicar al usuario por qué un mensaje es o no peligroso, promoviendo la concientización.
- Registrar el historial de análisis para estadísticas y seguimiento.
- Ser accesible desde la web y, en el futuro, desde bots de mensajería.

---

## 3. Funcionalidades implementadas

| Funcionalidad | Estado |
|---|---|
| Análisis de texto/URL vía API REST (`POST /api/analyze`) | ✅ Implementado |
| Motor de IA con Groq (`openai/gpt-oss-120b` por defecto) | ✅ Implementado |
| Fallback heurístico local (sin necesidad de clave API) | ✅ Implementado |
| Persistencia del historial en SQLite | ✅ Implementado |
| Endpoint de historial (`GET /api/history`) | ✅ Implementado |
| Endpoint de salud (`GET /api/health`) | ✅ Implementado |
| Interfaz web React (Home, Analyze, Dashboard, About) | ✅ Implementado |
| Bot de Telegram (integración con orquestador) | ✅ Operativo (requiere token) |
| Bot de WhatsApp | 🔧 En desarrollo (archivo vacío) |
| Despliegue público en la nube | ⏳ Planificado |

---

## 4. Características principales

- **Análisis con IA:** El orquestador llama directamente a la API de Groq mediante HTTP, sin SDKs adicionales. Si no hay clave configurada, activa automáticamente el modo heurístico local.
- **Modo heurístico local:** Funciona sin conexión a IA externa, aplicando reglas de análisis de URLs, detección de TLDs peligrosos, listas negras internas y heurísticas de lenguaje para detectar phishing.
- **Reporte estructurado:** Cada análisis devuelve `risk_score`, `risk_level`, `findings`, `recommendations` y `educational_explanation`.
- **Historial persistente:** Todos los análisis se almacenan en una base de datos SQLite local.
- **Interfaz web moderna:** Frontend en React 18 con Tailwind CSS, Framer Motion y Recharts para visualización de datos.
- **Arquitectura extensible:** Los agentes individuales (URL, Phishing, Reputation, Education, Report) son módulos independientes que pueden integrarse con CrewAI en el futuro.

---

## 5. Tecnologías utilizadas

### Backend
| Tecnología | Versión mínima | Función |
|---|---|---|
| Python | 3.11+ | Lenguaje principal |
| FastAPI | 0.110.0 | Framework web y API REST |
| Uvicorn | 0.28.0 | Servidor ASGI |
| SQLAlchemy | 2.0.28 | ORM y acceso a base de datos |
| Pydantic | 2.6.0 | Validación de datos y esquemas |
| Requests | 2.31.0 | Llamadas HTTP a la API de Groq |
| Python-dotenv | 1.0.1 | Gestión de variables de entorno |
| SQLite | — | Base de datos local (por defecto) |
| Groq | API REST | Motor de IA para análisis de amenazas |
| CrewAI | 0.30.0 | Dependencia opcional/legado (agentes individuales) |

### Frontend
| Tecnología | Versión | Función |
|---|---|---|
| React | 18.3 | Biblioteca de interfaz de usuario |
| Vite | 5.3 | Herramienta de construcción y servidor de desarrollo |
| Tailwind CSS | 3.4 | Framework de estilos utilitarios |
| Framer Motion | 11.x | Animaciones y transiciones |
| Recharts | 2.x | Gráficos y visualización de datos |
| Axios | 1.7 | Cliente HTTP para consumo de la API |
| React Router DOM | 6.x | Navegación entre páginas |
| Lucide React | 0.395 | Biblioteca de íconos |

---

## 6. Arquitectura del sistema

```
┌─────────────────────────────────────────────────────────────┐
│                      CLIENTES                               │
│  Navegador Web (React/Vite)  │  Bot de Telegram             │
└─────────────────┬────────────┴──────────────┬──────────────┘
                  │ HTTP                       │ HTTP
                  ▼                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   BACKEND — FastAPI                         │
│                                                             │
│  POST /api/analyze  │  GET /api/history  │  GET /api/health │
│                                                             │
│  ┌────────────────────────────────────────────────────┐    │
│  │              Orchestrator (orchestrator.py)         │    │
│  │                                                     │    │
│  │  ┌─────────────────┐   ┌─────────────────────────┐ │    │
│  │  │  Groq API (IA)  │   │  Modo Heurístico Local   │ │    │
│  │  │  openai/gpt-oss │   │  URLService              │ │    │
│  │  │  -120b (HTTP)   │   │  ReputationService       │ │    │
│  │  └─────────────────┘   │  PhishingService         │ │    │
│  │         fallback ──────►  ReportService            │ │    │
│  │                        └─────────────────────────┘ │    │
│  └────────────────────────────────────────────────────┘    │
│                                                             │
│  ┌────────────────────────────────────────────────────┐    │
│  │              SQLAlchemy + SQLite                    │    │
│  │         (cyberguardian.db — local)                  │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

**Flujo de análisis:**
1. El cliente envía `POST /api/analyze` con `content` (texto o URL) y `source` (web, telegram, etc.).
2. El `Orchestrator` intenta el análisis con Groq vía HTTP.
3. Si la clave no está disponible o hay error, activa el modo heurístico local.
4. El resultado se persiste en SQLite y se devuelve al cliente.

---

## 7. Estructura del repositorio

```
CyberGuardian/
├── backend/
│   ├── agents/
│   │   ├── orchestrator.py       # Coordinador principal: Groq + fallback heurístico
│   │   ├── url_agent.py          # Agente CrewAI (opcional) para análisis de URLs
│   │   ├── phishing_agent.py     # Agente CrewAI (opcional) para detección de phishing
│   │   ├── reputation_agent.py   # Agente CrewAI (opcional) para reputación de dominios
│   │   ├── education_agent.py    # Agente CrewAI (opcional) para explicaciones educativas
│   │   └── report_agent.py       # Agente CrewAI (opcional) para compilación de reportes
│   ├── api/
│   │   ├── routes/
│   │   │   └── analysis.py       # Endpoints: /analyze, /history, /health
│   │   └── schemas/
│   │       └── analysis.py       # Esquemas Pydantic (request/response)
│   ├── database/
│   │   ├── connection.py         # Motor SQLAlchemy y sesiones
│   │   ├── repository.py         # CRUD de registros de análisis
│   │   └── migrations/           # Directorio de migraciones (actualmente vacío)
│   ├── models/
│   │   └── analysis.py           # Modelo ORM AnalysisRecord
│   ├── services/
│   │   ├── url_service.py        # Extracción y análisis heurístico de URLs
│   │   ├── reputation_service.py # Listas blancas/negras de dominios
│   │   ├── phishing_service.py   # Heurísticas de detección de phishing en texto
│   │   └── report_service.py     # Compilación del reporte heurístico final
│   └── main.py                   # Punto de entrada FastAPI
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Home.jsx          # Página de inicio
│   │   │   ├── Analyze.jsx       # Página de análisis (formulario + resultado)
│   │   │   ├── Dashboard.jsx     # Dashboard con historial y estadísticas
│   │   │   ├── About.jsx         # Información sobre el proyecto
│   │   │   └── NotFound.jsx      # Página 404
│   │   ├── components/           # Componentes reutilizables (Navbar, Footer, etc.)
│   │   ├── services/             # Cliente Axios para la API
│   │   ├── routes/AppRoutes.jsx  # Definición de rutas
│   │   └── main.jsx              # Punto de entrada React
│   ├── package.json
│   └── vite.config.js            # Vite + proxy hacia backend
├── telegram_bot/
│   └── main.py                   # Bot de Telegram (operativo con token)
├── whatsapp_bot/
│   └── bot.py                    # Bot de WhatsApp (en desarrollo)
├── tests/
│   ├── test_api.py               # Pruebas de integración de endpoints
│   └── test_agents.py            # Pruebas unitarias de servicios y agentes
├── docs/
│   └── architecture/
│       └── system_design.md      # Diseño de arquitectura del sistema
├── .env.example                  # Plantilla de variables de entorno
├── .gitignore                    # Configuración de exclusiones Git
└── requirements.txt              # Dependencias Python
```

---

## 8. Requisitos previos

Antes de instalar CyberGuardian, asegúrate de tener instalado en tu sistema:

| Herramienta | Versión mínima | Verificar con |
|---|---|---|
| Python | 3.11 | `python3 --version` |
| pip | 23.x | `pip --version` |
| Node.js | 18.x | `node --version` |
| npm | 9.x | `npm --version` |
| Git | 2.x | `git --version` |

**Recomendado:** Cuenta gratuita en [Groq Console](https://console.groq.com/keys) para habilitar el análisis con IA. Sin ella, el sistema funciona en modo heurístico local.

---

## 9. Instalación local

### Paso 1: Clonar el repositorio

```bash
git clone https://github.com/hrotzank/CyberGuardian.git
cd CyberGuardian
```

### Paso 2: Crear y activar el entorno virtual de Python

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Deberías ver `(.venv)` al inicio del prompt de tu terminal.

### Paso 3: Instalar dependencias del backend

```bash
pip install -r requirements.txt
```

### Paso 4: Crear el archivo de variables de entorno

```bash
cp .env.example .env
```

Abre `.env` con tu editor y completa los valores. Ver sección [Configuración de variables de entorno](#10-configuración-de-variables-de-entorno).

### Paso 5: Instalar dependencias del frontend

```bash
cd frontend
npm install
cd ..
```

---

## 10. Configuración de variables de entorno

Edita el archivo `.env` en la raíz del proyecto con los valores correspondientes a tu entorno:

```dotenv
# Clave de API de Groq (requerida para análisis con IA)
GROQ_API_KEY=tu_clave_groq_aqui

# Modelo a utilizar (ver sección 11)
AI_MODEL=openai/gpt-oss-120b

# Base de datos (SQLite por defecto, no requiere configuración adicional)
DATABASE_URL=sqlite:///./cyberguardian.db

# Orígenes permitidos para el frontend (CORS)
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Configuración del servidor
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=info
```

> **Importante:** El archivo `.env` nunca debe subirse a Git. Está excluido por `.gitignore`.

---

## 11. Configuración de la API de Groq

### Obtener la clave API

1. Crea una cuenta gratuita en [https://console.groq.com](https://console.groq.com).
2. Ve a la sección **API Keys** → **Create API Key**.
3. Copia la clave generada y pégala en `GROQ_API_KEY=` dentro de tu `.env`.

### Seleccionar el modelo

El sistema usa `openai/gpt-oss-120b` por defecto, verificado y disponible en la API de Groq. Puedes cambiarlo configurando `AI_MODEL` en `.env`.

Para ver la lista actualizada de modelos disponibles en tu cuenta:

```bash
curl https://api.groq.com/openai/v1/models \
  -H "Authorization: Bearer $GROQ_API_KEY" | python3 -m json.tool
```

Modelos de generación de texto verificados (oct 2026):

| ID del modelo | Contexto | Notas |
|---|---|---|
| `openai/gpt-oss-120b` | 131k tokens | Por defecto, recomendado |
| `openai/gpt-oss-20b` | 131k tokens | Más rápido, menos potente |
| `qwen/qwen3.8-27b` | 131k tokens | Alternativa open source |
| `allam-2-7b` | 4k tokens | Contexto reducido |

> **Nota:** Si el modelo seleccionado no está disponible en tu cuenta, el sistema activará automáticamente el modo heurístico local y registrará el error en los logs.

### Modo heurístico local (sin clave API)

Si no configuras `GROQ_API_KEY` o si la API de Groq no está disponible, el sistema activa automáticamente un modo de análisis local basado en:
- Extracción y análisis de URLs.
- Verificación contra listas blancas y negras de dominios.
- Detección de TLDs sospechosos (`.xyz`, `.top`, `.club`, etc.).
- Análisis de lenguaje: urgencia, amenazas, señuelos financieros.

---

## 12. Ejecución del backend

Asegúrate de tener el entorno virtual activado:

```bash
source .venv/bin/activate
```

Desde la raíz del proyecto:

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

El servidor iniciará en `http://localhost:8000`.

**Documentación interactiva de la API:**
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

**Endpoints disponibles:**

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/api/analyze` | Analiza texto o URL en busca de amenazas |
| `GET` | `/api/history` | Devuelve el historial de análisis (máx. 100) |
| `GET` | `/api/health` | Estado de la API y conexión a la base de datos |

**Ejemplo de llamada a `/api/analyze`:**

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"content": "Tu cuenta fue bloqueada. Ingresa a http://banco-seguro.xyz para reactivarla.", "source": "web"}'
```

---

## 13. Ejecución del frontend

Desde la raíz del proyecto, en una terminal separada:

```bash
cd frontend
npm run dev
```

El servidor de desarrollo Vite iniciará en `http://localhost:5173`.

El frontend está configurado con un proxy que redirige las llamadas `/api/*` al backend en `http://localhost:8000`. No requiere configuración adicional en desarrollo.

**Páginas disponibles:**

| Ruta | Descripción |
|---|---|
| `/` | Página de inicio |
| `/analyze` | Formulario de análisis de contenido |
| `/dashboard` | Historial de análisis y estadísticas |
| `/about` | Información sobre el proyecto |

---

## 14. Pruebas del proyecto

### Ejecutar todas las pruebas

Desde la raíz del proyecto con el entorno virtual activado:

```bash
source .venv/bin/activate
pytest tests/ -v
```

### Descripción de las pruebas

**`tests/test_agents.py`** — Pruebas unitarias de servicios:
- Extracción de URLs desde texto.
- Heurísticas de análisis de URLs (TLDs, keywords).
- Verificación de listas blancas y negras de dominios.
- Detección de phishing en lenguaje natural.
- Compilación de reporte heurístico.
- Fallback del orquestador al modo heurístico.

**`tests/test_api.py`** — Pruebas de integración de endpoints:
- `GET /api/health` → responde `{"status": "ok", "database": "connected"}`.
- `POST /api/analyze` con mensaje seguro → `risk_level: LOW`.
- `POST /api/analyze` con mensaje de phishing → `risk_level: CRITICAL`.
- `GET /api/history` → devuelve lista con registros.

> **Nota:** Las pruebas de API usan una base de datos temporal (`test_temp.db`) que se elimina automáticamente al finalizar. No afectan la base de datos de producción.

### Build de producción del frontend

```bash
cd frontend
npm run build
```

Los archivos compilados se generan en `frontend/dist/`.

---

## 15. Solución de problemas frecuentes

### El backend no inicia: `ModuleNotFoundError`

```bash
# Verificar que el entorno virtual está activado
source .venv/bin/activate

# Reinstalar dependencias
pip install -r requirements.txt
```

### Error CORS en el frontend

Verifica que `ALLOWED_ORIGINS` en `.env` incluye la URL exacta del frontend:

```dotenv
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

### El análisis siempre devuelve resultados heurísticos

Significa que `GROQ_API_KEY` no está configurada o es inválida. Verifica:

```bash
# Comprobar si la variable está cargada
python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); print(bool(os.getenv('GROQ_API_KEY')))"
```

Debe imprimir `True`. Si imprime `False`, el archivo `.env` no está en la raíz del proyecto o la variable está vacía.

### El modelo de Groq devuelve error 404 o 400

El ID del modelo puede haber cambiado o no estar disponible en tu cuenta. Consulta los modelos actuales:

```bash
curl https://api.groq.com/openai/v1/models -H "Authorization: Bearer $GROQ_API_KEY"
```

Actualiza `AI_MODEL` en `.env` con un ID válido de la lista.

### Las pruebas fallan con `ImportError`

Ejecuta pytest desde la raíz del proyecto, no desde dentro de `tests/`:

```bash
# Correcto
pytest tests/ -v

# Incorrecto
cd tests && pytest  # puede fallar por rutas relativas
```

### `npm install` falla

Verifica la versión de Node.js:

```bash
node --version  # debe ser 18.x o superior
```

Si usas `nvm`, activa la versión correcta:

```bash
nvm use 18
```

---

## 16. Consideraciones de seguridad

### Implementadas actualmente

- **Variables de entorno:** Todas las credenciales se gestionan mediante `.env`, excluido de Git.
- **CORS configurable:** Los orígenes permitidos se definen en `ALLOWED_ORIGINS`. No se usa `allow_origins=["*"]` con `allow_credentials=True` (configuración inválida según la especificación CORS).
- **Sin exposición de claves en logs:** El orquestador usa `logging` y nunca imprime la clave API.
- **Validación de entrada:** Los endpoints usan esquemas Pydantic con validación estricta.
- **Manejo global de errores:** FastAPI devuelve mensajes de error genéricos sin exponer detalles internos.
- **Base de datos local:** SQLite no expone puertos de red en la instalación local.

### Consideraciones para producción (no implementadas aún)

- **HTTPS obligatorio:** Configurar certificado TLS antes de cualquier despliegue público.
- **Autenticación:** No existe actualmente ningún sistema de autenticación. Si se almacenan historiales privados por usuario, es imprescindible.
- **Rate limiting:** No hay protección contra abuso de la API o solicitudes excesivas a Groq.
- **Base de datos en la nube:** SQLite no es adecuado para múltiples usuarios simultáneos. Migrar a PostgreSQL.
- **Rotación de claves:** Implementar rotación periódica de la clave de Groq.
- **Política de privacidad:** Definir qué datos se almacenan y por cuánto tiempo.

---

## 17. Estado actual del desarrollo

| Componente | Estado |
|---|---|
| Backend API (FastAPI) | ✅ Funcional |
| Análisis con Groq | ✅ Funcional |
| Modo heurístico local | ✅ Funcional |
| Base de datos SQLite | ✅ Funcional |
| Frontend React | ✅ Funcional |
| Pruebas automatizadas | ✅ Passing |
| Bot de Telegram | ✅ Operativo (requiere token) |
| Bot de WhatsApp | 🔧 En desarrollo |
| Despliegue en la nube | ⏳ Planificado |
| Autenticación de usuarios | ⏳ Planificado |
| Rate limiting | ⏳ Planificado |
| Migraciones de base de datos | ⏳ Pendiente |

---

## 18. Funcionalidades futuras

- **Despliegue público:** Hosting del frontend (Vercel / Netlify) y backend (Railway / Render / VPS).
- **Base de datos en la nube:** Migración a PostgreSQL con Alembic para migraciones.
- **Autenticación:** Sistema de cuentas para guardar histórico por usuario.
- **Bot de WhatsApp:** Integración funcional con la API de WhatsApp Business.
- **Rate limiting:** Protección contra abuso mediante slowapi o middleware personalizado.
- **Panel de administración:** Estadísticas globales, gestión de listas negras.
- **Integración con APIs externas de reputación:** VirusTotal, PhishTank, etc.
- **Soporte multilenguaje:** Análisis en inglés y portugués además de español.

---

## 19. Preparación para despliegue público

> ⚠️ **La plataforma pública todavía no está desplegada.** Esta sección documenta los requisitos técnicos identificados para cuando se realice el despliegue.

### Requisitos pendientes antes del despliegue

| Requisito | Estado |
|---|---|
| HTTPS / certificado TLS | ⏳ Pendiente |
| Hosting del frontend | ⏳ Pendiente |
| Hosting del backend | ⏳ Pendiente |
| Base de datos persistente (PostgreSQL) | ⏳ Pendiente |
| Gestión segura de secretos en la nube | ⏳ Pendiente |
| Configuración CORS para dominio público | ⏳ Pendiente |
| Rate limiting / protección contra abuso | ⏳ Pendiente |
| Política de privacidad | ⏳ Pendiente |
| Autenticación (si se almacena historial privado) | ⏳ Pendiente |
| Límites de uso de la API de Groq | ⏳ Pendiente |

### Variables de entorno para producción

```dotenv
# Producción — NO usar estos valores en desarrollo local
GROQ_API_KEY=<clave_real_de_produccion>
DATABASE_URL=postgresql://usuario:password@host:5432/cyberguardian
ALLOWED_ORIGINS=https://cyberguardian.app,https://www.cyberguardian.app
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=warning
```

---

## 20. Bot de Telegram

El bot de Telegram está implementado y es operativo. Requiere un token de bot válido obtenido mediante [@BotFather](https://t.me/BotFather) en Telegram.

### Configuración

1. Abre Telegram y busca `@BotFather`.
2. Envía `/newbot` y sigue las instrucciones para crear tu bot.
3. Copia el token recibido y agrégalo al archivo `.env`:

```dotenv
TELEGRAM_BOT_TOKEN=tu_token_de_telegram_aqui
```

### Ejecución

```bash
source .venv/bin/activate
python telegram_bot/main.py
```

### Comandos del bot

| Comando / Acción | Descripción |
|---|---|
| `/start` | Mensaje de bienvenida |
| Enviar cualquier texto | Analiza el texto con el orquestador y devuelve el reporte |

> **Nota:** El bot de WhatsApp (`whatsapp_bot/bot.py`) se encuentra actualmente en desarrollo y no está operativo.

---

## Contribuciones

Este proyecto está en desarrollo activo. Si deseas contribuir, por favor:

1. Abre un issue describiendo el cambio propuesto.
2. Crea una rama desde `main`.
3. Realiza tus cambios y asegúrate de que las pruebas pasen.
4. Abre un Pull Request con una descripción clara.

---

*CyberGuardian — Desarrollado con el objetivo de hacer la ciberseguridad accesible para todos.*
