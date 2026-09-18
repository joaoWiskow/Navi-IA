import os
import chromadb
from dotenv import load_dotenv
from google import genai
from pypdf import PdfReader

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

EMBEDDING_MODEL = "gemini-embedding-001"

# Suporte flexivel de caminho para execucao da raiz ou de dentro da sprint
caminhos_possiveis = [
    "data/manual_xiaomi_watch5.pdf",
    "sprint_1_fundamentos_rag/data/manual_xiaomi_watch5.pdf",
    "/home/usuario/Desktop/Navi-IA/dia_5/manual_xiaomi_watch5.pdf",
]
CAMINHO_PDF = next((p for p in caminhos_possiveis if os.path.exists(p)), "data/manual_xiaomi_watch5.pdf")

# 1. Funcao para gerar embeddings vetoriais via Gemini API
def gerar_embedding(texto: str) -> list[float]:
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=texto,
    )
    return response.embeddings[0].values

# 2. Leitura e extracao de paginas do PDF com pypdf
if not os.path.exists(CAMINHO_PDF):
    raise FileNotFoundError(
        f"Arquivo '{CAMINHO_PDF}' nao encontrado! "
        "Certifique-se de que o arquivo manual_xiaomi_watch5.pdf esta na pasta data/."
    )

reader = PdfReader(CAMINHO_PDF)
total_paginas = len(reader.pages)
print(f"Lendo manual em PDF: '{CAMINHO_PDF}' ({total_paginas} paginas)...")

documentos_indexados = []
for num_pagina, pagina in enumerate(reader.pages, start=1):
    texto = (pagina.extract_text() or "").strip()
    if len(texto) > 30:  # Ignora paginas sem conteudo textual relevante
        documentos_indexados.append({
            "id": f"pagina_{num_pagina:02d}",
            "pagina": num_pagina,
            "texto": texto
        })

print(f"Extraidas {len(documentos_indexados)} paginas com conteudo textual.")

# 3. Inicializar cliente local persistente do ChromaDB (salva em ./chroma_data)
chroma_client = chromadb.PersistentClient(path="./chroma_data")

# 4. Criar ou obter a colecao vetorial com similaridade de cosseno
collection = chroma_client.get_or_create_collection(
    name="manual_xiaomi_watch5",
    metadata={"hnsw:space": "cosine"}
)

# 5. Gerar embeddings e indexar cada pagina no ChromaDB
print("Gerando embeddings e inserindo paginas no ChromaDB...")
for doc in documentos_indexados:
    vetor = gerar_embedding(doc["texto"])
    collection.upsert(
        ids=[doc["id"]],
        embeddings=[vetor],
        documents=[doc["texto"]],
        metadatas=[{"pagina": doc["pagina"], "arquivo": "manual_xiaomi_watch5.pdf"}]
    )
    resumo_linha = doc["texto"].split("\n")[0][:45]
    print(f"  -> Indexada Pagina {doc['pagina']:02d}: {resumo_linha}... (ID: {doc['id']})")

print("\n" + "=" * 65)
print(f"Sucesso! Colecao '{collection.name}' pronta com {collection.count()} paginas indexadas.")
print("=" * 65)