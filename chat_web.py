"""
PyChatbot - Web UI
Python coding asistent, brez interneta.
Uporablja vgrajeni http.server + Ollama REST API.
"""

import json
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.request import urlopen, Request
from urllib.error import URLError

OLLAMA_URL = "http://localhost:11434"
MODEL = "deepseek-coder:6.7b"

SYSTEM_PROMPT = """Si strokovni Python programer in učitelj. Tvoja vloga:
- Odgovarjaš SAMO na vprašanja o Python programiranju
- Pišeš čisto, berljivo Python kodo z dobrimi praksami (PEP 8)
- Razlagaš koncepte jasno in concizno
- Če vprašanje ni o Pythonu, ljubeznivo povej da si specializiran samo za Python
- Vedno dodaj kratko razlago ob kodi
- Upoštevaj Python 3.10+ sintakso
Odgovarjaj v jeziku, v katerem te sprašuje uporabnik."""

HTML = """<!DOCTYPE html>
<html lang="sl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PyChatbot - Python Assistant</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Segoe UI', sans-serif; background: #0d1117; color: #e6edf3; height: 100vh; display: flex; flex-direction: column; }
  header { background: #161b22; border-bottom: 1px solid #30363d; padding: 12px 20px; display: flex; align-items: center; gap: 12px; }
  header h1 { font-size: 1.1rem; color: #58a6ff; }
  header span { font-size: 0.8rem; color: #8b949e; background: #21262d; padding: 2px 8px; border-radius: 12px; }
  #chat { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 16px; }
  .msg { max-width: 85%; padding: 12px 16px; border-radius: 12px; line-height: 1.6; font-size: 0.95rem; }
  .user { background: #1f6feb; align-self: flex-end; border-radius: 12px 12px 2px 12px; }
  .bot  { background: #161b22; border: 1px solid #30363d; align-self: flex-start; border-radius: 12px 12px 12px 2px; }
  .bot pre { background: #0d1117; border: 1px solid #30363d; border-radius: 6px; padding: 10px; margin: 8px 0; overflow-x: auto; font-size: 0.88rem; }
  .bot code { font-family: 'Consolas', monospace; color: #79c0ff; }
  .bot pre code { color: #e6edf3; }
  .thinking { color: #8b949e; font-style: italic; }
  #input-area { background: #161b22; border-top: 1px solid #30363d; padding: 16px 20px; display: flex; gap: 10px; }
  #msg-input { flex: 1; background: #0d1117; border: 1px solid #30363d; border-radius: 8px; padding: 10px 14px; color: #e6edf3; font-size: 0.95rem; resize: none; outline: none; font-family: inherit; }
  #msg-input:focus { border-color: #58a6ff; }
  #send-btn { background: #238636; color: white; border: none; border-radius: 8px; padding: 10px 20px; cursor: pointer; font-size: 0.95rem; font-weight: 600; transition: background 0.2s; }
  #send-btn:hover { background: #2ea043; }
  #send-btn:disabled { background: #21262d; color: #8b949e; cursor: default; }
  #clear-btn { background: #21262d; color: #8b949e; border: 1px solid #30363d; border-radius: 8px; padding: 10px 14px; cursor: pointer; font-size: 0.88rem; }
  #clear-btn:hover { background: #30363d; color: #e6edf3; }
  .welcome { text-align: center; color: #8b949e; margin: auto; }
  .welcome h2 { color: #58a6ff; margin-bottom: 8px; }
</style>
</head>
<body>
<header>
  <h1>🐍 PyChatbot</h1>
  <span>Python Programming Assistant</span>
  <span id="model-badge">Model: """ + MODEL + """</span>
  <span style="margin-left:auto; font-size:0.75rem;">localhost · brez interneta</span>
</header>
<div id="chat">
  <div class="welcome">
    <h2>Python Programming Assistant</h2>
    <p>Postavi vprašanje o Python programiranju...</p>
  </div>
</div>
<div id="input-area">
  <button id="clear-btn" onclick="clearChat()">Počisti</button>
  <textarea id="msg-input" rows="2" placeholder="Vpraši karkoli o Pythonu..." onkeydown="handleKey(event)"></textarea>
  <button id="send-btn" onclick="send()">Pošlji</button>
</div>
<script>
let history = [];

function escapeHtml(t) {
  return t.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function formatMsg(text) {
  // code blocks
  text = text.replace(/```(\\w*)\\n?([\\s\\S]*?)```/g, (_, lang, code) =>
    `<pre><code>${escapeHtml(code.trim())}</code></pre>`);
  // inline code
  text = text.replace(/`([^`]+)`/g, (_, c) => `<code>${escapeHtml(c)}</code>`);
  // bold
  text = text.replace(/\\*\\*(.+?)\\*\\*/g, '<strong>$1</strong>');
  // newlines
  text = text.replace(/\\n/g, '<br>');
  return text;
}

function addMsg(role, text) {
  const chat = document.getElementById('chat');
  const welcome = chat.querySelector('.welcome');
  if (welcome) welcome.remove();
  const div = document.createElement('div');
  div.className = 'msg ' + (role === 'user' ? 'user' : 'bot');
  div.innerHTML = role === 'user' ? escapeHtml(text) : formatMsg(text);
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
  return div;
}

async function send() {
  const input = document.getElementById('msg-input');
  const btn = document.getElementById('send-btn');
  const text = input.value.trim();
  if (!text) return;

  input.value = '';
  btn.disabled = true;
  addMsg('user', text);
  history.push({role: 'user', content: text});

  const botDiv = addMsg('bot', '<span class="thinking">Razmišljam...</span>');

  try {
    const resp = await fetch('/chat', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({history})
    });

    const reader = resp.body.getReader();
    const decoder = new TextDecoder();
    let full = '';
    botDiv.innerHTML = '';

    while (true) {
      const {done, value} = await reader.read();
      if (done) break;
      const chunk = decoder.decode(value);
      const lines = chunk.split('\\n').filter(l => l.startsWith('data: '));
      for (const line of lines) {
        try {
          const data = JSON.parse(line.slice(6));
          if (data.token) {
            full += data.token;
            botDiv.innerHTML = formatMsg(full);
            document.getElementById('chat').scrollTop = 9999;
          }
        } catch(e) {}
      }
    }
    history.push({role: 'assistant', content: full});
  } catch(e) {
    botDiv.innerHTML = '<span style="color:#f85149">Napaka: ' + e.message + '</span>';
  }
  btn.disabled = false;
  input.focus();
}

function handleKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); }
}

function clearChat() {
  history = [];
  const chat = document.getElementById('chat');
  chat.innerHTML = '<div class="welcome"><h2>Python Programming Assistant</h2><p>Postavi vprašanje o Python programiranju...</p></div>';
}
</script>
</body>
</html>"""


