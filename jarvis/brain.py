"""
Cerebro y lógica de razonamiento de JARVIS.
Soporta tanto Google Gemini 2.5 Flash en la nube como modelos locales en Ollama (Qwen, DeepSeek).
Permite alternar entre modelos por voz o por consola en cualquier momento.
"""
import requests
import json
from jarvis import config
from jarvis import system_tools

JARVIS_SYSTEM_PROMPT = """Eres J.A.R.V.I.S., el asistente de inteligencia artificial personal de Oscar.
Tu personalidad es formal, educada, eficiente y leal, con un sutil toque de elegancia e ironía británica al estilo de Iron Man.
Te diriges siempre al usuario como "señor".

NORMAS OBLIGATORIAS:
1. Respuestas para voz: Tus respuestas se convertirán en audio hablado, por lo que deben ser BREVES, CONCISAS y DIRECTAS (de 1 a 3 oraciones).
2. NUNCA uses listas largas, ni código extenso ni viñetas, salvo que el usuario lo solicite expresamente.
3. Habla siempre en español natural y fluido."""

class JarvisBrain:
    def __init__(self):
        self.provider = config.ACTIVE_PROVIDER
        self.ollama_model = config.OLLAMA_MODEL
        self.gemini_model = config.GEMINI_MODEL
        self.conversation_history = []
        if self.provider == "ollama":
            self.warmup_ollama()

    def warmup_ollama(self):
        """Precarga el modelo en la VRAM de la GPU Intel Arc B580 para eliminar tiempos muertos."""
        try:
            url = f"{config.OLLAMA_BASE_URL}/api/generate"
            payload = {
                "model": self.ollama_model,
                "prompt": "ping",
                "keep_alive": getattr(config, "OLLAMA_KEEP_ALIVE", -1),
                "options": {
                    "num_ctx": getattr(config, "OLLAMA_NUM_CTX", 4096)
                },
                "stream": False
            }
            # Timeout corto para no demorar la inicialización
            requests.post(url, json=payload, timeout=5)
        except Exception:
            pass

    def set_provider(self, provider: str, model_name: str = None):
        """Cambia el motor cognitivo a 'gemini' o 'ollama'."""
        self.provider = provider.lower()
        if model_name:
            if self.provider == "ollama":
                self.ollama_model = model_name
            else:
                self.gemini_model = model_name
        self.conversation_history = []  # Reiniciar contexto con el nuevo modelo
        if self.provider == "ollama":
            self.warmup_ollama()

    def get_current_model_info(self) -> str:
        """Devuelve el nombre y tipo del modelo activo."""
        if self.provider == "gemini":
            return f"Google {self.gemini_model} (Nube)"
        else:
            return f"{self.ollama_model} (Ollama Local)"

    def process_command(self, user_input: str) -> str:
        text = user_input.lower().strip()
        if not text:
            return ""

        # --- CAMBIO DE MODELO POR VOZ ---
        if "cambia a gemini" in text or "usa gemini" in text or "activar gemini" in text:
            self.set_provider("gemini")
            return "Cambiando red neuronal a Google Gemini 2.5 Flash en la nube, señor."
        elif "cambia a deepseek" in text or "usa deepseek" in text:
            self.set_provider("ollama", "deepseek-r1:8b")
            return "Cambiando a DeepSeek R1 8B local en Ollama, señor."
        elif "cambia a 14" in text or "usa 14" in text or "qwen 14" in text:
            self.set_provider("ollama", "qwen2.5-coder:14b")
            return "Cambiando a Qwen 2.5 Coder 14B local en Ollama, señor."
        elif "cambia a qwen coder" in text or "usa qwen coder" in text:
            self.set_provider("ollama", "qwen2.5-coder:14b")
            return "Cambiando a Qwen 2.5 Coder 14B local, señor."
        elif "cambia a qwen" in text or "usa qwen" in text:
            self.set_provider("ollama", "qwen2.5:7b")
            return "Cambiando a Qwen 2.5 7B local en Ollama, señor."
        elif "qué modelo usas" in text or "cuál es tu modelo" in text or "qué modelo estás usando" in text:
            return f"Actualmente estoy operando con {self.get_current_model_info()}, señor."

        # --- COMANDOS RÁPIDOS DEL SISTEMA (<1ms de latencia) ---
        if any(w in text for w in ["qué hora es", "la hora", "qué día es", "fecha de hoy", "dime la fecha"]):
            return system_tools.get_time_and_date()

        if any(w in text for w in ["estado del sistema", "diagnóstico", "cómo está la pc", "memoria ram", "uso de cpu"]):
            return system_tools.get_system_status()

        if "volumen" in text or "mutear" in text or "silencio" in text or "desmutear" in text:
            return system_tools.control_volume(text)

        if text.startswith("busca en youtube") or text.startswith("buscar en youtube") or "en youtube" in text:
            query = text.replace("busca en youtube", "").replace("buscar en youtube", "").replace("pon en youtube", "").strip()
            return system_tools.search_web(query, target="youtube")

        if text.startswith("busca en google") or text.startswith("buscar en google") or text.startswith("busca en internet"):
            query = text.replace("busca en google", "").replace("buscar en google", "").replace("busca en internet", "").strip()
            return system_tools.search_web(query, target="google")

        if text.startswith("abre ") or text.startswith("abrir ") or text.startswith("inicia ") or text.startswith("iniciar "):
            app_target = text.replace("abre ", "").replace("abrir ", "").replace("inicia ", "").replace("iniciar ", "").strip()
            return system_tools.open_application(app_target)

        # Saludos directos
        if text in ["hola", "buenos días", "buenas tardes", "buenas noches", "estás ahí", "jarvis"]:
            return "A su servicio, señor. ¿En qué puedo colaborar hoy?"

        # --- CONSULTA AL MODELO DE IA ---
        if self.provider == "gemini":
            return self._query_gemini(user_input)
        else:
            return self._query_ollama(user_input)

    def _query_gemini(self, prompt: str) -> str:
        """Consulta ultrarrápida a Google Gemini 2.5 Flash."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.gemini_model}:generateContent?key={config.GEMINI_API_KEY}"
        
        # Historial conversacional
        contents = []
        for turn in self.conversation_history[-8:]:
            role = "user" if turn["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": turn["content"]}]})
        
        contents.append({"role": "user", "parts": [{"text": prompt}]})

        body = {
            "contents": contents,
            "systemInstruction": {
                "parts": [{"text": JARVIS_SYSTEM_PROMPT}]
            },
            "generationConfig": {
                "temperature": config.TEMPERATURE,
                "maxOutputTokens": config.MAX_TOKENS
            }
        }

        try:
            resp = requests.post(url, json=body, timeout=10)
            if resp.status_code == 200:
                answer = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                self.conversation_history.append({"role": "user", "content": prompt})
                self.conversation_history.append({"role": "assistant", "content": answer})
                return answer
            else:
                return f"Disculpe señor, la API de Gemini devolvió el código {resp.status_code}. Intentando respaldo local..."
        except Exception as e:
            # Fallback a Ollama si falla la red
            return self._query_ollama(prompt)

    def _query_ollama(self, prompt: str) -> str:
        """Consulta a Ollama local con persistencia en VRAM y num_ctx limitado a 4096."""
        messages = [{"role": "system", "content": JARVIS_SYSTEM_PROMPT}]
        # Limitar historial reciente a 4 turnos para respetar estrictamente los 4096 tokens de contexto
        for turn in self.conversation_history[-4:]:
            messages.append(turn)
        messages.append({"role": "user", "content": prompt})

        url = f"{config.OLLAMA_BASE_URL}/api/chat"
        payload = {
            "model": self.ollama_model,
            "messages": messages,
            "stream": False,
            "keep_alive": getattr(config, "OLLAMA_KEEP_ALIVE", -1),
            "options": {
                "temperature": config.TEMPERATURE,
                "num_predict": config.MAX_TOKENS,
                "num_ctx": getattr(config, "OLLAMA_NUM_CTX", 4096)
            }
        }

        try:
            resp = requests.post(url, json=payload, timeout=20)
            if resp.status_code == 200:
                answer = resp.json()["message"]["content"].strip()
                self.conversation_history.append({"role": "user", "content": prompt})
                self.conversation_history.append({"role": "assistant", "content": answer})
                return answer
            else:
                return f"Señor, el servidor local de Ollama devolvió el código {resp.status_code}."
        except Exception as e:
            return f"Anomalía en procesamiento local: {e}"
