import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

MODEL = "gemini-3.1-flash-lite"

client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)


def calcular_faturamento(regiao: str, ano: int) -> dict:
    """Retorna o faturamento anual, em reais, de uma regiao comercial brasileira.

    Args:
        regiao: nome da regiao, por exemplo "Sul" ou "Nordeste".
        ano: ano de referencia com 4 digitos, por exemplo 2025.
    """

    base = {
        "Sul": 1_250_000.0,
        "Sudeste": 3_400_000.0,
        "Nordeste": 980_000.0
    }

    return {
        "regiao": regiao,
        "ano": ano,
        "faturamento": base.get(regiao, 0.0)
    }


def consultar_cotacao(moeda: str) -> float:
    """Retorna a cotacao atual em reais de uma moeda estrangeira (USD, EUR ou GBP)."""

    cotacoes = {
        "USD": 5.20,
        "EUR": 5.65,
        "GBP": 6.60
    }

    moeda = moeda.upper()

    if moeda not in cotacoes:
        raise ValueError(f"Moeda desconhecida: {moeda}")

    return cotacoes[moeda]


config = types.GenerateContentConfig(
    tools=[
        calcular_faturamento,
        consultar_cotacao
    ],

    # Queremos apenas visualizar o que o Gemini decidiu chamar.
    automatic_function_calling=types.AutomaticFunctionCallingConfig(
        disable=True
    ),
)


PERGUNTAS = [
    "Quanto a regiao Sul faturou em 2025?",
    "Quanto custa um dolar hoje em reais?",
    "O que e um JOIN em SQL?",
]


if __name__ == "__main__":

    for pergunta in PERGUNTAS:

        response = client.models.generate_content(
            model=MODEL,
            contents=pergunta,
            config=config
        )

        print("\nPERGUNTA:", pergunta)

        if response.function_calls:

            for chamada in response.function_calls:

                print("  função:", chamada.name)
                print("  argumentos:", chamada.args)

        else:

            print("  resposta em texto:", response.text)