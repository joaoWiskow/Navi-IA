import asyncio
import importlib
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


# Adiciona a pasta dia_14 ao caminho de importação
DIA_14 = Path(__file__).resolve().parent.parent / "dia_14"
sys.path.insert(0, str(DIA_14))

ponte = importlib.import_module("03_mcp_gemini_bridge")


PARAMS = StdioServerParameters(
    command=sys.executable,
    args=["server_utils.py"],
)

PERGUNTAS = [
    "Quantas linhas de codigo Python temos neste projeto e qual o hash do arquivo server_utils.py?",
    "Quanto sao 98.6 graus Fahrenheit em Celsius?",
]


async def main() -> None:
    async with stdio_client(PARAMS) as (leitura, escrita):
        async with ClientSession(leitura, escrita) as sessao:
            await sessao.initialize()

            for pergunta in PERGUNTAS:
                print("PERGUNTA:", pergunta)

                resposta = await ponte.perguntar(sessao, pergunta)

                print("RESPOSTA:", resposta)
                print("-" * 60)


if __name__ == "__main__":
    asyncio.run(main())