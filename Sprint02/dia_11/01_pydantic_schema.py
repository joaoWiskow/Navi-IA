import os
from typing import Literal

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

load_dotenv()
MODEL = "gemini-3.1-flash-lite"
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


class PerfilUsuario(BaseModel):
    # TODO: declare os campos do perfil com type hints e Field(description=...): 
    # # nome (str), idade (int, entre 0 e 120: dica, Field(ge=0, le=120)), habilidades (list[str]),
    # # status (Literal["ativo", "inativo", "pendente"]) ...
    
    nome: str = Field(description="Nome do usuário")
    idade: int = Field(
        ge=0,
        le=120,
        description="Idade do usuário, entre 0 e 120 anos"
    )
    habilidades: list[str] = Field(
        description="Lista de habilidades do usuário"
    )
    status: Literal["ativo", "inativo", "pendente"] = Field(
        description="Status atual do usuário"
    )


TEXTO = (
    "Oi, sou a Marina Souza, tenho trinta anos e trabalho com Python, SQL e Power BI. "
    "Minha conta ainda esta aguardando aprovacao do time."
)


def extrair_perfil(texto: str) -> PerfilUsuario:
    response = client.models.generate_content(
        model=MODEL,
        contents=f"Extraia o perfil do usuario do texto abaixo.\n\n{texto}",
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            # TODO: passe a classe PerfilUsuario em response_schema
            response_schema=PerfilUsuario,
        ),
    )
    # response.parsed ja vem como instancia de PerfilUsuario
    return response.parsed


if __name__ == "__main__":
    perfil = extrair_perfil(TEXTO)
    print(type(perfil).__name__)
    print(perfil.model_dump_json(indent=2))
    # TODO: imprima o JSON Schema gerado pelo Pydantic com PerfilUsuario.model_json_schema()
    print(PerfilUsuario.model_json_schema())