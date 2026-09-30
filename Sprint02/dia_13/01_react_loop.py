import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
MODEL = "gemini-3.1-flash-lite"
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

INSTRUCAO = (
    "Voce e um agente de dados. Use as ferramentas disponiveis, uma etapa por vez, "
    "e so responda ao usuario quando tiver todas as informacoes necessarias."
)


def rodar_agente(pergunta, ferramentas, max_iterations=5, antes_de_executar=None, ao_fim_do_turno=None):
    """Executa o loop ReAct e retorna (resposta_final, historico).

    ferramentas: dicionario {nome: funcao_python}
    antes_de_executar(nome, args): retorna None (seguir) ou um texto de aviso (nao executar)
    ao_fim_do_turno(turno, response, segundos): gancho de telemetria
    """
    config = types.GenerateContentConfig(
        system_instruction=INSTRUCAO,
        tools=list(ferramentas.values()),
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )
    historico = [types.Content(role="user", parts=[types.Part(text=pergunta)])]

    turno = 0
    while True:
        turno += 1
        # TODO: se turno > max_iterations, retorne ("Limite de iteracoes atingido sem resposta final.", historico)
        if turno > max_iterations:
            return ("Limite de iteracoes atingido sem resposta final.", historico)

        print(f"\n[Turno {turno}] {pergunta}")
        inicio = time.perf_counter()
        response = client.models.generate_content(model=MODEL, contents=historico, config=config)
        historico.append(response.candidates[0].content)

        # TODO: se NAO houver response.function_calls, chame ao_fim_do_turno (se existir) e retorne (response.text, historico)
        if not response.function_calls:
            if ao_fim_do_turno:
                ao_fim_do_turno(turno, response, time.perf_counter() - inicio)
            return (response.text, historico)

        partes = []
        for chamada in response.function_calls:
            args = dict(chamada.args)
            aviso = antes_de_executar(chamada.name, args) if antes_de_executar else None
            if aviso:
                resultado = {"erro": aviso}
            else:
                try:
                    # TODO: execute ferramentas[chamada.name](**args) e guarde em resultado
                    resultado = ferramentas[chamada.name](**args)
                except Exception as erro:
                    resultado = {"erro": f"{type(erro).__name__}: {erro}"}
            partes.append(types.Part.from_function_response(name=chamada.name, response={"result": resultado}))

        historico.append(types.Content(role="user", parts=partes))
        if ao_fim_do_turno:
            ao_fim_do_turno(turno, response, time.perf_counter() - inicio)


def clima_servidor(datacenter: str) -> dict:
    """Retorna a temperatura em graus Celsius de um datacenter (sp-01 ou rs-02)."""
    return {"sp-01": {"celsius": 24.5}, "rs-02": {"celsius": 21.0}}[datacenter]


if __name__ == "__main__":
    texto, historico = rodar_agente(
        "Qual datacenter esta mais quente, sp-01 ou rs-02?",
        {"clima_servidor": clima_servidor},
    )
    print(texto)
    print("Mensagens no historico:", len(historico))