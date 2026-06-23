# PyChatbot - Python Programming Assistant

Lokalni AI chatbot za Python programiranje. Deluje **brez interneta**.

## Zahteve
- Windows 10/11 (ARM64 ali x64)
- Python 3.13+
- 16+ GB RAM (priporočeno 32 GB)
- ~4 GB prostora na disku za model

## Namestitev

### 1. Namesti Ollama
Prenesi in namesti z [ollama.com/download](https://ollama.com/download), nato potegni model:
```
ollama pull deepseek-coder:6.7b
```

### 2. Namesti Python odvisnosti
```
pip install -r requirements.txt
```

### 3. Zaženi Ollama service
```
ollama serve
```

### 4. Zaženi chatbot

**Web UI** (odpre se v brskalniku na localhost:7860):
```
python chat_web.py
```

**Terminal vmesnik:**
```
python chat_terminal.py
```

## Ukazi v terminalu
- `clear` / `novo` / `reset` — počisti pogovor
- `exit` / `quit` / `izhod` — zapri

## Model
Privzeto: `deepseek-coder:6.7b` (~3.8 GB)

Za še boljše rezultate (potrebuje več RAM):
```
ollama pull deepseek-coder:33b
```
Zamenjaj `MODEL = "deepseek-coder:33b"` v obeh Python datotekah.

---

## Posebnosti za Snapdragon X Elite (ARM64)

Pri razvoju na Snapdragon X Elite procesorju smo naleteli na naslednje težave in rešitve:

### Problem: Python paketi brez ARM64 wheel-ov

Python 3.13 na Windows ARM64 nima predhodno zgrajenih (`wheel`) paketov za mnoge knjižnice, ki zahtevajo C/C++ razširitve:

| Paket | Napaka | Rešitev |
|-------|--------|---------|
| `gradio` | Zahteva `brotli` — ni ARM64 wheel | Zamenjano z vgrajenim `http.server` |
| `streamlit` | Zahteva `httptools`, `pyarrow` — ni ARM64 wheel | Opuščeno |
| `brotli` | `Microsoft Visual C++ 14.0 required` | Ni na voljo brez Build Tools |
| `brotlicffi` | Enaka napaka | Ni na voljo |

**Vzrok:** Na Windows ARM64 manjka Microsoft C++ Build Tools (`cl.exe`, `nmake`), ki so potrebni za kompajliranje C razširitev iz izvorne kode.

### Rešitev: Vgrajeni Python HTTP server

Namesto Gradio/Streamlit smo napisali web UI z:
- `http.server` — vgrajen v Python, brez zunanjih odvisnosti
- Ollama REST API (`http://localhost:11434`) — čisti HTTP klici
- Vanilla HTML/CSS/JavaScript frontend — brez build korakov

Rezultat: **nič C razširitev**, dela na vsakem sistemu brez Build Tools.

### Ollama na ARM64

Ollama ima uradni Windows ARM64 installer in deluje nativno na Snapdragon X Elite — ni posebnih korakov. Model (`deepseek-coder:6.7b`) se izvaja na CPU; za GPU/NPU pohitritev bi bil potreben QNN backend, ki ga Ollama trenutno ne podpira.

### Priporočila za ARM64 razvoj

- Uporabljaj pakete, ki imajo **čiste Python** (`pure Python`) implementacije ali uradne ARM64 wheel-e
- Preden namestiš paket, preveri na [PyPI](https://pypi.org) ali ima `cp313-win_arm64` wheel
- Alternativa: namesti **Microsoft C++ Build Tools** (brezplačno), kar reši večino težav z izgradnjo wheel-ov
