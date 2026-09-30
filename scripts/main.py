import os
from dropbox_manager import get_next_video_from_dropbox, archive_published_video
from ai_content import generate_post_copy
import requests

def publish_to_meta(media_url, caption, media_type="VIDEO"):
    page_id = os.environ.get("META_PAGE_ID")
    ig_account_id = os.environ.get("META_IG_ACCOUNT_ID")
    access_token = os.environ.get("META_ACCESS_TOKEN")
    
    # 1. Publicar en Facebook
    print(f"Publicando {media_type} en Facebook...")
    fb_url = f"https://graph.facebook.com/v26.0/{page_id}/feed" if media_type == "TEXT" else f"https://graph.facebook.com/v26.0/{page_id}/videos"
    
    fb_payload = {
        "access_token": access_token,
        "message": caption
    }
    if media_type == "VIDEO":
        fb_payload["file_url"] = media_url
    elif media_type == "IMAGE":
        fb_payload["url"] = media_url
        
    response = requests.post(fb_url, data=fb_payload)
    print("Respuesta Facebook:", response.json())

    # 2. Publicar en Instagram (si aplica para video o imagen)
    if ig_account_id and media_type != "TEXT":
        print(f"Publicando {media_type} en Instagram...")
        # Paso 1 de Instagram: Crear el contenedor de medios
        container_url = f"https://graph.facebook.com/v26.0/{ig_account_id}/media"
        container_payload = {
            "access_token": access_token,
            "caption": caption
        }
        if media_type == "VIDEO":
            container_payload["media_type"] = "REELS"
            container_payload["video_url"] = media_url
        else:
            container_payload["image_url"] = media_url
            
        container_res = requests.post(container_url, data=container_payload).json()
        
        if "id" in container_res:
            creation_id = container_res["id"]
            # Paso 2 de Instagram: Publicar el contenedor
            publish_url = f"https://graph.facebook.com/v26.0/{ig_account_id}/media_publish"
            publish_payload = {
                "access_token": access_token,
                "creation_id": creation_id
            }
            pub_res = requests.post(publish_url, data=publish_payload).json()
            print("Respuesta Instagram:", pub_res)
        else:
            print("Error al crear contenedor en Instagram:", container_res)

def main():
    print("Iniciando ciclo de automatización de FrigZone-Publisher...")
    
    # Intentamos buscar un video pendiente en Dropbox
    video_data = get_next_video_from_dropbox()
    
    if video_data:
        print(f"Procesando video de trabajo: {video_data['name']}")
        # Generamos un texto dinámico con IA para acompañar el video real
        caption = generate_post_copy() or "Nuevo trabajo técnico realizado por FrigZone. Climatización y refrigeración profesional."
        
        # Publicamos en Meta
        publish_to_meta(video_data['url'], caption, media_type="VIDEO")
        
        # Archivamos el video para que no se vuelva a publicar
        archive_published_video(video_data['path'], video_data['name'])
    else:
        print("No hay videos en Dropbox. Generando contenido alternativo con Gemini AI...")
        ai_text = generate_post_copy()
        if ai_text:
            # Si no hay video, publicamos el tip de texto/ IA directamente en Facebook
            publish_to_meta(None, ai_text, media_type="TEXT")

if __name__ == "__main__":
    main()