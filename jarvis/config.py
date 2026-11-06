"""
Configuración central de JARVIS.
Permite personalizar la voz, el modelo de IA (local u online), y los dispositivos de audio.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# --- CONFIGURACIÓN DE IDENTIDAD ---
ASSISTANT_NAME = "JARVIS"
USER_TITLE = "señor"
WAKE_WORDS = [
    "jarvis", "oye jarvis", "hola jarvis", "hey jarvis",
    "chárvis", "charvis", "llarvis", "yarvis", "service",
    "yervis", "larvis", "arvis", "chávez", "jarvis,"
]

# --- VOZ Y AUDIO (TTS / STT) ---
TTS_ENGINE = "gtts"  # 'gtts' (reproduce por sounddevice directamente al parlante) o 'sapi5'
TTS_SPEED = 1.05
STT_LANGUAGE = "es-ES"

def find_audio_device(name_substring, is_output=True, fallback_index=None):
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        for idx, dev in enumerate(devices):
            channels = dev.get("max_output_channels" if is_output else "max_input_channels", 0)
            if channels > 0 and name_substring.lower() in dev.get("name", "").lower():
                return idx
    except Exception:
        pass
    return fallback_index

# Dispositivos de audio: Detección inteligente con índice de respaldo
OUTPUT_DEVICE_INDEX = 3
MICROPHONE_INDEX = 2

# Sensibilidad y búfer del micrófono (STT optimizado sin cortes)
ENERGY_THRESHOLD = 120   # Sensibilidad alta para captar el micrófono de auriculares
DYNAMIC_THRESHOLD = True
STT_PAUSE_THRESHOLD = 0.8        # Tiempo de silencio antes de considerar finalizada la frase (evita cortes)
STT_NON_SPEAKING_DURATION = 0.5  # Búfer de silencio retenido
STT_TIMEOUT = 7                  # Espera máxima para inicio de voz
STT_PHRASE_TIME_LIMIT = 15       # Tiempo límite por frase completa

# Sonidos de confirmación
ENABLE_SOUND_EFFECTS = True

# --- PROVEEDORES Y MODELOS DE IA ---
# Proveedor activo: 'ollama' (Local privado en GPU Intel Arc B580) o 'gemini' (Nube)
ACTIVE_PROVIDER = "ollama"

# Configuración Gemini en la Nube
GEMINI_API_KEY = "AIzaSyCBWtmrGijFks4Zv7p1zXafi2xwtWAfAoA"
GEMINI_MODEL = "gemini-2.5-flash"

# Configuración Ollama Local (GPU Intel Arc B580 12GB VRAM + Ryzen 7 5700G)
OLLAMA_BASE_URL = "http://127.0.0.1:11434"
OLLAMA_MODEL = "qwen2.5-coder:14b"
OLLAMA_NUM_CTX = 16384           # Contexto amplio soportado en VRAM de 12GB
OLLAMA_KEEP_ALIVE = -1           # Persistencia perpetua en VRAM (0 latencia de carga)

# Parámetros de generación
TEMPERATURE = 0.6
MAX_TOKENS = 180  # Respuestas orales concisas

# --- INTEGRACIÓN CON OPENCLAW ---
OPENCLAW_ENABLED = True
OPENCLAW_URL = "http://127.0.0.1:18789"
OPENCLAW_TOKEN = "e9d7182aeb396a42b51ee744dff17c29642af493ef5122df"

# --- MODO DE INTERACCIÓN ---
DEFAULT_MODE = 1
