"""
Simula un celular oyente desde la PC: inicia sesión, se conecta al WebSocket y
muestra (y dice en voz alta con la voz de Windows) cada pago que llegue.

Uso:
    python tools/oyente_pc.py                 # entra como lopez / clave123
    python tools/oyente_pc.py maria miclave   # otro usuario
"""
import asyncio
import json
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime

import websockets

SERVIDOR = "127.0.0.1:8000"


def login(username, password):
    req = urllib.request.Request(
        f"http://{SERVIDOR}/api/auth/login/",
        data=json.dumps({"username": username, "password": password}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())["token"]
    except urllib.error.HTTPError as e:
        sys.exit(f"No se pudo iniciar sesión: {e.read().decode()}")
    except urllib.error.URLError:
        sys.exit(f"El servidor no responde en {SERVIDOR}. ¿Está corriendo runserver?")


def emisores(token):
    req = urllib.request.Request(
        f"http://{SERVIDOR}/api/escucho/", headers={"Authorization": f"Token {token}"}
    )
    with urllib.request.urlopen(req) as r:
        return [e["username"] for e in json.loads(r.read())]


def hablar(texto):
    """Voz de Windows (System.Speech), sin instalar nada. No bloquea."""
    texto = texto.replace("'", "")
    subprocess.Popen(
        [
            "powershell", "-NoProfile", "-Command",
            "Add-Type -AssemblyName System.Speech; "
            f"(New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{texto}')",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


async def escuchar(username, token):
    url = f"ws://{SERVIDOR}/ws/pagos/?token={token}"
    while True:
        try:
            async with websockets.connect(url) as ws:
                print("Conectado. Esperando pagos... (Ctrl+C para salir)\n")
                async for raw in ws:
                    pago = json.loads(raw)
                    if pago.get("tipo") != "pago":
                        continue
                    hora = datetime.now().strftime("%H:%M:%S")
                    print(
                        f"[{hora}] 💰 {pago['emisor']} recibió S/ {pago['monto']} "
                        f"de {pago['remitente']}"
                    )
                    hablar(
                        f"A {pago['emisor']} le yapearon {pago['monto']} soles "
                        f"de {pago['remitente']}"
                    )
        except (OSError, websockets.ConnectionClosed) as e:
            print(f"Conexión perdida ({e}). Reintentando en 3 s...")
            await asyncio.sleep(3)


def main():
    username = sys.argv[1] if len(sys.argv) > 1 else "lopez"
    password = sys.argv[2] if len(sys.argv) > 2 else "clave123"
    token = login(username, password)
    lista = emisores(token)
    print(f"Sesión iniciada como '{username}'.")
    if lista:
        print(f"Escuchando los pagos de: {', '.join(lista)}")
    else:
        print("⚠ Nadie te agregó como oyente todavía: no llegará ningún pago.")
    try:
        asyncio.run(escuchar(username, token))
    except KeyboardInterrupt:
        print("\nAdiós.")


if __name__ == "__main__":
    main()
