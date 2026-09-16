import os
from dotenv import load_dotenv
from google import genai

# Carregar credenciais do arquivo .env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("Erro: GEMINI_API_KEY nao encontrada no arquivo .env!")

# Inicializar o cliente oficial do Google GenAI
client = genai.Client(api_key=api_key)

# Definir o Modelo Gemini
MODELO_FLASH = "gemini-3.1-flash-lite"

# Chamada ao Modelo Gemini
response = client.models.generate_content(
    model=MODELO_FLASH,
    contents="Explique em exatamente 2 frases por que entender tokens e importante para um desenvolvedor de software.",
)

print("\n--- Resposta do Gemini ---")
print(response.text)
print("\n--- Metadados de Uso (Tokens) ---")
print(f"Tokens de Entrada (Prompt): {response.usage_metadata.prompt_token_count}")
print(f"Tokens de Saida (Resposta): {response.usage_metadata.candidates_token_count}")
print(f"Total de Tokens: {response.usage_metadata.total_token_count}")