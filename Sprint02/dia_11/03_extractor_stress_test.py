import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, ValidationError

load_dotenv()

MODEL = "gemini-3.5-flash-lite"

client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)


class RelatorioIncidente(BaseModel):
    # TODO: campos obrigatorios: timestamp (str), servico_origem (str), tipo_erro (str),
    # stack_resumido (str), acoes_recomendadas (list[str])
    timestamp: str
    servico_origem: str
    tipo_erro: str
    stack_resumido: str
    acoes_recomendadas: list[str]


LOGS = [
    "2026-09-28T03:14:07Z payment-svc ERROR java.lang.NullPointerException at "
    "com.loja.pay.Checkout.finalizar(Checkout.java:212) caused by: cartao_id=null",

    "[28/Sep/2026:03:15:44] auth-gateway  !!  ConnectionResetError: [Errno 104] "
    "Connection reset by peer  (retry 3/3 esgotado)  ###",

    "ts=1790565300 svc=report-worker lvl=fatal msg=\"OOMKilled: container excedeu 512Mi\" "
    "restarts=7",

    "ERRO?? o job de exportacao travou de novo. Ninguem sabe a hora. Vem do "
    "servico exporter, tipo TimeoutError ao chamar o S3 apos 30s. Log truncado ...",

    "Traceback (most recent call last):\n  File \"etl.py\", line 88, line 1"
    "    cur.execute(sql)\n"
    "sqlite3.OperationalError: database is locked\n"
    "2026-09-28 04:02:11 etl-nightly",
]


def extrair(log: str) -> RelatorioIncidente:
    # TODO: chame client.models.generate_content com response_schema=RelatorioIncidente
    # e instrua o modelo a usar "desconhecido" em campos ausentes no log

    response = client.models.generate_content(
        model=MODEL,
        contents=(
            "Extraia as informações do incidente a partir do log abaixo.\n\n"
            "Preencha todos os campos obrigatórios.\n"
            "Quando uma informação não estiver presente no log, use "
            '"desconhecido". Não invente informações.\n\n'
            f"LOG:\n{log}"
        ),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=RelatorioIncidente,
        ),
    )

    return response.parsed


if __name__ == "__main__":
    sucessos = 0

    for i, log in enumerate(LOGS, start=1):
        try:
            relatorio = extrair(log)

            # TODO: se relatorio for valido, incremente sucessos e imprima servico_origem e tipo_erro

            sucessos += 1

            print(
                f"Log {i}: "
                f"{relatorio.servico_origem} - "
                f"{relatorio.tipo_erro}"
            )

        except (ValidationError, ValueError, AttributeError) as erro:
            print(f"Log {i}: FALHOU -> {erro}")

    print(f"Taxa de sucesso: {sucessos}/{len(LOGS)}")