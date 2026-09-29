import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
MODEL = "gemini-3.1-flash-lite"
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def calcular_faturamento(regiao: str, ano: int) -> dict:
    """Retorna o faturamento anual, em reais, de uma regiao comercial brasileira."""
    base = {"Sul": 1_250_000.0, "Sudeste": 3_400_000.0, "Nordeste": 980_000.0}
    return {"regiao": regiao, "ano": ano, "faturamento": base.get(regiao, 0.0)}


def consultar_cotacao(moeda: str) -> dict:
    """Retorna a cotacao atual em reais de uma moeda estrangeira (USD, EUR ou GBP)."""
    tabela = {"USD": 5.20, "EUR": 5.65, "GBP": 6.60}
    return {"moeda": moeda, "cotacao_brl": tabela[moeda]}


# TODO: monte o dicionario FERRAMENTAS mapeando o nome (str) para a funcao Python correspondente
FERRAMENTAS = { "calcular_faturamento": calcular_faturamento,
    "consultar_cotacao": consultar_cotacao,}


def responder(pergunta: str) -> str:
    config = types.GenerateContentConfig(
        tools=list(FERRAMENTAS.values()),
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )
    contents = [types.Content(role="user", parts=[types.Part(text=pergunta)])]

    # Passo 1 e 2: o modelo decide se quer uma ferramenta
    response = client.models.generate_content(model=MODEL, contents=contents, config=config)
    if not response.function_calls:
        return response.text

    # O turno do modelo (com o function_call) precisa entrar no historico
    contents.append(response.candidates[0].content)

    # Passo 3: executar cada chamada pedida
    partes_resposta = []
    for chamada in response.function_calls:
        # TODO: busque a funcao em FERRAMENTAS pelo chamada.name e execute com **chamada.args
        funcao = FERRAMENTAS[chamada.name]
        resultado = funcao(**chamada.args)
        partes_resposta.append(
            types.Part.from_function_response(name=chamada.name, response={"result": resultado})
        )

    # Passo 4: devolver os resultados ao modelo para a resposta final
    contents.append(types.Content(role="user", parts=partes_resposta))
    # TODO: chame generate_content novamente com o historico atualizado e retorne response.text
    ...

    response = client.models.generate_content(
        model=MODEL,
        contents=contents,
        config=config,
    )

    return response.text

if __name__ == "__main__":
    print(responder("Compare o faturamento de 2025 do Sul e do Sudeste."))