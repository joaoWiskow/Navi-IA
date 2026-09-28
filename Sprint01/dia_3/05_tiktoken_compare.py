import os
import tiktoken
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODELO_FLASH = "gemini-3.8-flash"

# Inicializar o tokenizador oficial da familia OpenAI (usado no GPT-4)
enc = tiktoken.get_encoding("cl100k_base")

textos = {
    "Ingles": "Artificial Intelligence is transforming how we build software systems and interact with data.",
    "Portugues": "A Inteligencia Artificial esta transformando a forma como construimos sistemas de software e interagimos com dados.",
    "Codigo Python": """def calcular_media(valores: list[float]) -> float:
    if not valores:
        return 0.0
    return sum(valores) / len(valores)"""
}

print(f"{'Categoria':<15} | {'Tokens Gemini':<15} | {'Tokens Tiktoken':<15} | {'Diferenca'}")
print("-" * 65)

for categoria, texto in textos.items():
    # Contagem no Gemini
    res_gemini = client.models.count_tokens(model=MODELO_FLASH, contents=texto)
    tokens_gemini = res_gemini.total_tokens
    
    # Contagem no Tiktoken (OpenAI)
    tokens_tiktoken = len(enc.encode(texto))
    
    diferenca = tokens_gemini - tokens_tiktoken
    print(f"{categoria:<15} | {tokens_gemini:<15} | {tokens_tiktoken:<15} | {diferenca:+d}")

# Inspecao detalhada dos bytes de cada token no tiktoken
exemplo_pt = "transformando"
tokens_ids = enc.encode(exemplo_pt)
tokens_bytes = [enc.decode_single_token_bytes(tid) for tid in tokens_ids]

print("\nFatiamento detalhado no tiktoken para 'inteligencia artificial':")
for tid, tbytes in zip(tokens_ids, tokens_bytes):
    print(f"ID {tid:<6}: {tbytes}")