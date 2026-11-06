import sounddevice as sd

print("=== DISPOSITIVOS DETECTADOS ===")
for i, d in enumerate(sd.query_devices()):
    name = d['name']
    in_ch = d['max_input_channels']
    out_ch = d['max_output_channels']
    api = d['hostapi']
    print(f"[{i:02d}] (API {api}) {name:40s} | In: {in_ch} | Out: {out_ch}")

print("\nDefault In:", sd.default.device[0])
print("Default Out:", sd.default.device[1])
