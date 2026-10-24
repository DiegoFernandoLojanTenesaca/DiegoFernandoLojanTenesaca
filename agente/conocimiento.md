# Base de conocimiento del agente del perfil

Cada sección `##` es un documento que el agente puede recuperar. Solo hechos verificables.

## perfil
Diego Fernando Lojan Tenesaca es Ingeniero en Ciencias de la Computación por la Universidad Nacional de Loja (UNL), de Ecuador. Trabaja como Data & AI Engineer y desarrollador full stack. Tiene cuatro años desarrollando software, los dos últimos de forma profesional, y dos enfocados en machine learning, ciencia de datos y procesamiento del lenguaje natural. Su trabajo es llevar modelos de IA a producción y mantenerlos ahí: LLMs, RAG, agentes, búsqueda semántica y pipelines de datos, junto con las aplicaciones web, de escritorio y móviles que los usan.

## trabajo-actual
Desde octubre de 2026 es Ingeniero de IA Aplicada en Inti Horizons IA, en remoto desde Ecuador. Los detalles de ese trabajo (clientes, sistemas, código, cifras) son confidenciales y no se comparten. Además mantiene sus productos propios en Indaga Lab y es cofundador de Xynitra Devs.

## experiencia/dataglov
De febrero a agosto de 2026 fue Ingeniero de Software Junior (Data & AI) en Dataglov S.A.S., en Loja. Trabajó en el microservicio de IA en producción de Sudial AI: arquitectura DDD con multi-tenencia aislada por esquemas en PostgreSQL, 18 dominios funcionales sobre una API REST única; búsqueda semántica sobre 139.000 conversaciones con embeddings BGE-M3 de 1.024 dimensiones e índice HNSW en pgvector; re-embebido de 62.000 conversaciones en menos de una hora en una GPU NVIDIA A6000 con Text Embeddings Inference; un benchmark propio de motores vectoriales (latencia, recall y memoria) sobre los 139.000 vectores reales para elegir el motor de producción con datos y no por moda; un agente conversacional con 15 herramientas de tool calling, control de bucles, caché normalizado y enmascaramiento de PII con LangChain y LangGraph; modelos de visión y lenguaje self-hosted (Qwen-VL, InternVL), clasificación zero-shot, OCR y transcripción local; migraciones reversibles con checksums, observabilidad de tokens y latencia, rate limiting por tenant y CI/CD.

## experiencia/serviestudios
De octubre de 2025 a febrero de 2026 fue Desarrollador Full Stack en Serviestudios Cía. Ltda., en Loja: backoffice web en Next.js y app móvil en React Native con tema dinámico e internacionalización; API REST en Python por dominios con JWT, OAuth y roles; PostgreSQL, WebSockets y Redis; integraciones con WhatsApp Business API, Google Calendar, pasarelas de pago y OTP; constructor visual de flujos conversacionales y OCR de documentos.

## experiencia/indaga-lab
Desde 2025 es fundador y desarrollador principal de Indaga Lab, su marca de productos de software e IA (indagalab.com). Ahí están Wauto Indaga, Kumbre, AgentOS, Cuadrekit, Xyra y Ordo. Lleva la dirección técnica, la definición de producto y el modelo de precios.

## experiencia/xynitra-devs
Desde julio de 2026 es cofundador de Xynitra Devs, un estudio de desarrollo de software en Quito. Construyó una plataforma de códigos OTP para cuentas de streaming con Cloudflare Email Workers, extracción de códigos en tiempo real, Upstash Redis, CAPTCHA y panel de administración, en Next.js 16 y FastAPI.

## experiencia/freelance
Desde 2024 trabaja como freelance en software e IA: bots conversacionales para Telegram y WhatsApp con orquestación de LLMs, failover entre proveedores, prompts versionados y validación estricta de salida; un CRM para una consultora de asesoría energética; detección de anomalías en series temporales, web scraping y automatizaciones con n8n; y apoyo computacional a tesis de posgrado, como la simulación numérica de aisladores sísmicos en Python y MATLAB validados entre sí.

## proyectos/wauto
Wauto Indaga es un CRM y automatización de mensajería con IA para WhatsApp, Telegram y Meta, en producción con cinco planes comerciales y respuesta del agente en menos de 2 segundos. Su agente responde con RAG sobre una base de conocimiento con recuperación híbrida (full-text + pgvector), y usa una cascada de modelos con failover entre proveedores, API pública versionada y servidor MCP. Next.js 16, React 19 y Supabase. Web: wauto.indagalab.com.

## proyectos/riksi
Riksi reconoce 100 especies de fauna y flora del Ecuador dentro del navegador y sin conexión, con un modelo EfficientNet-Lite0 cuantizado a 8 bits de 3,8 MB en ONNX Runtime. Lo completan Yachaq, un agente de siete herramientas con RAG y cascada de proveedores que funciona en 512 MB de RAM, y riksi-radar, un pipeline Kafka, DuckDB y dbt que contrasta el modelo con las etiquetas de GBIF y confirma que aguanta fuera de su distribución.

