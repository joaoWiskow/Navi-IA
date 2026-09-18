import math
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

EMBEDDING_MODEL = "gemini-embedding-001"

def gerar_embedding(texto: str) -> list[float]:
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=texto,
    )
    return response.embeddings[0].values

def produto_escalar(v1: list[float], v2: list[float]) -> float:
    return sum(a * b for a, b in zip(v1, v2))

def norma_vetor(v: list[float]) -> float:
    return math.sqrt(sum(a * a for a in v))

def similaridade_cosseno(v1: list[float], v2: list[float]) -> float:
    dot = produto_escalar(v1, v2)
    norma1 = norma_vetor(v1)
    norma2 = norma_vetor(v2)
    if norma1 == 0 or norma2 == 0:
        return 0.0
    return dot / (norma1 * norma2)

# Teste pratico com pares conceituais
frase_a = "como resetar o relogio para as configuracoes de fabrica"
frase_b = "restaurar padroes de fabrica e apagar todos os dados"
frase_c = "receita de bolo de chocolate com cobertura de morango"

print("Gerando embeddings via Gemini API...")
vetor_a = gerar_embedding(frase_a)
vetor_b = gerar_embedding(frase_b)
vetor_c = gerar_embedding(frase_c)

sim_ab = similaridade_cosseno(vetor_a, vetor_b)
sim_ac = similaridade_cosseno(vetor_a, vetor_c)

print("\n" + "=" * 65)
print("CALCULO MANUAL DE SIMILARIDADE DE COSSENO (SEM LIBS EXTERNAS)")
print("=" * 65)
print(f"Frase A: \"{frase_a}\"")
print(f"Frase B: \"{frase_b}\"")
print(f"Frase C: \"{frase_c}\"")
print("-" * 65)
print(f"Similaridade (A vs B - mesmo tema):     {sim_ab:.4f} ({sim_ab:.2%})")
print(f"Similaridade (A vs C - temas opostos):  {sim_ac:.4f} ({sim_ac:.2%})")
print("=" * 65)