def ollama_check():
    try:
        urlopen(f"{OLLAMA_URL}/api/tags", timeout=3)
        return True
    except URLError:
        return False


class ChatHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # tihi log

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML.encode("utf-8"))

    def do_POST(self):
        if self.path != "/chat":
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers["Content-Length"])
        body = json.loads(self.rfile.read(length))
        history = body.get("history", [])

        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history

        payload = json.dumps({
            "model": MODEL,
            "messages": messages,
            "stream": True,
        }).encode("utf-8")

        req = Request(
            f"{OLLAMA_URL}/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()

        try:
            with urlopen(req) as resp:
                for line in resp:
                    data = json.loads(line.decode("utf-8"))
                    token = data.get("message", {}).get("content", "")
                    if token:
                        event = f"data: {json.dumps({'token': token})}\n\n"
                        self.wfile.write(event.encode("utf-8"))
                        self.wfile.flush()
        except Exception as e:
            err = f"data: {json.dumps({'token': f'Napaka: {e}'})}\n\n"
            self.wfile.write(err.encode("utf-8"))
            self.wfile.flush()


def main():
    print("=== PyChatbot Web UI ===")

    if not ollama_check():
        print("NAPAKA: Ollama ni dostopen. Zaženi: ollama serve")
        return

    print(f"Model: {MODEL}")

    port = 7860
    server = HTTPServer(("127.0.0.1", port), ChatHandler)
    url = f"http://localhost:{port}"
    print(f"Zaganjam na {url}")

    threading.Timer(1.0, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nUstavljen.")


if __name__ == "__main__":
    main()
