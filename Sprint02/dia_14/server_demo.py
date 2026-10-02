from mcp.server.fastmcp import FastMCP

mcp = FastMCP("demo-dia14")


@mcp.tool()
def somar(a: int, b: int) -> int:
    """Soma dois numeros inteiros e retorna o resultado."""
    return a + b


@mcp.tool()
def status_servico(servico: str) -> str:
    """Retorna o status de um servico interno (api, banco ou fila)."""
    tabela = {"api": "operacional", "banco": "operacional", "fila": "degradada"}
    if servico not in tabela:
        raise ValueError(f"Servico desconhecido: {servico}")
    return tabela[servico]


@mcp.resource("file:///docs/regras.md")
def regras() -> str:
    """Regras internas da equipe de dados."""
    return "1. Nunca altere dados em producao.\n2. Toda consulta deve ter LIMIT.\n3. Registre incidentes no canal #dados."


if __name__ == "__main__":
    mcp.run(transport="stdio")