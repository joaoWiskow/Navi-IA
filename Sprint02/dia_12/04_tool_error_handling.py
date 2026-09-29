import os

from dotenv import load_dotenv
from google import genai
from google.genai import types


# ============================================================
# CONFIGURAÇÃO
# ============================================================

load_dotenv()

MODEL = "gemini-3.5-flash-lite"

client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)


# ============================================================
# FERRAMENTAS
# ============================================================

def dividir_metricas(numerador: float, denominador: float) -> dict:
    """Divide duas metricas e retorna a razao (por exemplo, erros por requisicao)."""

    return {
        "razao": numerador / denominador
    }


def consultar_servico_externo(servico: str) -> dict:
    """Consulta o status de um servico externo pelo nome."""

    raise ConnectionError(
        f"Servico '{servico}' temporariamente indisponivel"
    )


FERRAMENTAS = {
    "dividir_metricas": dividir_metricas,
    "consultar_servico_externo": consultar_servico_externo,
}


# ============================================================
# EXECUÇÃO SEGURA DAS FERRAMENTAS
# ============================================================

def executar_com_seguranca(nome: str, args: dict) -> dict:
    """Executa a ferramenta e transforma qualquer excecao em um resultado estruturado."""

    try:
        resultado = FERRAMENTAS[nome](**args)

        return {
            "status": "sucesso",
            "resultado": resultado,
        }

    except KeyError:
        return {
            "status": "falha",
            "error": f"Ferramenta desconhecida: {nome}",
        }

    except Exception as erro:
        return {
            "status": "falha",
            "error": str(erro),
        }


# ============================================================
# RESPONDER
# ============================================================

def responder(pergunta: str) -> str:

    config = types.GenerateContentConfig(
        tools=list(FERRAMENTAS.values()),
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            disable=True
        ),
    )

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part(text=pergunta)
            ],
        )
    ]

    # --------------------------------------------------------
    # 1. Primeira chamada ao Gemini
    # --------------------------------------------------------

    response = client.models.generate_content(
        model=MODEL,
        contents=contents,
        config=config,
    )

    # --------------------------------------------------------
    # 2. Caso o Gemini não utilize nenhuma ferramenta
    # --------------------------------------------------------

    if not response.function_calls:
        return response.text

    # Adiciona a resposta do Gemini ao histórico
    contents.append(
        response.candidates[0].content
    )

    # --------------------------------------------------------
    # 3. Executa as ferramentas com segurança
    # --------------------------------------------------------

    partes_resposta = []

    for chamada in response.function_calls:

        resultado = executar_com_seguranca(
            chamada.name,
            chamada.args,
        )

        partes_resposta.append(
            types.Part.from_function_response(
                name=chamada.name,
                response=resultado,
            )
        )

    # --------------------------------------------------------
    # 4. Envia os resultados para o Gemini
    # --------------------------------------------------------

    contents.append(
        types.Content(
            role="user",
            parts=partes_resposta,
        )
    )

    # --------------------------------------------------------
    # 5. Segunda chamada ao Gemini
    # --------------------------------------------------------

    response = client.models.generate_content(
        model=MODEL,
        contents=contents,
        config=config,
    )

    return response.text


# ============================================================
# PERGUNTAS
# ============================================================

PERGUNTAS = [
    "Qual a razao entre 50 erros e 0 requisicoes?",
    "O servico de pagamentos esta no ar?",
]


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":

    for pergunta in PERGUNTAS:

        print("=" * 70)
        print(f"Pergunta: {pergunta}")

        resposta = responder(pergunta)

        print(f"Resposta: {resposta}")