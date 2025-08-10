# Archivo: app.py (Versión Híbrida de Alta Calidad)

import os
import json
import google.generativeai as genai
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app) 

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("No se encontró la GOOGLE_API_KEY en el archivo .env")

genai.configure(api_key=api_key)

@app.route('/')
def index():
    return render_template('index.html')

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
        prompt_completo = crear_prompt(objetivo, nivel)
        # Aumentamos el tiempo de espera, ya que la petición es más compleja
        response = model.generate_content(prompt_completo, request_options={"timeout": 120})
        
        respuesta_texto = response.text.strip()
        if respuesta_texto.startswith('```json'):
            respuesta_texto = respuesta_texto[7:]
        if respuesta_texto.endswith('```'):
            respuesta_texto = respuesta_texto[:-3]
        
        respuesta_json = json.loads(respuesta_texto)

        if "core_topic" not in respuesta_json or "specializations" not in respuesta_json:
            raise ValueError("La IA devolvió una estructura de datos inesperada.")

        return jsonify(respuesta_json)

    except json.JSONDecodeError:
        print(f"Error JSONDecode: La IA no devolvió un JSON válido. Respuesta: {response.text}")
        return jsonify({"error": "Error al procesar la respuesta de la IA."}), 500
    except Exception as e:
        print(f"Error inesperado: {e}")
        return jsonify({"error": f"Ocurrió un error en el servidor."}), 500

# --- PROMPT DE ESTRATEGIA HÍBRIDA ---
def crear_prompt(objetivo_usuario, nivel_conocimiento):
    return f"""
    Eres un 'Estratega Educativo de Élite'. Tu misión es crear una ruta de aprendizaje integral, detallada y accionable en formato JSON. La calidad y utilidad de los recursos es la máxima prioridad.

    Objetivo del usuario: '{objetivo_usuario}'
    Nivel de conocimiento: '{nivel_conocimiento}'

    **INSTRUCCIONES DE GENERACIÓN:**
    1.  **Longitud y Detalle:** Genera una ruta completa con 3 a 5 fases. Cada fase debe contener entre 4 y 7 pasos detallados.
    2.  **Descripciones Ricas:** Para cada paso, la 'descripcion' debe ser una explicación clara y útil del concepto, su importancia y qué debe aprender el usuario.

    **ESTRUCTURA DE RECURSOS HÍBRIDA (OBLIGATORIA):**
    Para cada paso, debes generar un objeto 'recursos' que contiene UN 'recurso_principal' y DOS 'alternativas'.

    -   **'recurso_principal'**: Este debe ser el **MEJOR ENLACE DIRECTO POSIBLE**.
        -   **Reglas:** Debe ser una URL real, funcional, sin muros de pago y sin necesidad de registro.
        -   **Prioridad:** 1. Documentación Oficial. 2. Tutoriales de sitios de élite (freeCodeCamp, Real Python, MDN, etc.). 3. Un video tutorial específico y completo de YouTube.
        -   **Formato:** Un objeto con 'titulo' (el título del recurso) y 'url' (el enlace directo).

    -   **'alternativas'**: Esta debe ser una lista de DOS búsquedas de respaldo.
        -   **Reglas:** Cada alternativa es un objeto con 'plataforma' ("YouTube" o "Google") y una 'query' de búsqueda optimizada. La query debe ser específica para encontrar contenido similar al recurso principal.
        -   **Propósito:** Actuar como una red de seguridad si el enlace principal está roto.

    **EJEMPLO DE FORMATO JSON EXACTO (NO TE DESVÍES):**
    ```json
    {{
      "titulo_ruta": "Ruta de Aprendizaje Avanzada para: {objetivo_usuario} (Nivel: {nivel_conocimiento})",
      "core_topic": {{
        "nombre_fase": "Fase 1: Fundamentos Indispensables",
        "pasos": [
          {{
            "titulo": "Entender el Event Loop en JavaScript",
            "descripcion": "Comprender cómo JavaScript maneja operaciones asíncronas de manera no bloqueante. Es clave para entender el rendimiento de Node.js y las aplicaciones de frontend.",
            "recursos": {{
              "recurso_principal": {{
                "titulo": "Video Explicativo Visual del Event Loop",
                "url": "https://www.youtube.com/watch?v=8aGhZQkoFbQ"
              }},
              "alternativas": [
                {{
                  "plataforma": "Google",
                  "query": "javascript event loop explained for beginners"
                }},
                {{
                  "plataforma": "YouTube",
                  "query": "visual explanation of javascript event loop"
                }}
              ]
            }}
          }}
        ]
      }},
      "specializations": []
    }}
    ```
    Genera el JSON completo basado en estas reglas.
    """

if __name__ == '__main__':
    app.run(debug=True, port=5000)