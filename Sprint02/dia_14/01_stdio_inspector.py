import json
import subprocess
import sys

proc = subprocess.Popen(
    [sys.executable, "server_demo.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.DEVNULL,
    text=True,
    bufsize=1,
)


def enviar(mensagem: dict) -> None:
    # TODO: escreva json.dumps(mensagem) + "\n" em proc.stdin e faca flush()
    ...
    proc.stdin.write(json.dumps(mensagem) + "\n")
    proc.stdin.flush()

def receber() -> dict:
    # TODO: leia UMA linha de proc.stdout e converta com json.loads
    ...
    linha = proc.stdout.readline()
    return json.loads(linha)    

# 1) Handshake: o cliente se apresenta
enviar({
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2025-06-18",
        "capabilities": {},
        "clientInfo": {"name": "inspetor-manual", "version": "0.1"},
    },
})
resposta = receber()
print("SERVIDOR SE APRESENTOU COMO:", resposta["result"]["serverInfo"])

# 2) Notificacao (nao tem "id" e nao recebe resposta)
enviar({"jsonrpc": "2.0", "method": "notifications/initialized"})

# 3) Descoberta de ferramentas
# TODO: envie um envelope com id=2 e method "tools/list"; imprima os nomes das ferramentas em result["tools"]
enviar({
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
})

resposta = receber()

print(
    "FERRAMENTAS:",
    [tool["name"] for tool in resposta["result"]["tools"]]
)
# 4) Execucao de uma ferramenta
# TODO: envie id=3, method "tools/call", params {"name": "somar", "arguments": {"a": 2, "b": 3}}
#       e imprima o texto em result["content"][0]["text"]

enviar({
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
        "name": "somar",
        "arguments": {
            "a": 2,
            "b": 3
        }
    },
})

resposta = receber()

print(
    "RESULTADO:",
    resposta["result"]["content"][0]["text"]
)


proc.terminate()