import json
import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel

load_dotenv()

MODEL = "gemini-3.5-flash-lite"

client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)

REPETICOES = 10

TEXTO = (
    "Pedido 8841 do cliente Joao Lima, total R$ 259,90, "
    "pago via PIX em 27/09/2026."
)


class Pedido(BaseModel):
    numero: int
    cliente: str
    total: float
    forma_pagamento: str


def abordagem_livre() -> dict:
    """Pede JSON no prompt, sem schema formal."""

    inicio = time.perf_counter()

    response = client.models.generate_content(
        model=MODEL,
        contents=(
            f"Retorne apenas JSON com numero, cliente, "
            f"total e forma_pagamento: {TEXTO}"
        ),
    )

    texto = response.text

    tem_markdown = texto.strip().startswith("`" * 3)

    # TODO: tente json.loads(texto) e marque erro_parse=True se levantar json.JSONDecodeError
    # Retorne: {"erro_parse": bool, "tem_markdown": bool, "segundos": float}

    erro_parse = False

    try:
        json.loads(texto)
    except json.JSONDecodeError:
        erro_parse = True

    return {
        "erro_parse": erro_parse,
        "tem_markdown": tem_markdown,
        "segundos": time.perf_counter() - inicio,
    }


def abordagem_schema() -> dict:

    inicio = time.perf_counter()

    # TODO: chame o modelo com response_schema=Pedido e retorne o mesmo formato de dicionario

    response = client.models.generate_content(
        model=MODEL,
        contents=f"Extraia os dados do pedido abaixo: {TEXTO}",
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=Pedido,
        ),
    )

    pedido = response.parsed

    return {
        "erro_parse": False,
        "tem_markdown": False,
        "segundos": time.perf_counter() - inicio,
    }


def resumir(nome: str, resultados: list[dict]) -> None:

    erros = sum(r["erro_parse"] for r in resultados)

    markdown = sum(r["tem_markdown"] for r in resultados)

    tempo_medio = (
        sum(r["segundos"] for r in resultados)
        / len(resultados)
    )

    print(
        f"{nome}: "
        f"erros de parse={erros}/{len(resultados)} | "
        f"com markdown={markdown} | "
        f"media={tempo_medio:.2f}s"
    )


if __name__ == "__main__":

    livre = [
        abordagem_livre()
        for _ in range(REPETICOES)
    ]

    estruturada = [
        abordagem_schema()
        for _ in range(REPETICOES)
    ]

    resumir(
        "JSON livre ",
        livre
    )

    resumir(
        "response_schema",
        estruturada
    )