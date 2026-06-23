# PyChatbot Setup Script
# Namesti Ollama in potegne Python coding model

Write-Host "=== PyChatbot Setup ===" -ForegroundColor Cyan

# 1. Preveri ce Ollama ze obstaja
if (Get-Command ollama -ErrorAction SilentlyContinue) {
    Write-Host "[OK] Ollama je ze namesceN." -ForegroundColor Green
} else {
    Write-Host "[>>] Prenasam Ollama installer..." -ForegroundColor Yellow
    $installerUrl = "https://ollama.com/download/OllamaSetup.exe"
    $installerPath = "$env:TEMP\OllamaSetup.exe"
    Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath
    Write-Host "[>>] Namesceam Ollama (sledi navodilom)..." -ForegroundColor Yellow
    Start-Process -FilePath $installerPath -Wait
    Write-Host "[OK] Ollama namesceN." -ForegroundColor Green
}

# 2. Zagon Ollama service (ce ni ze zagnan)
Write-Host "[>>] Zaganjam Ollama service..." -ForegroundColor Yellow
Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# 3. Potegni model
Write-Host "[>>] Prenasam deepseek-coder:6.7b model (~3.8 GB)..." -ForegroundColor Yellow
Write-Host "     To lahko traja nekaj minut..." -ForegroundColor Gray
ollama pull deepseek-coder:6.7b

Write-Host ""
Write-Host "=== Setup zakljucen! ===" -ForegroundColor Green
Write-Host "Zazeni chatbot z:" -ForegroundColor Cyan
Write-Host "  Terminal:  python chat_terminal.py" -ForegroundColor White
Write-Host "  Web UI:    python chat_web.py" -ForegroundColor White
