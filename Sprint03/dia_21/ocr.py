import os
import sys
from pathlib import Path
from typing import Annotated
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from visao import carregar_imagem

load_dotenv(Path(__file__).resolve().parents[2] / ".env")
MODEL = "gemini-3.8-flash"

PROJECT_ROOT = Path(__file__).resolve().parents[2]
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError(f"GEMINI_API_KEY nao encontrada em {PROJECT_ROOT / '.env'}")

Coordenada = Annotated[int, Field(ge=0, le=1000, description="Coordenada normalizada de 0 a 1000")]

class ElementoVisual(BaseModel):
    texto_extraido: str = Field(description="Texto exato lido na regiao")
    caixa_delimitadora: list[Coordenada] = Field(
        min_length=4, max_length=4,
        description="Coordenadas [ymin, xmin, ymax, xmax] normalizadas de 0 a 1000"
    )

class AnaliseDocumento(BaseModel):
    elementos: list[ElementoVisual] = Field(description="Lista de textos e suas posicoes")
    codigo_identificador: str | None = Field(default=None, description="Codigo principal do documento (ex: A101) ou null se ausente")
    relacoes_detectadas: list[str] = Field(description="Relacoes semanticas observadas no diagrama")
    limitacoes_visuais: list[str] = Field(description="Alertas de baixa resolucao, cortes ou incertezas")

def extrair_dados_estruturados(caminho: Path) -> AnaliseDocumento:
    dados, mime, _ = carregar_imagem(caminho)
    cliente = genai.Client(api_key=API_KEY)
    
    prompt = (
        "Analise a imagem tecnica fornecida. "
        "Localize todas as caixas de texto com suas coordenadas [ymin, xmin, ymax, xmax]. "
        "Descreva somente o que estiver explicitamente visivel na imagem. "
        "Se um codigo identificador nao estiver nitido, deixe codigo_identificador como null; "
        "nao invente nomes, numeros ou campos ausentes. "
        "Em relacoes_detectadas, cite apenas relacoes que forem claramente observadas. "
        "Em limitacoes_visuais, liste qualquer problema de qualidade, corte, ambiguidade ou duvida."
    )
    
    resposta = cliente.models.generate_content(
        model=MODEL,
        contents=[prompt, types.Part.from_bytes(data=dados, mime_type=mime)],
        config=types.GenerateContentConfig(
            temperature=0.0,
            response_mime_type="application/json",
            response_schema=AnaliseDocumento
        )
    )
    
    documento = AnaliseDocumento.model_validate_json(resposta.text or "{}")
    
    # Validacao de consistencia geometrica
    for item in documento.elementos:
        ymin, xmin, ymax, xmax = item.caixa_delimitadora
        if ymin >= ymax or xmin >= xmax:
            raise ValueError(f"Coordenadas geometricamente invalidas detectadas: {item.caixa_delimitadora}")
            
    return documento

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python dia_21/ocr.py amostras/diagrama.png")
        sys.exit(1)
        
    resultado = extrair_dados_estruturados(Path(sys.argv[1]))
    print(resultado.model_dump_json(indent=2))