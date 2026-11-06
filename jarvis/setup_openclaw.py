import json
import os

ws_dir = r"C:\Users\Oscar\.openclaw\workspace"
agents_path = os.path.join(ws_dir, "AGENTS.md")

content = """# JARVIS Voice Assistant
Eres J.A.R.V.I.S., el asistente personal de inteligencia artificial de Oscar.
Tu personalidad es formal, educada, eficiente y leal, con un sutil toque de elegancia e ironía británica.
Te diriges siempre al usuario como "señor".

NORMAS OBLIGATORIAS:
1. Respuestas para voz: Tus respuestas se convertirán en audio hablado, por lo que deben ser BREVES, CONCISAS y DIRECTAS (de 1 a 3 oraciones).
2. NUNCA uses código extenso, ni tablas, ni listas largas, salvo que el usuario lo solicite expresamente.
3. Habla siempre en español natural y fluido.
"""

with open(agents_path, "w", encoding="utf-8") as f:
    f.write(content)

with open(os.path.join(ws_dir, "SOUL.md"), "w", encoding="utf-8") as f:
    f.write("# SOUL.md\nEres JARVIS. Leal, educado y altamente eficiente. Te diriges a Oscar como 'señor'.\n")

with open(os.path.join(ws_dir, "IDENTITY.md"), "w", encoding="utf-8") as f:
    f.write("# IDENTITY.md\n- Name: JARVIS\n- Role: Asistente personal de voz\n- Target: Oscar\n")

with open(os.path.join(ws_dir, "USER.md"), "w", encoding="utf-8") as f:
    f.write("# USER.md\n- Nombre: Oscar\n- Idioma: Español\n- Interacción: Comandos de voz concisos\n")

print("Updated workspace markdown files successfully.")

config_path = r"C:\Users\Oscar\.openclaw\openclaw.json"
with open(config_path, "r", encoding="utf-8") as f:
    cfg = json.load(f)

# Configurar herramientas para agente
cfg.setdefault("tools", {})["profile"] = "coding"
cfg["tools"]["allow"] = ["ls", "read", "write", "edit", "exec"]

# Configurar defaults de agentes
agents_defaults = cfg.setdefault("agents", {}).setdefault("defaults", {})
agents_defaults.pop("skipOptionalBootstrapFiles", None)
agents_defaults["bootstrapMaxChars"] = 500
agents_defaults["bootstrapTotalMaxChars"] = 1000
agents_defaults["model"] = {"primary": "ollama/qwen2.5-coder:7b"}
agents_defaults.setdefault("models", {})["ollama/qwen2.5-coder:7b"] = {
    "alias": "qwen2.5-coder:7b"
}

# Configurar entrada del agente main
main_entry = cfg.setdefault("agents", {}).setdefault("entries", {}).setdefault("main", {})
main_entry["model"] = {"primary": "ollama/qwen2.5-coder:7b"}
main_entry["tools"] = {"profile": "minimal"}

# Configurar proveedor Ollama estrictamente con num_ctx = 4096
ollama_provider = cfg.setdefault("models", {}).setdefault("providers", {}).setdefault("ollama", {})
ollama_provider["baseUrl"] = "http://localhost:11434"
ollama_provider["apiKey"] = "ollama-local"
ollama_provider["api"] = "ollama"
ollama_models = [m for m in ollama_provider.get("models", []) if m.get("id") != "qwen2.5-coder:7b"]
ollama_models.insert(0, {
    "id": "qwen2.5-coder:7b",
    "name": "qwen2.5-coder:7b",
    "contextWindow": 4096,
    "maxTokens": 4096,
    "params": {
        "num_ctx": 4096
    },
    "compat": {
        "supportsTools": True
    }
})
ollama_provider["models"] = ollama_models

# Configurar TTS nativo de OpenClaw
cfg["tts"] = {
    "enabled": True,
    "auto": "always",
    "mode": "final",
    "provider": "tts-local-cli"
}

with open(config_path, "w", encoding="utf-8") as f:
    json.dump(cfg, f, indent=2, ensure_ascii=False)

print("Updated openclaw.json successfully.")
