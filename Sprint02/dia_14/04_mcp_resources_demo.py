import asyncio
import os
import sys

from dotenv import load_dotenv
from google import genai
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()

MODEL = "gemini-3.5-flash-lite"

client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)

PARAMS = StdioServerParameters(
    command=sys.executable,
    args=["server_demo.py"]
)


async def main() -> None:
    async with stdio_client(PARAMS) as (leitura, escrita):
        async with ClientSession(leitura, escrita) as sessao:
            await sessao.initialize()

            # 1. Listar os resources
            catalogo = await sessao.list_resources()

            for resource in catalogo.resources:
                print(
                    f"- URI: {resource.uri} | "
                    f"Nome: {resource.name}"
                )

            # 2. Ler o resource
            conteudo = await sessao.read_resource(
                "file:///docs/regras.md"
            )

            regras = conteudo.contents[0].text

            print("\nREGRAS:")
            print(regras)

            # 3. Montar o prompt usando as regras como contexto
            prompt = f"""
Com base nas regras abaixo, responda:

Posso rodar um DELETE em producao?

Regras:
{regras}
"""

            # 4. Enviar o prompt para o Gemini
            print("\nCONSULTANDO GEMINI...")

            response = await client.aio.models.generate_content(
                model=MODEL,
                contents=prompt
            )

            # 5. Imprimir resposta
            print("\nRESPOSTA DO GEMINI:")
            print(response.text)


if __name__ == "__main__":
    asyncio.run(main())