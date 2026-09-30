import os
import time
from google import genai
from google.genai import types

def generate_post_content():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: No se encontró la GEMINI_API_KEY.")
        return None, None

    client = genai.Client(api_key=api_key)

    prompt = """
    Eres el director de marketing de 'FrigZone', una empresa de refrigeración y climatización en Argentina.
    Genera contenido para una publicación en redes sociales sobre consejos de mantenimiento, ahorro de energía, service de aires acondicionados o buenas prácticas técnicas.
    
    Devuelve la respuesta estrictamente separada por '---':
    [TEXTO_PUBLICACION]
    (Redacta un consejo técnico útil y amigable para clientes, con un toque profesional y hashtags al final).
    ---
    [PROMPT_IMAGEN]
    (Describe detalladamente en inglés una imagen limpia, moderna, fotorrealista y profesional relacionada con el consejo, ideal para Instagram/Facebook en formato cuadrado).
    """

    max_retries = 3
    response = None

    for attempt in range(1, max_retries + 1):
        try:
            print(f"Generando contenido con Gemini (Intento {attempt}/{max_retries})...")
            response = client.models.generate_content(
                model='gemini-3.5-flash',
                contents=prompt,
            )
            if response and response.text:
                print("¡Contenido generado exitosamente con Gemini!")
                break
        except Exception as e:
            print(f"Aviso en intento {attempt}: {e}")
            if attempt < max_retries:
                print("Esperando 20 segundos para reintentar texto...")
                time.sleep(20)

    if not response or not response.text:
        print("Error crítico: No se pudo obtener respuesta de Gemini.")
        return None, None

    try:
        content = response.text
        parts = content.split("---")
        
        if len(parts) >= 2:
            post_text = parts[0].replace("[TEXTO_PUBLICACION]", "").strip()
            image_prompt = parts[1].replace("[PROMPT_IMAGEN]", "").strip()
            return post_text, image_prompt
        else:
            return content.strip(), "A modern professional HVAC and refrigeration technician working cleanly with tools."
            
    except Exception as e:
        print(f"Error procesando la respuesta de la IA: {e}")
        return None, None

def generate_ai_image(image_prompt, output_filename="post_ia.jpg"):
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    print(f"Iniciando renderizado de imagen con IA (esto puede tomar varios segundos)...")
    
    # Damos hasta 2 intentos con un tiempo de espera prudente
    max_image_retries = 2
    for attempt in range(1, max_image_retries + 1):
        try:
            print(f"Enviando solicitud de imagen al servidor (Intento {attempt}/{max_image_retries})...")
            
            # Usamos el modelo oficial compatible con la API de imágenes
            response = client.models.generate_content(
                model='gemini-2.5-flash-image',
                contents=f"Create a clean, professional, photorealistic 1:1 square image for this marketing post: {image_prompt}",
                config=types.GenerateContentConfig(
                    response_modalities=["TEXT", "IMAGE"],
                ),
            )
            
            # Verificamos si el servidor devolvió los datos binarios de la imagen
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if part.inline_data is not None:
                        image_data = part.inline_data.data
                        with open(output_filename, "wb") as f:
                            f.write(image_data)
                        print(f"¡Imagen generada y guardada exitosamente como {output_filename}!")
                        return output_filename
                        
            print(f"El servidor respondió pero no entregó datos binarios de imagen en el intento {attempt}.")
            
        except Exception as e:
            print(f"Aviso en renderizado de imagen (Intento {attempt}): {e}")
            
        if attempt < max_image_retries:
            print("El servidor está procesando los gráficos. Esperando 30 segundos antes del reintento...")
            time.sleep(30)
                
    print("No se pudo completar la generación de la imagen tras las esperas prolongadas.")
    return None
