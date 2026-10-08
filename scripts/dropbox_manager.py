import os
import dropbox
from dropbox.files import WriteMode

def get_dbx_client():
    """Crea una sesión de Dropbox utilizando un Access Token directo de forma limpia"""
    access_token = os.environ.get("DROPBOX_ACCESS_TOKEN")
    if not access_token:
        raise ValueError("No se encontró el DROPBOX_ACCESS_TOKEN en las variables de entorno.")
    return dropbox.Dropbox(access_token, desktop=False)


def upload_generated_image_to_dropbox(local_file_path, filename):
    dbx = get_dbx_client()
    dest_path = f"/FrigZone-AutoQueue/imagenes-generadas/{filename}"
    
    with open(local_file_path, "rb") as f:
        dbx.files_upload(f.read(), dest_path, mode=dropbox.files.WriteMode.overwrite)
    
    # Creamos un enlace compartido público o recuperamos el existente
    url = ""
    try:
        shared_link_metadata = dbx.sharing_create_shared_link_with_settings(dest_path)
        url = shared_link_metadata.url
    except Exception:
        links = dbx.sharing_list_shared_links(path=dest_path).links
        if links:
            url = links[0].url

    # Convertimos la URL al formato de descarga directa pura de Dropbox (esencial para Meta)
    direct_url = url.replace("www.dropbox.com", "dl.dropboxusercontent.com").replace("?dl=0", "").replace("?dl=1", "") + "?dl=1"
    return direct_url

def get_next_video_from_dropbox():
    try:
        dbx = get_dbx_client()
    except Exception as e:
        print(f"Error al conectar con Dropbox (videos): {e}")
        return None
        
    folder_path = "/FrigZone-AutoQueue/videos-pendientes"
    
    try:
        result = dbx.files_list_folder(folder_path)
        files = [f for f in result.entries if isinstance(f, dropbox.files.FileMetadata)]
        
        if not files:
            print("No hay videos pendientes en la cola de Dropbox.")
            return None
        
        files.sort(key=lambda x: x.server_modified)
        target_file = files[0]
        
        print(f"Video seleccionado para publicar: {target_file.name}")
        
        try:
            shared_link_metadata = dbx.sharing_create_shared_link_with_settings(target_file.path_lower)
            link_url = shared_link_metadata.url
        except Exception:
            links = dbx.sharing_list_shared_links(path=target_file.path_lower).links
            link_url = links[0].url if links else ""

        direct_url = link_url.replace("www.dropbox.com", "dl.dropboxusercontent.com").replace("dl=0", "dl=1")
        
        return {
            "name": target_file.name,
            "path": target_file.path_lower,
            "url": direct_url
        }
    except Exception as e:
        print(f"Error al conectar con Dropbox (videos): {e}")
        return None

def get_next_image_from_dropbox():
    """Busca la siguiente imagen pendiente en la cola de Dropbox (FIFO)"""
    try:
        dbx = get_dbx_client()
    except Exception:
        return None
        
    folder_path = "/FrigZone-AutoQueue/imagenes-pendientes"
    
    try:
        result = dbx.files_list_folder(folder_path)
        # Filtramos solo archivos de imagen válidos
        valid_exts = (".jpg", ".jpeg", ".png", ".webp")
        files = [f for f in result.entries if isinstance(f, dropbox.files.FileMetadata) and f.name.lower().endswith(valid_exts)]
        
        if not files:
            print("No hay imágenes pendientes en la cola de Dropbox.")
            return None
        
        files.sort(key=lambda x: x.server_modified)
        target_file = files[0]
        
        print(f"Imagen seleccionada de la cola de Dropbox: {target_file.name}")
        
        try:
            shared_link_metadata = dbx.sharing_create_shared_link_with_settings(target_file.path_lower)
            link_url = shared_link_metadata.url
        except Exception:
            links = dbx.sharing_list_shared_links(path=target_file.path_lower).links
            link_url = links[0].url if links else ""

        direct_url = link_url.replace("www.dropbox.com", "dl.dropboxusercontent.com").replace("?dl=0", "").replace("?dl=1", "") + "?dl=1"
        
        return {
            "name": target_file.name,
            "path": target_file.path_lower,
            "url": direct_url
        }
    except Exception as e:
        print(f"Error al conectar con Dropbox (imágenes): {e}")
        return None

def archive_published_video(file_path, file_name):
    dbx = get_dbx_client()
    destination_path = f"/FrigZone-History/{file_name}"
    try:
        dbx.files_move_v2(file_path, destination_path, autorename=True)
        print(f"Video movido exitosamente al historial: {file_name}")
    except Exception as e:
        print(f"Error al archivar el video en Dropbox: {e}")

def archive_published_image(file_path, file_name):
    """Mueve la imagen publicada desde la cola al histórico"""
    dbx = get_dbx_client()
    destination_path = f"/FrigZone-History/{file_name}"
    try:
        dbx.files_move_v2(file_path, destination_path, autorename=True)
        print(f"Imagen movida exitosamente al historial: {file_name}")
    except Exception as e:
        print(f"Error al archivar la imagen en Dropbox: {e}")