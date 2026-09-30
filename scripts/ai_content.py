import os
import time
from google import genai
from google.genai import types
from PIL import Image, ImageDraw, ImageFont

def generate_post_content():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: No se encontró la GEMINI_API_KEY.")
        return None, None, None

    client = genai.Client(api_key=api_key)

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
    [TITULO_PLACA]
    (Un título corto y llamativo de 3 a 5 palabras para la placa gráfica, ej: "¡Cuidado con el consumo!").
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
        placa_title = "FrigZone Climatización"

        if len(parts) >= 1:
            post_text = parts[0].replace("[TEXTO_PUBLICACION]", "").strip()
        if len(parts) >= 2:
            image_prompt = parts[1].replace("[PROMPT_IMAGEN]", "").strip()
        if len(parts) >= 3:
            placa_title = parts[2].replace("[TITULO_PLACA]", "").strip()

        return post_text, image_prompt, placa_title
            
    except Exception as e:
        print(f"Error procesando la respuesta de la IA: {e}")
        return None, None, None

def generate_ai_image(image_prompt, output_filename="post_ia.jpg"):
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    print(f"Intentando generar imagen oficial con IA...")
    
    try:
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
                    return output_filename
                    
        return None
        
    except Exception as e:
        print(f"⚠️ Aviso de cuota de IA visual: {e}")
        return None

def create_fallback_image(title_text, subtitle_text, output_filename="post_placa.jpg"):
    """Crea una placa gráfica profesional en formato JPG con los colores de FrigZone si la IA visual falla"""
    try:
        width, height = 1080, 1080
        # Fondo azul corporativo moderno estilo FrigZone
        image = Image.new("RGB", (width, height), color="#0A2540")
        draw = ImageDraw.Draw(image)
        
        # Intentamos cargar una fuente estándar, si no usa la predeterminada
        try:
            font_title = ImageFont.truetype("DejaVuSans-Bold.ttf", 60)
            font_sub = ImageFont.truetype("DejaVuSans.ttf", 36)
        except:
            font_title = ImageFont.load_default()
            font_sub = ImageFont.load_default()

        # Dibujar elementos gráficos decorativos (franja superior)
        draw.rectangle([(0, 0), (width, 40)], fill="#00D4B2") # Turquesa marca
        
        # Texto de marca
        draw.text((80, 100), "❄️ FRIGZONE CLIMATIZACIÓN", fill="#00D4B2", font=font_sub)
        
        # Título principal de la placa (limitado en líneas o espaciado)
        draw.text((80, 220), title_text[:40], fill="#FFFFFF", font=font_title)
        
        # Línea divisoria
        draw.line([(80, 320), (1000, 320)], fill="#3A506B", width=4)
        
        # Subtítulo o extracto del consejo
        # Dividimos el texto en líneas para que no se salga de la placa
        margin = 80
        y_text = 380
        for line in subtitle_text.split('\n'):
            draw.text((margin, y_text), line[:60], fill="#E2E8F0", font=font_sub)
            y_text += 50
            if y_text > 900:
                break

        # Pie de página
        draw.text((80, 980), "Servicio Técnico Profesional • Buenos Aires", fill="#94A3B8", font=font_sub)

        image.save(output_filename, "JPEG", quality=95)
        print(f"Placa gráfica de respaldo generada exitosamente como {output_filename}")
        return output_filename
    except Exception as e:
        print(f"Error al generar la imagen de respaldo: {e}")
        return None
