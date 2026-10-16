import os
import sys
from io import BytesIO
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image

load_dotenv(Path(__file__).resolve().parents[2] / ".env")
MODEL = "gemini-3.5-flash-lite"

PROJECT_ROOT = Path(__file__).resolve().parents[2]
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError(f"GEMINI_API_KEY nao encontrada em {PROJECT_ROOT / '.env'}")

def carregar_imagem(caminho: Path) -> tuple[bytes, str, Image.Image]:
    """Valida o arquivo em disco e retorna os bytes, o MIME real e a imagem Pillow."""
    if not caminho.is_file() or caminho.stat().st_size > 5_000_000:
        raise ValueError("O arquivo deve existir e ter ate 5 MB.")
    
    dados = caminho.read_bytes()
    
    # Validacao de integridade com Pillow (evita renomear .txt para .png)
    with Image.open(BytesIO(dados)) as img:
        img.verify()
        formato = img.format
        largura, altura = img.size

    mime = {"PNG": "image/png", "JPEG": "image/jpeg"}.get(formato or "")
    if not mime:
        raise ValueError(f"Formato nao suportado: {formato}. Use PNG ou JPEG.")
    
    if largura * altura > 12_000_000:
        raise ValueError("Imagem excede o limite de 12 Megapixels.")

    with Image.open(BytesIO(dados)) as img:
        imagem_pil = img.convert("RGB")

    return dados, mime, imagem_pil

def comparar_modalidades(caminho: Path) -> dict[str, str]:
    """Envia a mesma imagem via bytes e via PIL e compara a clareza da resposta."""
    dados, mime, imagem_pil = carregar_imagem(caminho)
    
    prompt = (
        "Voce e um especialista em auditoria de diagramas de arquitetura. "
        "Descreva os componentes tecnicos visiveis, as direcoes exatas de todas as setas e as conexoes entre eles. "
        "Mencione explicitamente qualquer texto ou rotulo que esteja ilegivel, incompleto ou pouco nítido usando a marca ROTULO_ILEGIVEL. "
        "Se algum componente ou label nao puder ser lido com seguranca, diga claramente que nao foi possivel confirmar e nao invente informacoes."
    )
    
    entradas = {
        "bytes": types.Part.from_bytes(data=dados, mime_type=mime),
        "PIL": imagem_pil
    }
    
    resultados: dict[str, str] = {}
    cliente = genai.Client(api_key=API_KEY)
    
    for modo, entrada in entradas.items():
        resposta = cliente.models.generate_content(
            model=MODEL,
            contents=[prompt, entrada],
            config=types.GenerateContentConfig(temperature=0.0)
        )
        resultados[modo] = resposta.text or "Sem resposta gerada."
        
    return resultados

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python dia_21/visao.py amostras/diagrama.png")
        sys.exit(1)
        
    respostas = comparar_modalidades(Path(sys.argv[1]))
    for modo, texto in respostas.items():
        print(f"\n=== Resposta via {modo.upper()} ===")
        print(texto)