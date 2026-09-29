import os
import statistics

from dotenv import load_dotenv
from google import genai
from google.genai import types


# ============================================================
# CONFIGURAÇÃO
# ============================================================

load_dotenv()

MODEL = "gemini-3.1-flash-lite"

client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)


# ============================================================
# FERRAMENTAS
# ============================================================

def obter_temperatura_servidor(datacenter: str) -> dict:
    """Retorna a temperatura atual em graus Celsius de um datacenter (sp-01, rs-02 ou rj-03)."""

    tabela = {
        "sp-01": 24.5,
        "rs-02": 21.0,
        "rj-03": 27.8,
    }

    return {
        "datacenter": datacenter,
        "celsius": tabela[datacenter],
    }


def verificar_status_banco(cluster: str) -> dict:
    """Retorna o status operacional de um cluster de banco de dados (prod, homolog ou analytics)."""

    tabela = {
        "prod": "saudavel",
        "homolog": "degradado",
        "analytics": "offline",
    }

    return {
        "cluster": cluster,
        "status": tabela[cluster],
    }


def calcular_desvio_padrao(valores: list[float]) -> float:
    """Calcula o desvio padrao amostral de uma lista com pelo menos 2 numeros."""

    return round(statistics.stdev(valores), 2)


def validar_formato_documento(cnpj: str) -> dict:
    """Confere apenas o FORMATO de um CNPJ (14 digitos, com ou sem pontuacao); nao consulta a Receita."""

    cnpj_limpo = (
        cnpj
        .replace(".", "")
        .replace("/", "")
        .replace("-", "")
    )

    valido = (
        len(cnpj_limpo) == 14
        and cnpj_limpo.isdigit()
    )

    return {
        "cnpj": cnpj,
        "formato_valido": valido,
    }


# ============================================================
# REGISTRO DAS FERRAMENTAS
# ============================================================

FERRAMENTAS = {
    "obter_temperatura_servidor": obter_temperatura_servidor,
    "verificar_status_banco": verificar_status_banco,
    "calcular_desvio_padrao": calcular_desvio_padrao,
    "validar_formato_documento": validar_formato_documento,
}


# ============================================================
# RESPONDER
# ============================================================

def responder(pergunta: str) -> tuple[str, str | None]:

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
    # 2. Se nenhuma ferramenta foi chamada
    # --------------------------------------------------------

    if not response.function_calls:
        return response.text, None

    # Guarda o nome da primeira ferramenta chamada
    nome_primeira_ferramenta = response.function_calls[0].name

    # Adiciona a resposta do Gemini ao histórico
    contents.append(
        response.candidates[0].content
    )

    # --------------------------------------------------------
    # 3. Executa as ferramentas solicitadas
    # --------------------------------------------------------

    partes_resposta = []

    for chamada in response.function_calls:

        funcao = FERRAMENTAS[chamada.name]

        resultado = funcao(**chamada.args)

        partes_resposta.append(
            types.Part.from_function_response(
                name=chamada.name,
                response={
                    "result": resultado
                },
            )
        )

    # --------------------------------------------------------
    # 4. Envia os resultados das ferramentas ao Gemini
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

    return response.text, nome_primeira_ferramenta


# ============================================================
# BATERIA DE TESTES
# ============================================================

BATERIA = [
    (
        "Qual a temperatura do datacenter rs-02?",
        "obter_temperatura_servidor",
    ),
    (
        "O cluster analytics esta funcionando?",
        "verificar_status_banco",
    ),
    (
        "Qual o desvio padrao de 10, 12, 9, 15 e 11?",
        "calcular_desvio_padrao",
    ),
    (
        "O CNPJ 12.345.678/0001-95 tem formato valido?",
        "validar_formato_documento",
    ),
    (
        "Explique em duas frases o que e um cluster de banco de dados.",
        None,
    ),
    (
        "Para que serve o desvio padrao em monitoramento de servidores?",
        None,
    ),
]


# ============================================================
# EXECUÇÃO DOS TESTES
# ============================================================

if __name__ == "__main__":

    acertos = 0

    for pergunta, esperada in BATERIA:

        resposta, ferramenta = responder(pergunta)

        if ferramenta == esperada:
            acertos += 1

        print("=" * 70)
        print(f"Pergunta: {pergunta}")
        print(f"Ferramenta esperada: {esperada}")
        print(f"Ferramenta utilizada: {ferramenta}")
        print(f"Resposta: {resposta}")

    print("=" * 70)
    print(f"Roteamento correto: {acertos}/{len(BATERIA)}")