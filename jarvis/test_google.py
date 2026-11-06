import speech_recognition as sr
import sounddevice as sd
import numpy as np

r = sr.Recognizer()
r.dynamic_energy_threshold = False
r.energy_threshold = 50  # Súper sensible

print("Probando dispositivos:")
for dev_idx in [1, 2]:
    name = sr.Microphone.list_microphone_names()[dev_idx]
    print(f"\nDispositivo [{dev_idx}]: {name}")
    try:
        with sr.Microphone(device_index=dev_idx) as source:
            print("Escuchando 3 segundos...")
            audio = r.listen(source, timeout=4, phrase_time_limit=3)
            print("Audio capturado. Longitud bytes:", len(audio.get_raw_data()))
            try:
                txt = r.recognize_google(audio, language="es-ES")
                print("-> Reconocido con éxito:", txt)
            except sr.UnknownValueError:
                print("-> Google no detectó palabras (silencio o ruido)")
            except Exception as e:
                print("-> Error de Google:", e)
    except Exception as e:
        print("-> Error de escucha:", e)
