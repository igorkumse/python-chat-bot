"""
PyChatbot - Terminal vmesnik
Python coding asistent, brez interneta
"""

import ollama
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.theme import Theme

SYSTEM_PROMPT = """Si strokovni Python programer in ucitelj. Tvoja vloga:
- Odgovarjas SAMO na vprasanja o Python programiranju
- Pises cistо, berljivo Python kodo z dobrimi praksami (PEP 8)
- Razlagaš koncepte jasno in concizno
- Ce vprasanje ni o Pythonu, ljubeznivo povej da si specializiran samo za Python
- Vedno dodaj kratko razlago ob kodi
- Upostevaj Python 3.10+ sintakso
- Ce je relevantno, omeni edge case-e ali potencialne napake
Odgovarjaj v jeziku, v katerem te sprašuje uporabnik."""

MODEL = "deepseek-coder:6.7b"

custom_theme = Theme({
    "user": "bold cyan",
    "assistant": "bold green",
    "info": "dim white",
    "error": "bold red",
})

console = Console(theme=custom_theme)


def check_ollama() -> bool:
    try:
        ollama.list()
        return True
    except Exception:
        return False


def check_model() -> bool:
    try:
        models = ollama.list()
        return any(MODEL in m.model for m in models.models)
    except Exception:
        return False


def chat_stream(messages: list) -> str:
    full_response = ""
    console.print("\n[assistant]Asistent:[/assistant] ", end="")

    with console.status("", spinner="dots"):
        stream = ollama.chat(
            model=MODEL,
            messages=messages,
            stream=True,
        )

    # Print streaming response
    console.print()
    for chunk in ollama.chat(model=MODEL, messages=messages, stream=True):
        content = chunk.message.content
        full_response += content

    # Render as markdown
    console.print(Markdown(full_response))
    return full_response


def main():
    console.print(Panel.fit(
        "[bold cyan]PyChatbot[/bold cyan] - Python Programming Assistant\n"
        "[dim]Lokalni AI asistent za Python, brez interneta[/dim]\n\n"
        "[dim]Ukazi: 'exit' ali 'quit' za izhod | 'clear' za nov pogovor[/dim]",
        border_style="cyan"
    ))

    if not check_ollama():
        console.print("[error]Ollama ni zagnan! Zazeni: ollama serve[/error]")
        return

    if not check_model():
        console.print(f"[error]Model {MODEL} ni najden![/error]")
        console.print(f"[info]Zazeni: ollama pull {MODEL}[/info]")
        return

    console.print(f"[info]Model: {MODEL} | Tip 'exit' za izhod[/info]\n")

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    while True:
        try:
            user_input = Prompt.ask("[user]Ti[/user]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[info]Nasvidenje![/info]")
            break

        if not user_input.strip():
            continue

        if user_input.lower() in ("exit", "quit", "izhod"):
            console.print("[info]Nasvidenje![/info]")
            break

        if user_input.lower() in ("clear", "novo", "reset"):
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            console.clear()
            console.print("[info]Pogovor je bil pociscen.[/info]\n")
            continue

        messages.append({"role": "user", "content": user_input})

        try:
            full_response = ""
            first_chunk = True
            console.print()

            for chunk in ollama.chat(model=MODEL, messages=messages, stream=True):
                content = chunk.message.content
                full_response += content
                if first_chunk:
                    console.print("[assistant]Asistent:[/assistant]")
                    first_chunk = False

            console.print(Markdown(full_response))
            console.print()
            messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            console.print(f"[error]Napaka: {e}[/error]")
            messages.pop()


if __name__ == "__main__":
    main()
