# Archivo: app.py (Corregido)

import os
import json
import google.generativeai as genai
from flask import Flask, request, jsonify
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

# --- El Prompt Maestro (sin cambios) ---
def crear_prompt(objetivo_usuario):
    return f"""
    Eres un 'Creador de Rutas de Aprendizaje Experto'. Tu misión es generar un plan de estudios detallado y personalizado basado en el objetivo que te proporcionará el usuario.
    El objetivo del usuario es: '{objetivo_usuario}'
    Tu respuesta DEBE seguir estrictamente el siguiente formato JSON. No incluyas texto antes o después del JSON:
    {{
      "titulo_ruta": "Ruta de Aprendizaje para: {objetivo_usuario}",
      "fases": [
        {{
          "nombre_fase": "Nombre de la Fase 1 (ej: Fundamentos)",
          "pasos": [
            {{
              "titulo": "Título específico de la habilidad a aprender",
              "descripcion": "Una descripción corta y clara de lo que el usuario debe aprender en este paso.",
              "recurso_util": "https://ejemplo.com/recurso-util-y-valido"
            }}
          ]
        }}
      ]
    }}
    Asegúrate de que cada 'recurso_util' sea una URL real y de alta calidad. Genera entre 2 y 4 fases, cada una con varios pasos lógicos.
    """

# --- La Ruta de la API (Endpoint) ---
@app.route('/generate-path', methods=['POST'])
def generar_ruta():
    try:
        data = request.get_json()
        objetivo = data.get('goal')

        if not objetivo:
            return jsonify({"error": "El objetivo ('goal') es requerido."}), 400

        # --- CORRECCIÓN AQUÍ: Se cambió el nombre del modelo ---
        model = genai.GenerativeModel('gemini-1.5-flash-latest') 
        
        prompt_completo = crear_prompt(objetivo)
        response = model.generate_content(prompt_completo)
        
        # Limpieza robusta de la respuesta de la IA
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
        # Devuelve el error específico de la API si está disponible, para un mejor diagnóstico.
        return jsonify({"error": f"Ocurrió un error en el servidor: {str(e)}"}), 500

# --- Iniciar el servidor ---
if __name__ == '__main__':
    app.run(debug=True, port=5000)