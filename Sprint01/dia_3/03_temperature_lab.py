import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODELO_FLASH = "gemini-3.1-flash-lite"

prompt = "Crie uma metafora curta e poetica para explicar o que e uma funcao recursiva na programacao."
temperaturas = [0.0, 0.7, 1.5]

print(f"Prompt Testado: '{prompt}'\n")

for temp in temperaturas:
    print(f"\n" + "=" * 50)
    print(f"EXPERIMENTO COM TEMPERATURA = {temp}")
    print("=" * 50)
    
    # Executar 2 vezes para verificar determinismo vs aleatoriedade
    for tentativa in range(1, 3):
        response = client.models.generate_content(
            model=MODELO_FLASH,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=temp,
                max_output_tokens=150
            )
        )
        print(f"\n[Tentativa {tentativa}]:")
        print(response.text.strip())