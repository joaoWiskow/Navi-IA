import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

PARAMS = StdioServerParameters(command=sys.executable, args=["server_demo.py"])


async def main() -> None:
    async with stdio_client(PARAMS) as (leitura, escrita):
        async with ClientSession(leitura, escrita) as sessao:
            await sessao.initialize()

            catalogo = await sessao.list_tools()
            for ferramenta in catalogo.tools:
                print(f"- {ferramenta.name}: {ferramenta.description}")
                # TODO: imprima tambem ferramenta.inputSchema (o JSON Schema gerado a partir dos type hints)
                print(f"  Schema: {ferramenta.inputSchema}")
            resultado = await sessao.call_tool("somar", {"a": 40, "b": 2})
            print("somar(40, 2) ->", resultado.content[0].text)

            # TODO: chame "status_servico" com {"servico": "fila"} e imprima o texto
            resultado = await sessao.call_tool(
            "status_servico",
            {"servico": "fila"}
            )
            print("status_servico(fila) ->", resultado.content[0].text)
            
            
            # TODO: chame "status_servico" com {"servico": "impressora"} (invalido) e imprima
            #       resultado.isError e o texto da mensagem de erro; o processo NAO deve cair
            resultado = await sessao.call_tool(
            "status_servico",
            {"servico": "impressora"}
            )
            print(
                "isError:", resultado.isError,
                "| mensagem:", resultado.content[0].text
            )


if __name__ == "__main__":
    asyncio.run(main())
    