"""
Calibrador y Detector Automático de Micrófono y Auriculares para JARVIS.
Permite ver el volumen del micrófono en tiempo real y probar el audio en los auriculares.
"""
import sys
import os
import time
import numpy as np
import sounddevice as sd
import soundfile as sf
import tempfile
from gtts import gTTS

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from jarvis import config

def test_microphone_meter(device_idx, device_name, duration=4):
    """Muestra una barra de volumen en tiempo real durante 4 segundos."""
    print(f"\n========================================================")
    print(f"Probando: [{device_idx}] {device_name}")
    print(f"Por favor, habla ahora en tu micrófono...")
    print(f"========================================================")
    
    max_level = 0.0
    start_time = time.time()
    
    def callback(indata, frames, time_info, status):
        nonlocal max_level
        rms = float(np.sqrt(np.mean(indata**2)))
        if rms > max_level:
            max_level = rms
        # Escala visual de 0 a 30 caracteres
        bars = int(min(rms * 200, 30))
        meter = "#" * bars + "-" * (30 - bars)
        print(f"\r  Volumen detectado: [{meter}] ({rms:.4f})", end="", flush=True)

    try:
        with sd.InputStream(device=device_idx, channels=1, samplerate=44100, callback=callback):
            while time.time() - start_time < duration:
                time.sleep(0.1)
    except Exception as e:
        print(f"\n  [!] Error al abrir dispositivo: {e}")
        return 0.0

    print()
    return max_level

def test_output_voice(device_idx, device_name):
    """Reproduce una frase por los auriculares para confirmar recepción."""
    print(f"\nReproduciendo mensaje de prueba en [{device_idx}] {device_name}...")
    try:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        temp_path = temp_file.name
        temp_file.close()

        tts = gTTS(text="Prueba de audio de Jarvis. Si escuchas esto, tus auriculares funcionan.", lang="es")
        tts.save(temp_path)
        data, fs = sf.read(temp_path)

        sd.play(data, fs, device=device_idx)
        sd.wait()

        try:
            os.remove(temp_path)
        except Exception:
            pass
        return True
    except Exception as e:
        print(f"[!] Error reproduciendo audio: {e}")
        return False

def main():
    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║     ASISTENTE DE CALIBRACIÓN DE AUDIO PARA J.A.R.V.I.S.   ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print("Vamos a encontrar exactamente cuál es tu micrófono y tus auriculares.\n")

    # 1. ENCONTRAR MICRÓFONO
    input_devices = []
    seen = set()
    for idx, d in enumerate(sd.query_devices()):
        if d.get("max_input_channels", 0) > 0 and d.get("hostapi") == 0:
            name = d.get("name", "")
            if name not in seen and not any(t in name.lower() for t in ["mezcla", "stereo mix"]):
                input_devices.append((idx, name))
                seen.add(name)

    print("--- PASO 1: DETECCIÓN DE MICRÓFONO ---")
    print("Vamos a probar cada uno durante 4 segundos. Habla cuando aparezca la barra.\n")

    best_input = None
    best_level = 0.0

    for idx, name in input_devices:
        lvl = test_microphone_meter(idx, name, duration=3.5)
        if lvl > best_level:
            best_level = lvl
            best_input = idx

    print("\n" + "="*50)
    if best_level > 0.005:
        dev_name = sd.query_devices(best_input)["name"]
        print(f"✓ ¡MICRÓFONO DETECTADO CON ÉXITO!")
        print(f"  Dispositivo: [{best_input}] {dev_name} (Nivel pico: {best_level:.4f})")
    else:
        print("⚠ Nivel muy bajo en todos los micrófonos. Usaremos el predeterminado de Windows.")
        best_input = sd.default.device[0]

    # 2. ENCONTRAR SALIDA (AURICULARES)
    print("\n--- PASO 2: DETECCIÓN DE AURICULARES / ALTAVOCES ---")
    output_devices = []
    seen_out = set()
    for idx, d in enumerate(sd.query_devices()):
        if d.get("max_output_channels", 0) > 0 and d.get("hostapi") == 0:
            name = d.get("name", "")
            if name not in seen_out:
                output_devices.append((idx, name))
                seen_out.add(name)

    print("Lista de salidas de audio detectadas:")
    for idx, name in output_devices:
        print(f"  [{idx}] {name}")

    selected_output = None
    for idx, name in output_devices:
        ans = input(f"\n¿Deseas probar el sonido en [{idx}] {name}? (s/n/omitir): ").strip().lower()
        if ans == "s":
            test_output_voice(idx, name)
            heard = input("¿Pudiste escuchar la voz claramente en tus auriculares? (s/n): ").strip().lower()
            if heard == "s":
                selected_output = idx
                print(f"✓ Auriculares confirmados: [{idx}] {name}")
                break
        elif ans == "omitir":
            break

    if selected_output is None:
        selected_output = sd.default.device[1]

    # Guardar en config.py
    config_path = os.path.join(os.path.dirname(__file__), "config.py")
    with open(config_path, "r", encoding="utf-8") as f:
        content = f.read()

    import re
    content = re.sub(r'MICROPHONE_INDEX\s*=\s*.*', f'MICROPHONE_INDEX = {best_input}', content)
    content = re.sub(r'OUTPUT_DEVICE_INDEX\s*=\s*.*', f'OUTPUT_DEVICE_INDEX = {selected_output}', content)

    with open(config_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("\n" + "="*50)
    print("✓ ¡CONFIGURACIÓN GUARDADA CON ÉXITO EN config.py!")
    print(f"  Micrófono guardado: [{best_input}] {sd.query_devices(best_input)['name']}")
    print(f"  Auriculares guardados: [{selected_output}] {sd.query_devices(selected_output)['name']}")
    print("="*50)
    print("\nAhora puedes iniciar JARVIS directamente sin tener que configurar nada más.")

if __name__ == "__main__":
    main()
