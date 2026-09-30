import os
import dropbox
from dropbox.files import WriteMode


def upload_generated_image_to_dropbox(local_file_path, filename):
    dbx = dropbox.Dropbox(os.environ.get("DROPBOX_ACCESS_TOKEN"))
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
    # Lee el token de acceso desde las variables de entorno de forma segura
    dbx_token = os.environ.get("DROPBOX_ACCESS_TOKEN")
    
    if not dbx_token:
        raise ValueError("No se encontró el DROPBOX_ACCESS_TOKEN en las variables de entorno.")
    
    dbx = dropbox.Dropbox(dbx_token)
    
    folder_path = "/FrigZone-AutoQueue/videos-pendientes" # Tu ruta real en Dropbox
    history_path = "/FrigZone-AutoQueue/videos-historico" # O la carpeta donde quieras archivarlos 
    try:
        # Lista los archivos en la carpeta de pendientes
        result = dbx.files_list_folder(folder_path)
        files = [f for f in result.entries if isinstance(f, dropbox.files.FileMetadata)]
        
        if not files:
            print("No hay videos pendientes en la cola de Dropbox.")
            return None
        
        # Ordena por fecha para tomar el más antiguo (FIFO: First In, First Out)
        files.sort(key=lambda x: x.server_modified)
        target_file = files[0]
        
        print(f"Video seleccionado para publicar: {target_file.name}")
        
        # Genera o solicita un enlace temporal o directo compartido
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
        print(f"Error al conectar con Dropbox: {e}")
        return None

def archive_published_video(file_path, file_name):
    dbx = dropbox.Dropbox(os.environ.get("DROPBOX_ACCESS_TOKEN"))
    destination_path = f"/FrigZone-History/{file_name}"
    
    try:
        # Mueve el archivo a la carpeta de histórico para no repetirlo
        dbx.files_move_v2(file_path, destination_path, autorename=True)
        print(f"Video movido exitosamente al historial: {file_name}")
    except Exception as e:
        print(f"Error al archivar el video en Dropbox: {e}")
