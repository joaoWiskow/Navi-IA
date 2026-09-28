import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODELO_FLASH = "gemini-3.1-flash-lite"

prompt = "Sugira um nome criativo para uma startup de IA que ajuda desenvolvedores a debugar codigo. sem explicar o porque"

print(f"Prompt Testado: '{prompt}'\n")

# Experimento 1: variando TOP_P (temperature fixa em 1.0)
print("=" * 50)
print("EXPERIMENTO 1: Variando TOP_P (temperature=1.0)")
print("=" * 50)
# for top_p in [0.1, 0.5, 1.0]:
#     response = client.models.generate_content(
#         model=MODELO_FLASH,
#         contents=prompt,
#         config=types.GenerateContentConfig(
#             temperature=1.0,
#             top_p=top_p,
#             max_output_tokens=50
#         )
#     )
#     print(f"\n[top_p={top_p}]: {response.text.strip()}")

# Experimento 2: variando TOP_K (temperature fixa em 1.0)
print("\n" + "=" * 50)
print("EXPERIMENTO 2: Variando TOP_K (temperature=1.0)")
print("=" * 50)
for top_k in [1, 10, 40]:
    response = client.models.generate_content(
        model=MODELO_FLASH,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=1.0,
            top_k=top_k,
            max_output_tokens=50
        )
    )
    print(f"\n[top_k={top_k}]: {response.text.strip()}")