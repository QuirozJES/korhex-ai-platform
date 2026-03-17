# KORHEX.AI 🤖

## Descripción del Proyecto

**KORHEX.AI** es una plataforma de **Enterprise Account Intelligence** diseñada con un enfoque estricto en **Zero Data Leakage**. Esta herramienta permite realizar análisis profundos de cuentas B2B operando de manera orientada a la privacidad, garantizando que la información sensible y estratégica esté siempre bajo control.

## Arquitectura Técnica

El sistema está construido sobre una arquitectura moderna, segura y localizada que integra tres componentes principales:

1. **Frontend en Streamlit**: Proporciona una interfaz de usuario interactiva, rápida y fluida para la captura de datos (URL, Nombre de la Empresa, Industria, años de inactividad) y la visualización de los resultados, "Net New Scores" y métricas de inteligencia.
2. **Orquestación Multi-Agente con CrewAI**: Emplea una arquitectura basada en agentes especializados interagiendo entre sí (como el `Account Executive Agent`, `Compliance Agent`, y un `Auditor Agent`). Estos agentes trabajan en sincronía para recolectar señales web, validar la calidad e integridad de los datos, identificar sesgos/alucinaciones y generar un discurso de ventas estratégico y personalizado.
3. **Ejecución Local con Llama 3 a través de Ollama**: El núcleo de procesamiento NLP opera de forma local utilizando **Llama 3** a través de **Ollama**. Esto asegura la privacidad bajo la premisa "Zero Data Leakage", procesando los análisis semánticos para hacer el _match_ con el portafolio de la empresa, todo en local sin depender de APIs LLM externas para el razonamiento.

Adicionalmente, la plataforma aprovecha la **API de Tavily** para la extracción de inteligencia y búsquedas web, e implementa una **base de datos SQLite** a nivel local para manejo en memoria y optimización de cachés, logrando despliegues de información casi inmediatos tras la primera consulta.

## Prerrequisitos

Para ejecutar KORHEX.AI, asegúrate de cumplir con los siguientes requerimientos en tu sistema:

- **Python 3.12** o superior.
- **Ollama** instalado y ejecutándose de forma local.
- **Modelo Llama 3** descargado en tu instancia local de Ollama (puedes descargarlo usando `ollama run llama3`).

## Guía de Instalación

Sigue estos pasos paso a paso para configurar y levantar el proyecto en tu máquina local:

1. **Clonar el repositorio**

   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd korhex-ai-platform
   ```

2. **Crear el entorno virtual (venv)**

   ```bash
   python -m venv venv
   ```

3. **Activar el entorno virtual**
   - En **Windows**:
     ```powershell
     .\venv\Scripts\activate
     ```
   - En **macOS/Linux**:
     ```bash
     source venv/bin/activate
     ```

4. **Instalar dependencias**
   Con el entorno virtual ya activo, instala los requerimientos oficiales del proyecto:
   ```bash
   pip install -r requirements.txt
   ```

## Configuración de Entorno

El sistema requiere de ciertas variables de entorno para funcionar correctamente con servicios de apoyo (como el raspado inteligente web y base de datos extendida).

Debes crear un archivo llamado `.env` en la raíz del proyecto y añadir las siguientes llaves:

```env
# Claves de acceso requeridas
TAVILY_API_KEY=tu_api_key_de_tavily
```

_(Nota: Tavily se utiliza para buscar la información pública de las cuentas objetivo, y Supabase actúa como infraestructura en la nube según las necesidades de tu base de datos)._

## Ejecución

Una vez cumplidos los pasos de instalación y configuración de variables, y teniendo **Ollama** previamente arrancado en segundo plano, levanta la interfaz gráfica ejecutando el siguiente comando exacto:

```bash
streamlit run Home.py
```

El portal de KORHEX.AI se abrirá automáticamente en tu navegador web por defecto. ¡Listo para analizar!
