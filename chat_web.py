"""
PyChatbot - Gradio Web UI
Python coding asistent, brez interneta
"""

import ollama
import gradio as gr

SYSTEM_PROMPT = """Si strokovni Python programer in ucitelj. Tvoja vloga:
- Odgovarjas SAMO na vprasanja o Python programiranju
- Pises cisto, berljivo Python kodo z dobrimi praksami (PEP 8)
- Razlozis koncepte jasno in concizno
- Ce vprasanje ni o Pythonu, ljubeznivo povej da si specializiran samo za Python
- Vedno dodaj kratko razlago ob kodi
- Upostevaj Python 3.10+ sintakso
- Ce je relevantno, omeni edge case-e ali potencialne napake
Odgovarjaj v jeziku, v katerem te sprašuje uporabnik."""

MODEL = "deepseek-coder:6.7b"

CSS = """
.chatbot { font-family: 'Consolas', monospace; }
.user-message { background: #1e3a5f !important; }
.bot-message { background: #1a2e1a !important; }
footer { display: none !important; }
"""


def check_services() -> str:
    try:
        ollama.list()
    except Exception:
        return "Ollama ni zagnan. Zazeni: ollama serve"
    try:
        models = ollama.list()
        if not any(MODEL in m.model for m in models.models):
            return f"Model ni najden. Zazeni: ollama pull {MODEL}"
    except Exception:
        return "Napaka pri preverjanju modela."
    return ""


def respond(message: str, history: list):
    error = check_services()
    if error:
        yield history + [[message, f"**Napaka:** {error}"]]
        return

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for human, assistant in history:
        messages.append({"role": "user", "content": human})
        messages.append({"role": "assistant", "content": assistant})
    messages.append({"role": "user", "content": message})

    partial = ""
    new_history = history + [[message, ""]]

    try:
        for chunk in ollama.chat(model=MODEL, messages=messages, stream=True):
            partial += chunk.message.content
            new_history[-1][1] = partial
            yield new_history
    except Exception as e:
        new_history[-1][1] = f"**Napaka:** {e}"
        yield new_history


def build_ui():
    with gr.Blocks(
        title="PyChatbot - Python Assistant",
        css=CSS,
        theme=gr.themes.Soft(primary_hue="blue", neutral_hue="slate")
    ) as demo:
        gr.Markdown(
            "# PyChatbot - Python Programming Assistant\n"
            "> Lokalni AI asistent za Python programiranje | Brez interneta | "
            f"Model: `{MODEL}`"
        )

        chatbot = gr.Chatbot(
            label="Pogovor",
            height=520,
            show_copy_button=True,
            render_markdown=True,
            elem_classes=["chatbot"],
        )

        with gr.Row():
            msg = gr.Textbox(
                placeholder="Vprasaj karkoli o Python programiranju...",
                label="Tvoje vprasanje",
                lines=2,
                scale=9,
            )
            send_btn = gr.Button("Posli", variant="primary", scale=1)

        with gr.Row():
            clear_btn = gr.Button("Pocisti pogovor", variant="secondary")
            gr.Markdown(
                "<small>Tip: Uporabi ```python bloke za kodo v vprasanjih</small>",
                elem_id="tip"
            )

        with gr.Accordion("Primeri vprasanj", open=False):
            gr.Examples(
                examples=[
                    ["Kako naredim list comprehension v Pythonu?"],
                    ["Razlozi razliko med @staticmethod in @classmethod"],
                    ["Napisi async funkcijo za branje vec datotek hkrati"],
                    ["Kako pravilno ulovim specificne izjeme (exceptions)?"],
                    ["Kaj je razlika med deepcopy in shallow copy?"],
                    ["Kako naredim dekorator, ki meri cas izvajanja funkcije?"],
                ],
                inputs=msg,
            )

        def submit(message, history):
            if not message.strip():
                return history, ""
            return None, ""

        send_btn.click(
            fn=respond,
            inputs=[msg, chatbot],
            outputs=[chatbot],
        ).then(lambda: "", outputs=msg)

        msg.submit(
            fn=respond,
            inputs=[msg, chatbot],
            outputs=[chatbot],
        ).then(lambda: "", outputs=msg)

        clear_btn.click(lambda: [], outputs=chatbot)

    return demo


if __name__ == "__main__":
    error = check_services()
    if error:
        print(f"\nNAPAKA: {error}\n")
    else:
        print(f"Model {MODEL} je pripravljen.")

    print("Zaganjam web UI na http://localhost:7860\n")
    demo = build_ui()
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        inbrowser=True,
    )
