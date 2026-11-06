import sounddevice as sd
import numpy as np
import speech_recognition as sr

print("=== ESCANEO DE DISPOSITIVOS DE ENTRADA (MICRÓFONOS) ===")
for i, d in enumerate(sd.query_devices()):
    if d.get("max_input_channels", 0) > 0 and d.get("hostapi") == 0:
        name = d.get("name", "Desconocido")
        try:
            rec = sd.rec(int(44100 * 0.8), samplerate=44100, channels=1, device=i)
            sd.wait()
            rms = float(np.sqrt(np.mean(rec**2)))
            print(f"[{i}] {name} -> Nivel RMS: {rms:.6f}")
        except Exception as e:
            print(f"[{i}] {name} -> Error: {e}")

print("\n=== DISPOSITIVOS PREDETERMINADOS DE WINDOWS ===")
print("Default Input:", sd.default.device[0], sd.query_devices(sd.default.device[0])["name"])
print("Default Output:", sd.default.device[1], sd.query_devices(sd.default.device[1])["name"])
