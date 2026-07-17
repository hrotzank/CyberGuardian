# CyberGuardian v1.0

## Descripción General

CyberGuardian es una plataforma inteligente de concientización y detección de phishing orientada a ciudadanos, instituciones educativas y organismos públicos.

El sistema utiliza una arquitectura multiagente basada en Inteligencia Artificial para analizar mensajes sospechosos recibidos por diferentes canales de comunicación y determinar si representan una amenaza de phishing, fraude o ingeniería social.

---

## Objetivo General

Desarrollar una plataforma multiagente capaz de identificar intentos de phishing y educar al usuario sobre los riesgos detectados mediante explicaciones comprensibles y recomendaciones de seguridad.

---

## Canales de Entrada

* Aplicación Web
* Telegram Bot
* WhatsApp Bot

---

## Entradas del Sistema

### Texto

Ejemplo:

"Su cuenta será suspendida. Ingrese al siguiente enlace para verificar sus datos."

### URL

Ejemplo:

https://dominio-sospechoso.xyz

---

## Arquitectura Multiagente

### URL Agent

Responsabilidades:

* Analizar URLs.
* Detectar dominios sospechosos.
* Detectar enlaces acortados.
* Verificar características básicas del dominio.

---

### Phishing Agent

Responsabilidades:

* Analizar lenguaje utilizado.
* Detectar urgencia artificial.
* Detectar amenazas.
* Detectar intentos de manipulación psicológica.

---

### Reputation Agent

Responsabilidades:

* Consultar reputación de dominios.
* Verificar listas negras.
* Validar indicadores de compromiso.

---

### Education Agent

Responsabilidades:

* Explicar riesgos al usuario.
* Generar recomendaciones.
* Promover buenas prácticas de ciberseguridad.

---

### Report Agent

Responsabilidades:

* Consolidar resultados.
* Calcular nivel de riesgo.
* Generar reporte final.

---

### Orchestrator Agent

Responsabilidades:

* Coordinar el flujo de trabajo.
* Gestionar la comunicación entre agentes.
* Unificar resultados.

---

## Tecnologías

### Backend

* Python
* FastAPI

### Orquestación Multiagente

* Antigravity

### Base de Datos

* PostgreSQL

### Frontend

* React

### Bots

* Telegram Bot API
* WhatsApp Business API

---

## Resultado Esperado

El sistema debe proporcionar un análisis comprensible para cualquier ciudadano indicando:

* Nivel de riesgo.
* Motivos de la clasificación.
* Recomendaciones de seguridad.
* Explicación educativa.
