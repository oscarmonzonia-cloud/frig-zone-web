import os
import time
import requests
from dropbox_manager import (
    get_next_video_from_dropbox, 
    archive_published_video, 
    upload_generated_image_to_dropbox
)
from ai_content import generate_post_content, generate_ai_image

def publish_to_meta(media_url, caption, media_type="VIDEO"):
    page_id = os.environ.get("META_PAGE_ID")
    ig_account_id = os.environ.get("META_IG_ACCOUNT_ID")
    access_token = os.environ.get("META_ACCESS_TOKEN")
    
    # 1. Publicar en Facebook
    print(f"Publicando {media_type} en Facebook...")
    fb_url = f"https://graph.facebook.com/v26.0/{page_id}/feed" if media_type == "TEXT" else f"https://graph.facebook.com/v26.0/{page_id}/videos" if media_type == "VIDEO" else f"https://graph.facebook.com/v26.0/{page_id}/photos"
    
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

    # 2. Publicar en Instagram
    if ig_account_id and media_type != "TEXT":
        print(f"Publicando {media_type} en Instagram...")
        container_url = f"https://graph.facebook.com/v26.0/{ig_account_id}/media"
        container_payload = {
            "access_token": access_token,
            "caption": caption
        }
        if media_type == "VIDEO":
            container_payload["media_type"] = "REELS"
            container_payload["video_url"] = media_url
        elif media_type == "IMAGE":
            container_payload["image_url"] = media_url
            
        container_res = requests.post(container_url, data=container_payload).json()
        
        if "id" in container_res:
            creation_id = container_res["id"]
            
            # Si es video, esperamos a que procese
            if media_type == "VIDEO":
                print("Esperando a que Instagram procese el video...")
                for _ in range(12):
                    time.sleep(5)
                    status_url = f"https://graph.facebook.com/v26.0/{creation_id}?fields=status_code&access_token={access_token}"
                    code = requests.get(status_url).json().get("status_code")
                    if code == "FINISHED":
                        break

            # Publicar el contenedor en Instagram
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
    print("Iniciando ciclo inteligente de automatización FrigZone...")
    
    # 1. Intentamos buscar si hay un video real del usuario en la cola de Dropbox
    video_data = get_next_video_from_dropbox()
    
    if video_data:
        print(f"Video detectado en Dropbox: {video_data['name']}")
        caption, _ = generate_post_content() # Usamos IA solo para redactar el copy del video
        final_caption = caption or f"Trabajo técnico de FrigZone: {video_data['name']}"
        
        publish_to_meta(video_data['url'], final_caption, media_type="VIDEO")
        archive_published_video(video_data['path'], video_data['name'])
    else:
        print("No hay videos en cola. Creando contenido automático con IA (Texto e Imagen)...")
        post_text, image_prompt = generate_post_content()
        
        if post_text and image_prompt:
            # Generamos la imagen con el modelo Imagen de Google
            local_img = generate_ai_image(image_prompt, output_filename="frigzone_ai.jpg")
            
            if local_img:
                # Subimos la imagen generada a Dropbox para respaldo y obtenemos link público
                timestamp = int(time.time())
                dropbox_img_url = upload_generated_image_to_dropbox(local_img, f"post_ia_{timestamp}.jpg")
                
                print(f"Imagen subida a Dropbox. Publicando en Meta...")
                publish_to_meta(dropbox_img_url, post_text, media_type="IMAGE")

if __name__ == "__main__":
    main()