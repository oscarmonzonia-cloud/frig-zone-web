"""
J.A.R.V.I.S. - Just A Rather Very Intelligent System
Punto de entrada principal con interfaz HUD en consola y control por voz en tiempo real.
Conectado a Google Gemini 2.5 Flash en la nube y modelos locales en Ollama.
Audio configurado con micrófono de auriculares y salida al parlante Echo Dot de Alexa.
"""
import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich import box

from jarvis import config
from jarvis.tts_engine import TTSEngine, get_real_output_devices
from jarvis.stt_engine import STTEngine, get_real_microphones
from jarvis.brain import JarvisBrain

console = Console()

def render_banner(stt_engine: STTEngine, tts_engine: TTSEngine, brain: JarvisBrain):
    """Muestra el panel de inicio futurista de JARVIS."""
    console.clear()
    title = Text()
    title.append("  ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗\n", style="bold cyan")
    title.append("  ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝\n", style="bold cyan")
    title.append("  ██║███████║██████╔╝██║   ██║██║███████╗\n", style="bold blue")
    title.append("████║██╔══██╗██╔══██╗╚██╗ ██╔╝██║╚════██║\n", style="bold blue")
    title.append("╚███╔██║  ██║██║  ██║ ╚████╔╝ ██║███████║\n", style="bold bright_blue")
    title.append(" ╚══╝╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝\n", style="bold bright_blue")
    title.append("  [ STARK INDUSTRIES - PROTOCOLO DE ASISTENCIA PERSONAL ]\n", style="dim italic cyan")

    panel = Panel(
        title,
        border_style="cyan",
        box=box.DOUBLE_EDGE,
        padding=(1, 2)
    )
    console.print(panel)

    table = Table(box=box.ROUNDED, border_style="dim blue", show_header=False)
    table.add_column("Propiedad", style="cyan")
    table.add_column("Estado", style="bold white")

    table.add_row("Modelo de IA", brain.get_current_model_info())
    table.add_row("Altavoz (Salida de Voz)", tts_engine.get_output_device_name())
    table.add_row("Micrófono (Entrada)", stt_engine.get_device_name())
    table.add_row("Sensibilidad", f"Umbral {config.ENERGY_THRESHOLD} (Ultra sensible)")
    
    console.print(table)
    console.print()

def select_model_interactive(brain: JarvisBrain):
    """Permite cambiar de modelo cognitivo interactivamente."""
    console.print("\n[bold yellow]═══ SELECCIÓN DE MODELO DE INTELIGENCIA ARTIFICIAL ═══[/bold yellow]")
    console.print("  [bold cyan][1][/bold cyan] Google Gemini 2.5 Flash (Nube: ultrarrápido y potente)")
    console.print("  [bold cyan][2][/bold cyan] Qwen 2.5 Coder 14B (Local: máxima potencia y código en Ollama)")
    console.print("  [bold cyan][3][/bold cyan] DeepSeek R1 8B (Local: razonamiento avanzado en Ollama)")
    console.print("  [bold cyan][4][/bold cyan] Qwen 2.5 Coder 7B (Local: ágil y ligero)")
    console.print("  [bold cyan][5][/bold cyan] Qwen 2.5 7B (Local: conversación general)")
    
    val = input("\nElija el modelo deseado [1-5]: ").strip()
    if val == "1":
        brain.set_provider("gemini")
    elif val == "2":
        brain.set_provider("ollama", "qwen2.5-coder:14b")
    elif val == "3":
        brain.set_provider("ollama", "deepseek-r1:8b")
    elif val == "4":
        brain.set_provider("ollama", "qwen2.5-coder:7b")
    elif val == "5":
        brain.set_provider("ollama", "qwen2.5:7b")

def contains_wake_word(text: str) -> bool:
    if not text:
        return False
    lower = text.lower()
    return any(w in lower for w in config.WAKE_WORDS)

def clean_wake_word(text: str) -> str:
    lower = text.lower()
    for w in config.WAKE_WORDS:
        if lower.startswith(w):
            return text[len(w):].strip(",. ")
        lower = lower.replace(w, "")
    return text.strip(",. ")

