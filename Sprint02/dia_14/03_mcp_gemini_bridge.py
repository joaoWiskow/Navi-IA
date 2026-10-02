import asyncio
import os
import sys

from dotenv import load_dotenv
from google import genai
from google.genai import types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()

MODEL = "gemini-3.5-flash-lite"
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

PARAMS = StdioServerParameters(
    command=sys.executable,
    args=["server_demo.py"]
)


def converter_mcp_para_gemini_tools(
    mcp_tools
) -> list[types.Tool]:
    """Converte o catalogo MCP (tools/list) em declaracoes de funcao do Gemini."""
    declaracoes = []

    for ferramenta in mcp_tools:
        declaracao = types.FunctionDeclaration(
            name=ferramenta.name,
            description=ferramenta.description,
            parameters_json_schema=ferramenta.inputSchema,
        )

        declaracoes.append(declaracao)

    return [
        types.Tool(
            function_declarations=declaracoes
        )
    ]


async def perguntar(
    sessao: ClientSession,
    pergunta: str,
    max_turnos: int = 5
) -> str:

    catalogo = await sessao.list_tools()

    config = types.GenerateContentConfig(
        tools=converter_mcp_para_gemini_tools(catalogo.tools)
    )

    historico = [
        types.Content(
            role="user",
            parts=[types.Part(text=pergunta)]
        )
    ]

    for _ in range(max_turnos):

        response = await client.aio.models.generate_content(
            model=MODEL,
            contents=historico,
            config=config
        )

        historico.append(response.candidates[0].content)

        if not response.function_calls:
            return response.text

        partes = []

        for chamada in response.function_calls:

            resultado_mcp = await sessao.call_tool(
                chamada.name,
                dict(chamada.args)
            )

            texto = (
                resultado_mcp.content[0].text
                if resultado_mcp
                else "sem resultado"
            )

            partes.append(
                types.Part.from_function_response(
                    name=chamada.name,
                    response={"result": texto}
                )
            )

        historico.append(
            types.Content(
                role="user",
                parts=partes
            )
        )

    return "Limite de turnos atingido."


async def main() -> None:

    async with stdio_client(PARAMS) as (leitura, escrita):

        async with ClientSession(leitura, escrita) as sessao:

            await sessao.initialize()

            print(
                await perguntar(
                    sessao,
                    "Quanto e 1234 mais 4321, e como esta a fila?"
                )
            )


if __name__ == "__main__":
    asyncio.run(main())