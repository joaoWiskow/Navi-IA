import asyncio
import hashlib
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

PARAMS = StdioServerParameters(command=sys.executable, args=["server_utils.py"])
aprovados = 0
falhas = 0


def checar(nome: str, condicao: bool, detalhe: str = "") -> None:
    global aprovados, falhas

    if condicao:
        aprovados += 1
        print(f"  [OK]   {nome}")
    else:
        falhas += 1
        print(f"  [FALHA] {nome} {detalhe}")


async def main() -> None:
    async with stdio_client(PARAMS) as (leitura, escrita):
        async with ClientSession(leitura, escrita) as sessao:
            await sessao.initialize()

            nomes = {
                t.name
                for t in (await sessao.list_tools()).tools
            }

            checar(
                "expoe as 3 ferramentas",
                nomes == {
                    "calcular_hash_arquivo",
                    "contar_linhas_codigo",
                    "converter_temperatura",
                },
            )

            # Teste básico da conversão
            r = await sessao.call_tool(
                "converter_temperatura",
                {
                    "valor": 100,
                    "de": "C",
                    "para": "F",
                },
            )

            checar(
                "100 C = 212 F",
                r.content[0].text.startswith("212"),
                r.content[0].text,
            )

            # Teste do hash SHA-256
            esperado = hashlib.sha256(
                Path(__file__).read_bytes()
            ).hexdigest()

            r = await sessao.call_tool(
                "calcular_hash_arquivo",
                {
                    "caminho": str(Path(__file__).resolve()),
                },
            )

            checar(
                "hash SHA-256 do proprio script",
                not r.isError and r.content[0].text == esperado,
                r.content[0].text if r.content else "sem resposta",
            )

            # Teste de erro: diretório inexistente
            r = await sessao.call_tool(
                "contar_linhas_codigo",
                {
                    "diretorio": "diretorio_que_nao_existe_123456",
                    "extensao": ".py",
                },
            )

            checar(
                "erro para diretorio inexistente",
                r.isError,
                r.content[0].text if r.content else "sem mensagem de erro",
            )

            # Teste de erro de tipo
            r = await sessao.call_tool(
                "converter_temperatura",
                {
                    "valor": "abc",
                    "de": "C",
                    "para": "F",
                },
            )

            checar(
                "erro para valor com tipo invalido",
                r.isError,
                r.content[0].text if r.content else "sem mensagem de erro",
            )

            # Teste de erro de domínio
            r = await sessao.call_tool(
                "converter_temperatura",
                {
                    "valor": 100,
                    "de": "X",
                    "para": "C",
                },
            )

            mensagem = r.content[0].text if r.content else ""

            checar(
                "erro para unidade invalida",
                r.isError and "Unidades validas" in mensagem,
                mensagem,
            )

            # Prova de vida: o servidor continua respondendo depois dos erros
            r = await sessao.call_tool(
                "converter_temperatura",
                {
                    "valor": 0,
                    "de": "K",
                    "para": "C",
                },
            )

            checar(
                "servidor vivo apos os erros",
                not r.isError,
                r.content[0].text if r.content else "sem resposta",
            )

    print(f"\nResumo: {aprovados} aprovados, {falhas} falhas")

    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    asyncio.run(main())