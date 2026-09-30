import os
import time
from google import genai
from google.genai import types

def generate_post_content():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: No se encontró la GEMINI_API_KEY.")
        return None, None, None

    client = genai.Client(api_key=api_key)

    # Prompt mejorado para pedir también un diseño HTML estilizado de respaldo
    prompt = """
    Eres el director de marketing de 'FrigZone', una empresa de refrigeración y climatización en Argentina.
    Genera contenido para una publicación en redes sociales sobre consejos de mantenimiento, ahorro de energía o buenas prácticas técnicas.
    
    Devuelve la respuesta estrictamente separada por '---':
    [TEXTO_PUBLICACION]
    (Redacta un consejo técnico útil y amigable para clientes, con un toque profesional y hashtags al final).
    ---
    [PROMPT_IMAGEN]
    (Describe detalladamente en inglés una imagen limpia, moderna y profesional relacionada con el consejo, ideal para redes).
    ---
    [HTML_ESTILIZADO]
    (Genera un diseño HTML/CSS completo y minimalista, listo para embeber en un contenedor cuadrado de 1080x1080px, con los colores de FrigZone (fondos limpios, azul corporativo, tipografía moderna) que muestre visualmente este mismo consejo técnico en formato de placa o tarjeta publicitaria).
    """

    max_retries = 3
    response = None

    for attempt in range(1, max_retries + 1):
        try:
            print(f"Generando contenido y estructura con Gemini (Intento {attempt}/{max_retries})...")
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
                print("Esperando 20 segundos para reintentar...")
                time.sleep(20)

    if not response or not response.text:
        print("Error crítico: No se pudo obtener respuesta de Gemini.")
        return None, None, None

    try:
        content = response.text
        parts = content.split("---")
        
        post_text = "Consejo FrigZone"
        image_prompt = "A modern professional HVAC technician."
        html_content = "<div><h1>FrigZone</h1></div>"

        if len(parts) >= 1:
            post_text = parts[0].replace("[TEXTO_PUBLICACION]", "").strip()
        if len(parts) >= 2:
            image_prompt = parts[1].replace("[PROMPT_IMAGEN]", "").strip()
        if len(parts) >= 3:
            html_content = parts[2].replace("[HTML_ESTILIZADO]", "").strip()
            # Limpiamos bloques de código markdown si la IA los incluye por error
            html_content = html_content.replace("```html", "").replace("```", "").strip()

        return post_text, image_prompt, html_content
            
    except Exception as e:
        print(f"Error procesando la respuesta de la IA: {e}")
        return None, None, None

def generate_ai_image(image_prompt, output_filename="post_ia.jpg"):
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    print(f"Intentando generar imagen con IA (dando tiempo de procesamiento)...")
    
    try:
        # Damos un margen lógico de espera/petición al modelo de imagen
        response = client.models.generate_content(
            model='gemini-3.1-flash-image',
            contents=f"Create a clean, professional, photorealistic 1:1 square image for this marketing post: {image_prompt}",
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
            ),
        )
        
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    image_data = part.inline_data.data
                    with open(output_filename, "wb") as f:
                        f.write(image_data)
                    print(f"¡Imagen generada por IA exitosamente como {output_filename}!")
                    return True
                    
        print("El modelo de IA no devolvió datos de imagen.")
        return False
        
    except Exception as e:
        print(f"⚠️ La IA visual reportó límite de cuota o demora: {e}")
        return False

def save_html_fallback(html_content, output_filename="post_placa.html"):
    """Guarda el diseño HTML generado por la IA como respaldo visual"""
    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"Placa HTML de respaldo generada y guardada como {output_filename}")
        return output_filename
    except Exception as e:
        print(f"Error al guardar el HTML de respaldo: {e}")
        return None
