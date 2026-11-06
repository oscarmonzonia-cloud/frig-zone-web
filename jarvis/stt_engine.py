"""
Motor de Reconocimiento de Voz (STT) para JARVIS.
Escucha el micrófono del usuario y transcribe a texto en tiempo real con latencia reducida.
"""
import speech_recognition as sr
import winsound
import time
from jarvis import config

def get_real_microphones():
    devices = []
    seen_names = set()
    for idx, name in enumerate(sr.Microphone.list_microphone_names()):
        lower = name.lower()
        if any(term in lower for term in ["salida", "output", "speakers", "altavoces", "hdmi"]):
            continue
        clean_name = name.encode('utf-8', 'ignore').decode('utf-8', 'ignore')
        if clean_name not in seen_names:
            devices.append({"index": idx, "name": clean_name})
            seen_names.add(clean_name)
    return devices

class STTEngine:
    def __init__(self, device_index=config.MICROPHONE_INDEX):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = config.ENERGY_THRESHOLD
        self.recognizer.dynamic_energy_threshold = config.DYNAMIC_THRESHOLD
        # Búfer de audio calibrado para procesamiento en tiempo real sin cortes a mitad de frase
        self.recognizer.pause_threshold = getattr(config, "STT_PAUSE_THRESHOLD", 0.8)
        self.recognizer.non_speaking_duration = getattr(config, "STT_NON_SPEAKING_DURATION", 0.5)
        self.recognizer.phrase_threshold = 0.3  # Filtra chasquidos o golpes accidentales de aire
        self.recognizer.dynamic_energy_adjustment_damping = 0.15
        self.recognizer.dynamic_energy_ratio = 1.5
        
        self.device_index = device_index
        try:
            self.microphone = sr.Microphone(device_index=self.device_index)
        except Exception as e:
            print(f"[!] Advertencia con micrófono {self.device_index}: {e}. Usando predeterminado.")
            self.microphone = sr.Microphone()
            self.device_index = None

        self.is_calibrated = False

    def get_device_name(self):
        try:
            names = sr.Microphone.list_microphone_names()
            if self.device_index is not None and self.device_index < len(names):
                return f"[{self.device_index}] {names[self.device_index]}"
            return f"[Default] {names[0] if names else 'Sistema'}"
        except Exception:
            return "Micrófono predeterminado"

    def play_sound_alert(self, sound_type="listen"):
        if not config.ENABLE_SOUND_EFFECTS:
            return
        try:
            if sound_type == "listen":
                winsound.Beep(1200, 50)
            elif sound_type == "processing":
                winsound.Beep(950, 40)
            elif sound_type == "error":
                winsound.Beep(440, 100)
        except Exception:
            pass

    def calibrate(self):
        if not self.is_calibrated:
            try:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.4)
                    if self.recognizer.energy_threshold > 300:
                        self.recognizer.energy_threshold = 220
                    elif self.recognizer.energy_threshold < 100:
                        self.recognizer.energy_threshold = 150
                self.is_calibrated = True
            except Exception as e:
                print(f"[!] Error calibrando micrófono: {e}")

    def listen(self, timeout=config.STT_TIMEOUT, phrase_time_limit=config.STT_PHRASE_TIME_LIMIT):
        self.calibrate()
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
            
            # Reconocimiento con Google Speech API
            text = self.recognizer.recognize_google(audio, language=config.STT_LANGUAGE)
            return text.strip(), "OK"
        except sr.WaitTimeoutError:
            return None, "TIMEOUT"
        except sr.UnknownValueError:
            return None, "NO_SPEECH"
        except sr.RequestError as e:
            text = self._listen_whisper(audio)
            if text:
                return text, "OK"
            return None, f"ERROR_API: {e}"
        except Exception as e:
            return None, f"ERROR: {e}"

    def _listen_whisper(self, audio):
        try:
            from faster_whisper import WhisperModel
            import io
            wav_data = io.BytesIO(audio.get_wav_data())
            model = WhisperModel("tiny", device="cpu", compute_type="int8")
            segments, _ = model.transcribe(wav_data, language="es")
            text = " ".join([seg.text for seg in segments]).strip()
            return text if text else None
        except Exception as e:
            return None
