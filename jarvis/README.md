# J.A.R.V.I.S. - Asistente de Voz Inteligente

Asistente de inteligencia artificial personal con reconocimiento de voz en tiempo real, síntesis de voz neuronal en español y control del sistema Windows, conectado a modelos locales con **Ollama** (`qwen2.5:7b`) y herramientas del sistema.

---

## 🚀 Cómo Iniciar

Puedes iniciarlo de dos formas:

1. **Desde tu Escritorio:** Haz doble clic en el acceso directo **`Iniciar_JARVIS.bat`**.
2. **Desde la Terminal:**
   ```powershell
   cd d:\GitOscarMonzonIA\frig-zone-web
   python -m jarvis.jarvis
   ```

---

## 🎙️ Modos de Uso

Al iniciar, JARVIS te permitirá elegir el modo de interacción:

1. **Modo 1 - Manos Libres (Wake-Word continuo):**
   - JARVIS escucha en segundo plano.
   - Actívalo diciendo: **"Jarvis"** o **"Oye Jarvis"** seguido de tu orden.
   - *Ejemplo:* `"Jarvis, qué hora es"`, `"Jarvis, abre la calculadora"`, `"Jarvis, busca en YouTube música relajante"`.
2. **Modo 2 - Push-to-Talk:**
   - Presiona `ENTER` en la consola cada vez que quieras hablarle al micrófono. Ideal para ambientes ruidosos.
3. **Modo 3 - Modo Texto:**
   - Escribe directamente tus mensajes en el teclado si no quieres usar el micrófono.

---

## ⚡ Comandos del Sistema Integrados

| Comando por Voz | Acción Realizada |
| :--- | :--- |
| *"Jarvis, qué hora es"* / *"fecha de hoy"* | Indica la hora y el día actual |
| *"Jarvis, estado del sistema"* / *"diagnóstico"* | Monitorea uso de CPU, memoria RAM y espacio en disco |
| *"Jarvis, abre [Chrome / Spotify / Calculadora / Bloc de notas / VS Code]"* | Inicia la aplicación seleccionada |
| *"Jarvis, busca en YouTube [canción o video]"* | Abre el navegador con la búsqueda en YouTube |
| *"Jarvis, busca en Google [tema]"* | Realiza la búsqueda en Google |
| *"Jarvis, sube / baja / silencia el volumen"* | Control de audio del sistema Windows |
| *"Jarvis, apágate"* / *"adiós"* | Cierra el asistente de forma segura |
| *Cualquier pregunta general o de programación* | Razona y responde usando **Qwen 2.5 7B** en Ollama |

---

## ⚙️ Personalización (`jarvis/config.py`)

Puedes editar el archivo [`config.py`](file:///d:/GitOscarMonzonIA/frig-zone-web/jarvis/config.py) para ajustar:
- **Modelo de IA:** Cambiar entre `qwen2.5-coder:14b` (por defecto en Ollama), `gemini-2.5-flash` (Google en la nube), o `deepseek-r1:8b`.
- **Dispositivos de Audio:** Detección automática por nombre para tu parlante Alexa Echo Dot y tu micrófono de auriculares.
- **Motor de Voz:** `gtts` (voz natural con entonación directa al parlante) o `sapi5` (voz Helena de Windows 100% offline).
- **Palabras de activación:** Agregar apodos o palabras clave personalizadas.
