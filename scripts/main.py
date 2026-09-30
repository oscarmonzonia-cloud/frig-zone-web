import os
import time
import requests
from dropbox_manager import (
    get_next_video_from_dropbox, 
    archive_published_video, 
    get_next_image_from_dropbox,
    archive_published_image,
    upload_generated_image_to_dropbox
)
from ai_content import generate_post_content, generate_ai_image, create_fallback_image

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
            
            # Esperamos a que Instagram procese el contenido multimedia
            print(f"Esperando a que Instagram procese el contenido ({media_type})...")
            for attempt in range(1, 12):
                time.sleep(5)
                status_url = f"https://graph.facebook.com/v26.0/{creation_id}?fields=status_code&access_token={access_token}"
                status_res = requests.get(status_url).json()
                code = status_res.get("status_code")
                print(f"Estado en Instagram (Intento {attempt}/11): {code}")
                
                if code == "FINISHED":
                    break
                elif code == "ERROR":
                    print("Error reportado por Instagram durante el procesamiento:", status_res)
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
        caption, _, _ = generate_post_content()
        final_caption = caption or f"Trabajo técnico de FrigZone: {video_data['name']}"
        
        publish_to_meta(video_data['url'], final_caption, media_type="VIDEO")
        archive_published_video(video_data['path'], video_data['name'])
        return

    # 2. Si no hay videos, buscamos si hay imágenes en la cola de Dropbox (imagenes-pendientes)
    image_data = get_next_image_from_dropbox()
    
    if image_data:
        print(f"Imagen detectada en la cola de Dropbox: {image_data['name']}")
        caption, _, _ = generate_post_content()
        final_caption = caption or f"Consejo de climatización FrigZone: {image_data['name']}"
        
        publish_to_meta(image_data['url'], final_caption, media_type="IMAGE")
        archive_published_image(image_data['path'], image_data['name'])
        return

    # 3. Si no hay videos ni imágenes en cola, recurrimos al contenido automático con IA
    print("No hay videos ni imágenes en cola. Creando contenido automático con IA (Texto y Respaldo Visual)...")
    post_text, image_prompt, placa_title = generate_post_content()
    
    if post_text:
        local_img = None
        if image_prompt:
            local_img = generate_ai_image(image_prompt, output_filename="frigzone_ai.jpg")
        
        if not local_img:
            print("⚠️ La IA visual no pudo generar la imagen (cuota o alta demanda).")
            print("Activando respaldo inteligente: Generando placa gráfica corporativa en JPG...")
            local_img = create_fallback_image(placa_title, post_text, output_filename="post_placa.jpg")
        
        if local_img:
            timestamp = int(time.time())
            filename = f"post_final_{timestamp}.jpg"
            dropbox_img_url = upload_generated_image_to_dropbox(local_img, filename)
            
            if dropbox_img_url:
                print(f"Imagen lista en Dropbox. Publicando en Meta como IMAGEN...")
                publish_to_meta(dropbox_img_url, post_text, media_type="IMAGE")
                
                # NUEVO: Movemos la imagen generada automáticamente al histórico tras publicarla con éxito
                remote_path = f"/FrigZone-AutoQueue/imagenes-generadas/{filename}"
                archive_published_image(remote_path, filename)
            else:
                print("Error al subir la imagen final a Dropbox.")
        else:
            print("Error crítico: No se pudo obtener ni generar ninguna imagen para la publicación.")

if __name__ == "__main__":
    main()
