# Archivo: app.py

import os
import json
import google.generativeai as genai
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv

# Flask buscará las carpetas 'templates' y 'static' automáticamente
app = Flask(__name__)
CORS(app) 

# Cargar variables de entorno desde el archivo .env
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("No se encontró la GOOGLE_API_KEY en el archivo .env")

genai.configure(api_key=api_key)

# RUTA 1: Servir la página web principal desde la carpeta 'templates'
@app.route('/')
def index():
    return render_template('index.html')

# RUTA 2: La API que genera la ruta de aprendizaje
@app.route('/generate-path', methods=['POST'])
def generar_ruta():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Petición inválida."}), 400

        objetivo = data.get('goal')
        nivel = data.get('level')

        if not objetivo or not nivel:
            return jsonify({"error": "El objetivo y el nivel son requeridos."}), 400

        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        prompt_completo = crear_prompt_definitivo(objetivo, nivel)
        # Aumentamos el tiempo de espera, ya que la petición es más compleja
        response = model.generate_content(prompt_completo, request_options={"timeout": 120})
        
        respuesta_texto = response.text.strip()
        if respuesta_texto.startswith('```json'):
            respuesta_texto = respuesta_texto[7:]
        if respuesta_texto.endswith('```'):
            respuesta_texto = respuesta_texto[:-3]
        
        respuesta_json = json.loads(respuesta_texto)

        if "titulo_ruta" not in respuesta_json or "fases" not in respuesta_json:
            raise ValueError("La IA devolvió una estructura de datos inesperada.")

        return jsonify(respuesta_json)

    except json.JSONDecodeError:
        print(f"Error de Decodificación JSON. La IA no devolvió un JSON válido. Respuesta recibida:\n{response.text}")
        return jsonify({"error": "Hubo un error al procesar la respuesta de la IA. Inténtalo de nuevo."}), 500
    except Exception as e:
        print(f"Error Inesperado: {e}")
        return jsonify({"error": f"Ocurrió un error inesperado en el servidor: {str(e)}"}), 500

def crear_prompt_definitivo(objetivo_usuario, nivel_conocimiento):
    """
    Este prompt está diseñado para ser extremadamente estricto y producir rutas largas,
    detalladas y con recursos híbridos de alta calidad.
    """
    return f"""
    Eres un 'Arquitecto de Currículos Digitales de Élite'. Tu única misión es construir la ruta de aprendizaje más completa, detallada y útil posible, en formato JSON. La calidad y fiabilidad de los recursos es la máxima prioridad.

    Objetivo del Usuario: '{objetivo_usuario}'
    Nivel de Conocimiento: '{nivel_conocimiento}'

    **REGLAS DE GENERACIÓN (OBLIGATORIAS):**

    1.  **Profundidad y Detalle:** La ruta debe ser extensa. Genera entre 3 y 5 'fases'. Cada 'fase' debe contener entre 4 y 7 'pasos'. Las descripciones de cada paso deben ser ricas, explicando el 'qué' y el 'porqué' del concepto.
    
    2.  **Estructura de Recursos HÍBRIDA (La Regla Más Importante):**
        Por cada 'paso', debes generar un objeto 'recursos' que contiene UN 'recurso_principal' Y un array de 'alternativas'.

        -   **`recurso_principal` (El Enlace de Oro):**
            -   **Propósito:** Debe ser el MEJOR ENLACE DIRECTO, ÚTIL Y FUNCIONAL en toda la web para ese concepto.
            -   **Prioridad Absoluta:** 1º Documentación Oficial (ej: python.org, developer.mozilla.org), 2º Tutoriales de sitios de élite (ej: freeCodeCamp, Real Python, CSS-Tricks), 3º Un video específico y completo de un canal educativo de renombre en YouTube.
            -   **RESTRICCIONES:** NO PUEDE ser un enlace a una página de venta (Udemy, Coursera), un foro (Stack Overflow), o requerir registro. Debe ser de acceso 100% gratuito e inmediato.
            -   **Formato:** Un objeto con `titulo` (el título real del recurso) y `url`.

        -   **`alternativas` (La Red de Seguridad):**
            -   **Propósito:** Dos búsquedas de respaldo por si el enlace principal falla.
            -   **Formato:** Un array de DOS objetos. Cada objeto debe tener `plataforma` ("YouTube" o "Google") y una `query` de búsqueda perfectamente optimizada para encontrar contenido similar.

    **FORMATO JSON EXACTO (NO TE DESVÍES NI UN CARÁCTER):**

    ```json
    {{
      "titulo_ruta": "Ruta de Aprendizaje Definitiva para: {objetivo_usuario} (Nivel: {nivel_conocimiento})",
      "fases": [
        {{
          "nombre_fase": "Fase 1: Cimientos Sólidos",
          "pasos": [
            {{
              "titulo": "Entender el Modelo de Caja en CSS",
              "descripcion": "Es el concepto más fundamental del layout en la web. Aprenderás cómo el padding, borde, margen y contenido interactúan para definir el tamaño y espaciado de un elemento.",
              "recursos": {{
                "recurso_principal": {{
                  "titulo": "Guía Completa sobre el Modelo de Caja - MDN",
                  "url": "https://developer.mozilla.org/es/docs/Learn/CSS/Building_blocks/The_box_model"
                }},
                "alternativas": [
                  {{ "plataforma": "YouTube", "query": "css box model tutorial español explicación visual" }},
                  {{ "plataforma": "Google", "query": "guía completa modelo de caja css" }}
                ]
              }}
            }}
          ]
        }}
      ]
    }}
    ```
    Tu única salida debe ser el código JSON. Nada antes, nada después.
    """

if __name__ == '__main__':
    app.run(debug=True, port=5000)