"""
Motor de Síntesis de Voz (TTS) y Reproducción de Audio para JARVIS.
Utiliza gTTS + sounddevice (reproducción directa por hardware) con respaldo en pyttsx3/pygame.
"""
import os
import re
import time
import tempfile
import threading
import sounddevice as sd
import soundfile as sf
from jarvis import config

def get_real_output_devices():
    """Devuelve los dispositivos de salida de audio reales en el sistema."""
    devices = []
    seen = set()
    for idx, d in enumerate(sd.query_devices()):
        if d.get("max_output_channels", 0) > 0:
            name = d.get("name", "")
            # Limpiar nombre
            clean_name = name.encode("utf-8", "ignore").decode("utf-8", "ignore")
            if clean_name not in seen:
                devices.append({"index": idx, "name": clean_name})
                seen.add(clean_name)
    return devices

def clean_text_for_speech(text: str) -> str:
    """Limpia markdown, código, emojis y caracteres no pronunciables."""
    if not text:
        return ""
    text = re.sub(r'```[\s\S]*?```', 'He generado un bloque de código.', text)
    text = re.sub(r'`[^`]+`', '', text)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    text = re.sub(r'[\*#_~>]', '', text)
    text = re.sub(r'https?://\S+', 'un enlace web', text)
    return text.strip()

def split_into_sentences(text: str) -> list:
    """Divide el texto en oraciones naturales para procesar fragmentos sin cortar a mitad de frase."""
    if not text:
        return []
    raw_sentences = re.split(r'(?<=[.!?:;\n])\s+', text)
    chunks = []
    for s in raw_sentences:
        clean_s = s.strip()
        if clean_s:
            chunks.append(clean_s)
    return chunks if chunks else [text.strip()]

_sapi_engine = None

def get_sapi_engine():
    global _sapi_engine
    if _sapi_engine is None:
        try:
            import pyttsx3
            _sapi_engine = pyttsx3.init('sapi5')
            voices = _sapi_engine.getProperty('voices')
            for v in voices:
                if any(t in v.name.lower() for t in ['spanish', 'helena', 'sabina']):
                    _sapi_engine.setProperty('voice', v.id)
                    break
            _sapi_engine.setProperty('rate', 170)
        except Exception as e:
            print(f"[!] Error inicializando pyttsx3: {e}")
    return _sapi_engine

class TTSEngine:
    def __init__(self, output_device=config.OUTPUT_DEVICE_INDEX):
        self.lock = threading.Lock()
        self.is_speaking = False
        self.output_device = output_device

    def set_output_device(self, dev_idx):
        self.output_device = dev_idx

    def get_output_device_name(self):
        try:
            if self.output_device is not None:
                info = sd.query_devices(self.output_device)
                return f"[{self.output_device}] {info['name']}"
            default_out = sd.default.device[1]
            info = sd.query_devices(default_out)
            return f"[{default_out}] {info['name']} (Predeterminado)"
        except Exception:
            return "Altavoces del sistema"

    def test_tone(self, dev_idx=None):
        """Reproduce un breve tono de prueba en el dispositivo."""
        try:
            import numpy as np
            fs = 44100
            t = np.linspace(0, 0.4, int(fs * 0.4), endpoint=False)
            tone = 0.3 * np.sin(2 * np.pi * 587.33 * t)  # Nota Re
            target = dev_idx if dev_idx is not None else self.output_device
            sd.play(tone, fs, device=target)
            sd.wait()
            return True
        except Exception as e:
            print(f"[!] Error en tono de prueba: {e}")
            return False

    def speak_gtts_sounddevice(self, text: str) -> bool:
        """Genera voz natural con gTTS y la reproduce directamente por hardware con sounddevice."""
        from gtts import gTTS
        temp_path = None
        try:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            temp_path = temp_file.name
            temp_file.close()

            # Generar audio
            tts = gTTS(text=text, lang="es", tld="com.mx", slow=False)
            tts.save(temp_path)

            # Leer datos decodificados directamente
            data, fs = sf.read(temp_path)

            # Reproducir al dispositivo de salida configurado
            sd.play(data, fs, device=self.output_device)
            sd.wait()

            try:
                os.remove(temp_path)
            except Exception:
                pass
            return True
        except Exception as e:
            print(f"[!] Error en gTTS + sounddevice: {e}. Probando respaldo pygame...")
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass
            return self.speak_pygame_fallback(text)

    def speak_pygame_fallback(self, text: str) -> bool:
        """Respaldo mediante pygame."""
        try:
            import pygame
            from gtts import gTTS
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            temp_path = temp_file.name
            temp_file.close()

            tts = gTTS(text=text, lang="es", slow=False)
            tts.save(temp_path)

            pygame.mixer.music.load(temp_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.05)
            pygame.mixer.music.unload()
            try:
                os.remove(temp_path)
            except Exception:
                pass
            return True
        except Exception as e:
            print(f"[!] Error en pygame fallback: {e}")
            return self.speak_sapi5(text)

    def speak_sapi5(self, text: str) -> bool:
        """Respaldo offline nativo de Windows (Helena)."""
        engine = get_sapi_engine()
        if engine:
            try:
                engine.say(text)
                engine.runAndWait()
                return True
            except Exception as e:
                print(f"[!] Error en SAPI5: {e}")
        return False

    def speak(self, text: str):
        """Punto de entrada principal para reproducir voz en tiempo real sin cortes."""
        cleaned = clean_text_for_speech(text)
        if not cleaned:
            return

        with self.lock:
            self.is_speaking = True
            try:
                sentences = split_into_sentences(cleaned)
                for sentence in sentences:
                    if not sentence:
                        continue
                    if config.TTS_ENGINE == "gtts":
                        success = self.speak_gtts_sounddevice(sentence)
                        if not success:
                            self.speak_sapi5(sentence)
                    else:
                        self.speak_sapi5(sentence)
            finally:
                self.is_speaking = False

    def stop(self):
        try:
            sd.stop()
        except Exception:
            pass