def run_jarvis():
    tts = TTSEngine(output_device=config.OUTPUT_DEVICE_INDEX)
    stt = STTEngine(device_index=config.MICROPHONE_INDEX)
    brain = JarvisBrain()

    render_banner(stt, tts, brain)

    console.print("[dim cyan]Calibrando micrófono de auriculares...[/dim cyan]")
    stt.calibrate()
    console.print("[bold green]✓ Todos los subsistemas en línea.[/bold green]\n")
    
    greeting = "Sistemas en línea, señor. Jarvis conectado a sus parlantes Alexa y listo para escuchar."
    console.print(f"[bold cyan]JARVIS:[/bold cyan] {greeting}")
    tts.speak(greeting)

    console.print("\n[bold yellow]Opciones de inicio:[/bold yellow]")
    console.print("  [bold cyan]1[/bold cyan] - Modo Manos Libres (Escucha continua automática)")
    console.print("  [bold cyan]2[/bold cyan] - Modo Push-to-Talk (Presione [bold]ENTER[/bold] para hablar)")
    console.print("  [bold cyan]3[/bold cyan] - Modo Teclado (Escribir en consola)")
    console.print("  [bold magenta]L[/bold magenta] - Cambiar Modelo de IA (Gemini / Ollama)")

    choice = input("\nOpción [1/2/3/L] (por defecto 1): ").strip().upper()
    if choice == "L":
        select_model_interactive(brain)
        render_banner(stt, tts, brain)
        choice = "1"

    mode = "ptt" if choice == "2" else ("text" if choice == "3" else "wake")

    console.print(f"\n[bold green]► SISTEMA ACTIVO: MODO {mode.upper()}[/bold green]")
    if mode == "wake":
        console.print("[bold cyan]● Háblele a Jarvis por el micrófono de su auricular.[/bold cyan]")
        console.print("[dim italic](Su voz saldrá respondida por el Echo Dot de Alexa).[/dim italic]\n")
    elif mode == "ptt":
        console.print("[dim]Presione ENTER cada vez que desee hablarle.[/dim]\n")
    else:
        console.print("[dim]Escriba su mensaje y presione ENTER para enviar.[/dim]\n")

    while True:
        try:
            user_text = None

            if mode == "wake":
                console.print("[dim cyan]● Escuchando micrófono...[/dim cyan]", end="\r")
                raw_text, status = stt.listen(timeout=config.STT_TIMEOUT, phrase_time_limit=config.STT_PHRASE_TIME_LIMIT)
                
                if status == "NO_SPEECH":
                    console.print("[dim yellow]● Sonido detectado en micrófono[/dim yellow]", end="\r")
                    continue
                elif status == "TIMEOUT" or not raw_text:
                    continue

                console.print(f"\n[bold green]● Audio captado:[/bold green] \"{raw_text}\"")

                # Limpiar palabra de activación si la dijo
                command = clean_wake_word(raw_text) if contains_wake_word(raw_text) else raw_text

                if not command or len(command) < 2:
                    prompt_resp = "A su servicio, señor. ¿Qué desea?"
                    console.print(f"[bold cyan]JARVIS:[/bold cyan] {prompt_resp}")
                    tts.speak(prompt_resp)
                    
                    stt.play_sound_alert("listen")
                    console.print("[bold cyan]● Escuchando su instrucción...[/bold cyan]")
                    command, _ = stt.listen(timeout=config.STT_TIMEOUT, phrase_time_limit=config.STT_PHRASE_TIME_LIMIT)
                    if not command:
                        continue

                user_text = command

            elif mode == "ptt":
                input("\n[Presione ENTER para hablar...]")
                stt.play_sound_alert("listen")
                console.print("[bold cyan]● Grabando micrófono... Hable ahora.[/bold cyan]")
                raw_text, status = stt.listen(timeout=config.STT_TIMEOUT, phrase_time_limit=config.STT_PHRASE_TIME_LIMIT)
                
                if not raw_text:
                    if status == "NO_SPEECH":
                        console.print("[dim yellow]● Se detectó sonido pero no palabras claras.[/dim yellow]")
                    else:
                        console.print("[dim yellow]● No se detectó audio en el micrófono.[/dim yellow]")
                    continue

                console.print(f"[bold green]Usuario:[/bold green] {raw_text}")
                user_text = raw_text

            elif mode == "text":
                user_text = input("\nOscar > ").strip()
                if not user_text:
                    continue

            # Comandos de salida
            if any(term in user_text.lower() for term in ["apágate", "cerrar jarvis", "adiós jarvis", "salir", "desactivar"]):
                farewell = "Desactivando protocolos de voz. Que tenga un buen día, señor."
                console.print(f"\n[bold cyan]JARVIS:[/bold cyan] {farewell}")
                tts.speak(farewell)
                break

            # Procesar el comando con el modelo activo
            stt.play_sound_alert("processing")
            console.print(f"[bold yellow]⚡ Procesando con {brain.get_current_model_info()}...[/bold yellow]")
            response = brain.process_command(user_text)

            console.print(f"\n[bold cyan]JARVIS:[/bold cyan] {response}\n")
            tts.speak(response)

        except KeyboardInterrupt:
            console.print("\n[bold yellow]Interrupción manual detectada. Hasta luego, señor.[/bold yellow]")
            break
        except Exception as e:
            console.print(f"[bold red][!] Error en ciclo principal: {e}[/bold red]")
            time.sleep(1)

if __name__ == "__main__":
    run_jarvis()