## proyectos/xyra
Xyra es un companion de escritorio y Android para League of Legends, creado por Diego con Xynitra Devs. Se conecta al cliente local por WebSocket, lee las cartas de aumento con OCR, empareja el celular por QR y se actualiza solo verificando cada versión con SHA-256. Las versiones se publican por etiqueta con CI. Está en revisión en el portal de desarrolladores de Riot Games. Rust, Tauri 2, Svelte 5 y Kotlin. Web: xyra-app.pages.dev.

## proyectos/ordo
Ordo es una app de escritorio que ordena Gmail con IA: propone una etiqueta por remitente y la convierte en filtros de Gmail, que siguen funcionando con la computadora apagada. Funciona con Claude, Groq, Ollama en local o cualquier API compatible con OpenAI. La IA solo propone: su salida se valida y el usuario aprueba cada cambio. Rust, Tauri y Svelte.

## proyectos/agentos
AgentOS es una app Android open source que convierte teléfonos sin servicios de Google en un agente de IA 24/7 que se maneja por Telegram, con Python embebido y modelo local opcional.

## proyectos/cuadrekit-kumbre
Cuadrekit es un kit gratuito para micronegocios del Ecuador (liquidación laboral, proformas, recibos y nómina) que funciona sin conexión y sin suscripción, hecho en Vue. Kumbre convierte presupuestos PDF en formato SERCOP a Excel editable con parsing inteligente y fuzzy matching.

## proyectos/cconnect
En CConnect, un cliente móvil, de escritorio y web para manejar Claude Code en otro equipo (repo de jahirxtrap), Diego es contribuidor: aportó al backend FastAPI sobre el Agent SDK y a la app, primero en Compose Multiplatform y luego en su migración a Svelte y Tauri.

## proyectos/anomalias
Anomalías Energéticas LATAM detecta crisis energéticas en 8 países por consenso de tres técnicas (Isolation Forest, STL y CUSUM), comparadas con nueve modelos base y validadas con bootstrap y prueba de McNemar. Logra un F1 de 0,75. scikit-learn, Optuna, SHAP y Streamlit.

## publicacion
Artículo aceptado en Springer Nature: Lojan, D. F. y Chamba-Eras, L., "Bayesian Hyperparameter Optimization of Support Vector Machines Using TPE for Stress Detection in Spanish Social Media During the 2024 Ecuadorian Energy Crisis", en Emerging Research in Intelligent Systems, actas del CIT 2026, serie Lecture Notes in Networks and Systems. Se presentó en el XXI CIT 2026 en la Universidad de las Fuerzas Armadas ESPE en junio de 2026 y está en producción. Usa un SVM optimizado con Optuna (TPE) bajo CRISP-DM.

## stack
IA y ML: LangChain, LangGraph, RAG y recuperación híbrida, agentes con tool calling, MCP, embeddings y búsqueda vectorial, NLP, clasificación zero-shot, detección de anomalías, OCR, speech-to-text, modelos de visión y lenguaje, ONNX Runtime, cuantización int8. Datos: SQL, ETL, Kafka, DuckDB, dbt, MLflow, series temporales, web scraping, Pandas, NumPy, SciPy. Backend: Python (FastAPI, Pyramid, Django), Rust, Node.js, Java (Spring Boot), PostgreSQL con pgvector, Redis, Supabase. Frontend y móvil: React, Next.js, TypeScript, Svelte, Tailwind, Astro, Vue, Kotlin, Jetpack Compose, React Native, Tauri. DevOps: Docker, CI/CD, GitHub Actions, Linux, Nginx, Cloudflare, n8n, Claude Code.

## formacion
Ingeniero en Ciencias de la Computación por la Universidad Nacional de Loja. Estudios internacionales en Ingeniería de Sistemas e Informática (un ciclo) en la Universidad Tecnológica del Perú, en Lima. Diplomado en Aprendizaje Basado en Proyectos (120 h) del Politécnico de Colombia. Quinta Escuela de Cómputo Cuántico (28 h) de la UNAM, Facultad de Ingeniería, en agosto de 2026. Cursos de Cisco Networking Academy en ciberseguridad (2025) e IPv6 de Sage (2023). Certificados de LinkedIn Learning y Microsoft en ciencia de datos, Big Data, PySpark, NLTK, agentes de IA, Microsoft Fabric y análisis de datos.

## idiomas
Español nativo e inglés intermedio (B1), con lectura técnica y documentación con fluidez.

## contacto
Correo: fernando.lojan10@gmail.com. LinkedIn: linkedin.com/in/diego-fernando-lojan. Portafolio: diegofernandolojantenesaca.github.io. GitHub: github.com/DiegoFernandoLojanTenesaca. ORCID: 0009-0003-3882-3889. Para propuestas de trabajo, colaboración o docencia, lo mejor es escribirle al correo.

## este-agente
Este agente es una GitHub Action del repositorio del perfil. Cuando alguien abre un Issue con una pregunta, recupera las secciones más relevantes de esta base de conocimiento con BM25 y le pide la respuesta a un LLM en Groq (gpt-oss-120b, con qwen3.8-27b de respaldo si falla). Solo responde con lo que está aquí; si algo no está, lo dice.
