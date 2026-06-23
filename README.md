# PyChatbot - Python Programming Assistant

Lokalni AI chatbot za Python programiranje. Deluje **brez interneta**.

## Zahteve
- Windows 10/11
- Python 3.10+
- 32 GB RAM (priporoceno)
- ~4 GB prostora na disku za model

## Namestitev

### 1. Namesci Ollama
```powershell
.\setup.ps1
```
Ali roci: prenesi z https://ollama.com/download in zazeni:
```
ollama pull deepseek-coder:6.7b
```

### 2. Namesci Python odvisnosti
```
pip install -r requirements.txt
```

## Zagon

### Terminal vmesnik
```
python chat_terminal.py
```

### Web UI (odpre se v brskalniku)
```
python chat_web.py
```

## Ukazi v terminalu
- `clear` / `novo` / `reset` — pocisti pogovor
- `exit` / `quit` / `izhod` — zapri

## Model
Privzeto: `deepseek-coder:6.7b` (~3.8 GB)

Alternativa za se boljse rezultate (potrebuje vec RAM):
```
ollama pull deepseek-coder:33b
```
Zamenjaj `MODEL = "deepseek-coder:33b"` v obeh Python datotekah.
