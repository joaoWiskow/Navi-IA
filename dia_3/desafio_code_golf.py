import json
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODELO_FLASH = "gemini-3.1-flash-lite"

entrada = "MarianaES4"

# Elabore o prompt mais enxuto possivel aqui:
prompt = f"JSONnomecursosemestre{entrada}"

# 1. Medicao oficial de tokens
tokens = client.models.count_tokens(model=MODELO_FLASH, contents=prompt).total_tokens
print(f"Total de Tokens do Prompt: {tokens}")

# 2. Execucao com retorno estruturado
response = client.models.generate_content(
    model=MODELO_FLASH,
    contents=prompt,
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        temperature=0.0
    )
)

print(f"\nResposta Bruta:\n{response.text.strip()}")

# 3. Validacao rigorosa do JSON
try:
    dados = json.loads(response.text)
    assert "nome" in dados and "curso" in dados and "semestre" in dados
    print(f"\nValidacao JSON: SUCESSO! Dados extraidos: {dados}")
except Exception as e:
    print(f"\nValidacao JSON: FALHA ({e})")