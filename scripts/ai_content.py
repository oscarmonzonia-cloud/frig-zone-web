import os
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

    # Lista de modelos a probar en orden de prioridad (Fallback automático)
    models_to_try = ['gemini-3.8-flash', 'gemini-1.5-flash']
    
    response = None
    for model_name in models_to_try:
        try:
            print(f"Intentando generar contenido con el modelo: {model_name}...")
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            if response and response.text:
                break # Si tiene éxito, salimos del bucle
        except Exception as e:
            print(f"Aviso: El modelo {model_name} falló o está saturado: {e}. Probando siguiente opción...")

    if not response or not response.text:
        print("Error crítico: Todos los modelos de Gemini fallaron.")
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
    
    print(f"Generando imagen con IA usando el prompt: {image_prompt}")
    try:
        result = client.models.generate_images(
            model='imagen-3.0-generate-002',
            prompt=image_prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                output_mime_type="image/jpeg",
                aspect_ratio="1:1",
            )
        )
        
        for generated_image in result.generated_images:
            image = generated_image.image.image_bytes
            with open(output_filename, "wb") as f:
                f.write(image)
        
        print(f"Imagen generada localmente como {output_filename}")
        return output_filename
    except Exception as e:
        print(f"Error al generar la imagen con IA: {e}")
        return None
