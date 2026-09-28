import os
from enum import Enum

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field, field_validator

load_dotenv()

MODEL = "gemini-3.8-flash"

client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)


class Severidade(str, Enum):
    BAIXA = "BAIXA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"
    CRITICA = "CRITICA"


class ItemAuditoria(BaseModel):
    tabela: str
    coluna: str
    anomalia_detectada: str
    registros_afetados: int
    severidade: Severidade

    @field_validator("registros_afetados")
    @classmethod
    def nao_negativo(cls, valor: int) -> int:
        # TODO: levante ValueError se valor < 0; caso contrario retorne o valor
        if valor < 0:
            raise ValueError("Sem registros afetados")

        return valor

    @field_validator("tabela", "coluna", "anomalia_detectada")
    @classmethod
    def nao_vazio(cls, valor: str) -> str:
        # TODO: levante ValueError se o texto (sem espacos nas pontas) estiver vazio
        if not valor.strip():
            raise ValueError("Sem texto")

        return valor


class RelatorioAuditoria(BaseModel):
    base_analisada: str
    itens: list[ItemAuditoria]
    resumo: str = Field(description="Resumo executivo em ate 2 frases")

    # TODO: adicione o campo requer_acao_imediata (bool)
    requer_acao_imediata: bool


RELATORIO_TEXTO = """
Auditoria da base de vendas (vendas.db). Na tabela clientes, a coluna email esta nula
em 37 registros, o que impede o envio de notas fiscais. Na tabela pedidos, a coluna
valor_total tem 4 pedidos com valores negativos, provavel erro de estorno. Na tabela
produtos, a coluna descricao tem 120 registros com texto duplicado, sem impacto operacional.
"""


if __name__ == "__main__":

    response = client.models.generate_content(
        model=MODEL,
        contents=f"Estruture o relatorio de auditoria abaixo.\n{RELATORIO_TEXTO}",
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=RelatorioAuditoria,
        ),
    )

    # response.parsed ja vem como instancia de RelatorioAuditoria
    relatorio: RelatorioAuditoria = response.parsed

    # Mostra o objeto completo retornado pelo Gemini
    print("\nRelatorio completo:")
    print(relatorio.model_dump_json(indent=2))

    print("\nItens da auditoria:")

    for item in relatorio.itens:
        print(
            f"[{item.severidade.value}] "
            f"{item.tabela}.{item.coluna}: "
            f"{item.registros_afetados}"
        )

    print("\nResumo:")
    print(relatorio.resumo)

    print("\nAcao imediata:")
    print(relatorio.requer_acao_imediata)

    # TODO: valide o validador sem chamar a LLM: tente instanciar ItemAuditoria com
    # registros_afetados=-5 dentro de try/except ValueError e imprima a mensagem de erro

    try:
        ItemAuditoria(
            tabela="clientes",
            coluna="email",
            anomalia_detectada="Campo nulo",
            registros_afetados=-5,
            severidade=Severidade.ALTA,
        )

    except ValueError as erro:
        print("\nErro de validacao:")
        print(erro)