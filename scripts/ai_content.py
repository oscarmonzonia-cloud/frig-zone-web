import os
from google import genai

def generate_post_copy():
    # Lee la API Key de Gemini desde las variables de entorno de forma segura
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        raise ValueError("No se encontró la GEMINI_API_KEY en las variables de entorno.")
    
    # Inicializa el cliente oficial de Google GenAI
    client = genai.Client(api_key=api_key)
    
    prompt = """
    Eres el experto en marketing y redes sociales de 'FrigZone', una marca especializada en refrigeración, aires acondicionados y climatización.
    Genera un post corto, profesional y atractivo para Facebook e Instagram que incluya:
    1. Un gancho inicial llamativo (pregunta o dato curioso sobre refrigeración).
    2. Un consejo técnico útil para el mantenimiento de equipos.
    3. Una llamada a la acción clara para que contacten a FrigZone.
    4. 5 hashtags relevantes y populares.
    
    Devuelve únicamente el texto listo para ser publicado.
    """
    
    try:
        # Usamos el modelo rápido y eficiente de la capa gratuita
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        print("¡Contenido generado exitosamente con Gemini AI!")
        return response.text
        
    except Exception as e:
        print(f"Error al generar contenido con Gemini: {e}")
        return None