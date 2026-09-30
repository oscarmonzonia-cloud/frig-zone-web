import os
import dropbox
from dropbox.files import WriteMode

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
        # Nota: Dropbox permite obtener un enlace de descarga directa modificando el parámetro final a dl=1
        shared_link_metadata = dbx.sharing_create_shared_link_with_settings(target_file.path_lower)
        direct_url = shared_link_metadata.url.replace("www.dropbox.com", "dl.dropboxusercontent.com").replace("dl=0", "dl=1")
        
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