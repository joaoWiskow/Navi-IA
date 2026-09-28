import json

from pydantic import BaseModel, Field, create_model

TIPOS = {"string": str, "integer": int, "number": float, "boolean": bool}


class Produto(BaseModel):
    sku: str = Field(description="Codigo unico do produto")
    preco: float = Field(description="Preco em reais")
    ativo: bool = True


def modelo_para_schema(modelo: type[BaseModel]) -> dict:
    return modelo.model_json_schema()


def schema_para_modelo(nome: str, schema: dict) -> type[BaseModel]:
    """Reconstroi uma classe Pydantic simples (campos escalares) a partir de um JSON Schema."""
    campos = {}
    obrigatorios = set(schema.get("required", []))

    for campo, definicao in schema["properties"].items():
        tipo = TIPOS[definicao["type"]]

        # TODO: se o campo for obrigatorio use (tipo, ...); senao use (tipo, definicao.get("default"))
        if campo in obrigatorios:
            campos[campo] = (tipo, ...)
        else:
            campos[campo] = (tipo, definicao.get("default"))

    return create_model(nome, **campos)


def gerar_documentacao(schema: dict) -> str:
    linhas = [
        f"# {schema['title']}",
        "",
        "| Campo | Tipo | Obrigatorio | Descricao |",
        "| --- | --- | --- | --- |"
    ]

    obrigatorios = set(schema.get("required", []))

    for campo, definicao in schema["properties"].items():
        # TODO: monte uma linha da tabela com campo, tipo, "sim"/"nao" e a descricao (se existir)
        tipo = definicao["type"]
        obrigatorio = "sim" if campo in obrigatorios else "nao"
        descricao = definicao.get("description", "")

        linhas.append(
            f"| {campo} | {tipo} | {obrigatorio} | {descricao} |"
        )

    return "\n".join(linhas)


if __name__ == "__main__":
    schema = modelo_para_schema(Produto)

    print(json.dumps(schema, indent=2, ensure_ascii=False))

    Reconstruido = schema_para_modelo("ProdutoReconstruido", schema)

    print(Reconstruido(sku="A-1", preco=10.5))

    print(gerar_documentacao(schema))