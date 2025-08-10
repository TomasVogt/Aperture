# Archivo: app.py (Corregido para servir archivos estáticos)

import os
import json
import google.generativeai as genai
# --- IMPORTANTE: Añade send_from_directory ---
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# --- Configuración Inicial ---
app = Flask(__name__)
CORS(app) 

# --- Carga de la Clave de API desde el archivo .env ---
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("No se encontró la GOOGLE_API_KEY en el archivo .env")

genai.configure(api_key=api_key)

# --- NUEVA RUTA: Para servir el index.html ---
@app.route('/')
def serve_index():
    # Busca 'index.html' dentro de la carpeta 'static' y lo devuelve
    return send_from_directory('static', 'index.html')

# --- El Prompt Maestro (sin cambios) ---
def crear_prompt(objetivo_usuario, nivel_conocimiento):
    return f"""
    Eres un 'Creador de Rutas de Aprendizaje Experto'. Tu misión es generar un plan de estudios detallado y personalizado.
    
    El objetivo del usuario es: '{objetivo_usuario}'
    
    IMPORTANTE: El nivel de conocimiento previo del usuario es '{nivel_conocimiento}'. Debes adaptar la ruta a este nivel:
    - Si es 'Principiante', empieza con los conceptos más fundamentales y básicos, asumiendo cero conocimiento previo.
    - Si es 'Intermedio', puedes omitir los fundamentos más obvios y empezar con temas más prácticos y de nivel medio.
    - Si es 'Avanzado', enfócate en temas complejos, especialización, mejores prácticas y herramientas de nivel profesional. Omite por completo los temas básicos e intermedios.

    Tu respuesta DEBE seguir estrictamente el siguiente formato JSON. No incluyas texto antes o después del JSON:
    {{
      "titulo_ruta": "Ruta de Aprendizaje para: {objetivo_usuario} (Nivel: {nivel_conocimiento})",
      "fases": [
        {{
          "nombre_fase": "Nombre de la Fase 1 (ej: Fundamentos Indispensables)",
          "pasos": [
            {{
              "titulo": "Título específico de la habilidad a aprender",
              "descripcion": "Una descripción corta y clara de lo que el usuario debe aprender en este paso, adaptada a su nivel.",
              "recurso_util": "https://ejemplo.com/recurso-util-y-valido"
            }}
          ]
        }}
      ]
    }}
    Asegúrate de que cada 'recurso_util' sea una URL real y de alta calidad. Genera entre 2 y 4 fases, cada una con varios pasos lógicos y relevantes para el nivel del usuario.
    """

# --- La Ruta de la API (sin cambios) ---
@app.route('/generate-path', methods=['POST'])
def generar_ruta():
    try:
        data = request.get_json()
        objetivo = data.get('goal')
        nivel = data.get('level')

        if not objetivo or not nivel:
            return jsonify({"error": "Tanto el objetivo ('goal') como el nivel ('level') son requeridos."}), 400

        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        
        prompt_completo = crear_prompt(objetivo, nivel)
        response = model.generate_content(prompt_completo)
        
        respuesta_texto = response.text.strip()
        if respuesta_texto.startswith('```json'):
            respuesta_texto = respuesta_texto[7:]
        if respuesta_texto.endswith('```'):
            respuesta_texto = respuesta_texto[:-3]
        
        respuesta_json = json.loads(respuesta_texto)

        return jsonify(respuesta_json)

    except json.JSONDecodeError:
        print(f"Error: La IA no devolvió un JSON válido. Respuesta recibida: {response.text}")
        return jsonify({"error": "Error al procesar la respuesta de la IA. Inténtalo de nuevo."}), 500
    except Exception as e:
        print(f"Error inesperado: {e}")
        return jsonify({"error": f"Ocurrió un error en el servidor: {str(e)}"}), 500

# --- Iniciar el servidor ---
if __name__ == '__main__':
    app.run(debug=True, port=5000)