"""
Herramientas del sistema y control de Windows para JARVIS.
Permite abrir programas, buscar información, controlar volumen y monitorizar hardware.
"""
import os
import sys
import subprocess
import webbrowser
import datetime
import psutil
import requests
from jarvis import config

# Días y meses en español
DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MESES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
]

def get_time_and_date():
    """Devuelve la hora y fecha actual de forma natural."""
    now = datetime.datetime.now()
    dia_semana = DIAS[now.weekday()]
    dia = now.day
    mes = MESES[now.month - 1]
    hora = now.strftime("%H:%M")
    return f"Son las {hora} del {dia_semana} {dia} de {mes}."

def get_system_status():
    """Obtiene métricas de CPU, memoria RAM y almacenamiento."""
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage("C:")
    
    battery = psutil.sensors_battery()
    bat_str = ""
    if battery:
        bat_str = f" Batería al {int(battery.percent)}%."

    return (
        f"Diagnóstico de sistemas: CPU al {cpu}%, "
        f"Memoria RAM al {int(ram.percent)}% ({round(ram.used / (1024**3), 1)} gigabytes en uso), "
        f"y disco principal con {round(disk.free / (1024**3), 1)} gigabytes disponibles.{bat_str}"
    )

def open_application(app_name: str) -> str:
    """Abre aplicaciones estándar de Windows."""
    name = app_name.lower().strip()
    try:
        if "calc" in name or "calculadora" in name:
            subprocess.Popen("calc.exe")
            return "Abriendo la calculadora, señor."
        elif "notepad" in name or "bloc de notas" in name or "notas" in name:
            subprocess.Popen("notepad.exe")
            return "Abriendo el Bloc de Notas."
        elif "explorador" in name or "archivos" in name or "carpeta" in name:
            subprocess.Popen("explorer.exe")
            return "Abriendo el Explorador de Archivos."
        elif "chrome" in name:
            subprocess.Popen(["start", "chrome"], shell=True)
            return "Abriendo Google Chrome."
        elif "spotify" in name:
            subprocess.Popen(["start", "spotify:"], shell=True)
            return "Iniciando Spotify."
        elif "vs code" in name or "visual studio code" in name or "code" in name:
            subprocess.Popen(["code"], shell=True)
            return "Abriendo Visual Studio Code."
        elif "terminal" in name or "consola" in name or "powershell" in name:
            subprocess.Popen(["start", "powershell"], shell=True)
            return "Iniciando la consola de comandos."
        elif "administrador de tareas" in name:
            subprocess.Popen("taskmgr.exe")
            return "Abriendo el Administrador de Tareas."
        else:
            # Intento genérico usando el comando start de Windows
            subprocess.Popen(f"start {app_name}", shell=True)
            return f"Intentando iniciar {app_name}."
    except Exception as e:
        return f"No pude iniciar la aplicación: {e}"

def search_web(query: str, target="google"):
    """Realiza búsquedas en la web o en YouTube."""
    query = query.strip()
    if not query:
        return "No especificó qué buscar, señor."
    
    if target == "youtube" or "youtube" in query.lower():
        clean_q = query.lower().replace("en youtube", "").replace("youtube", "").strip()
        url = f"https://www.youtube.com/results?search_query={clean_q}"
        webbrowser.open(url)
        return f"Buscando '{clean_q}' en YouTube."
    else:
        clean_q = query.lower().replace("en google", "").replace("google", "").strip()
        url = f"https://www.google.com/search?q={clean_q}"
        webbrowser.open(url)
        return f"Buscando '{clean_q}' en Google."

def control_volume(action: str):
    """Controla el volumen de Windows usando comandos nativos."""
    import ctypes
    VK_VOLUME_MUTE = 0xAD
    VK_VOLUME_DOWN = 0xAE
    VK_VOLUME_UP = 0xAF
    
    if "sub" in action or "aument" in action:
        for _ in range(5):
            ctypes.windll.user32.keybd_event(VK_VOLUME_UP, 0, 0, 0)
        return "Subiendo el volumen."
    elif "baj" in action or "disminu" in action:
        for _ in range(5):
            ctypes.windll.user32.keybd_event(VK_VOLUME_DOWN, 0, 0, 0)
        return "Bajando el volumen."
    elif "mute" in action or "silenc" in action:
        ctypes.windll.user32.keybd_event(VK_VOLUME_MUTE, 0, 0, 0)
        return "Alternando silencio del sistema."
    return "Comando de volumen no reconocido."

def delegate_to_openclaw(instruction: str):
    """Envía instrucciones complejas al agente OpenClaw."""
    if not config.OPENCLAW_ENABLED:
        return "El enlace con OpenClaw está deshabilitado en la configuración."
    
    # 1. Intento vía CLI oficial del Gateway de OpenClaw
    try:
        import subprocess
        result = subprocess.run(
            f'openclaw agent --message "{instruction}" --json',
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=25,
            shell=True
        )
        if result.returncode == 0 and result.stdout:
            try:
                data = json.loads(result.stdout)
                payloads = data.get("result", {}).get("payloads", [])
                if payloads and "text" in payloads[0]:
                    return payloads[0]["text"]
            except Exception:
                pass
            return result.stdout.strip()
    except Exception:
        pass

    # 2. Intento vía API HTTP del Gateway
    try:
        headers = {
            "Authorization": f"Bearer {config.OPENCLAW_TOKEN}",
            "Content-Type": "application/json"
        }
        resp = requests.post(
            f"{config.OPENCLAW_URL}/api/agent/chat",
            json={"message": instruction},
            headers=headers,
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get("response", "Orden enviada a OpenClaw con éxito.")
    except Exception as e:
        return f"No se pudo conectar con el agente OpenClaw: {e}"

    return "Orden delegada a OpenClaw, señor."
