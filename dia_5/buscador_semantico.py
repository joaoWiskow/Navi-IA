import os
import chromadb
from dotenv import load_dotenv
from google import genai
from pypdf import PdfReader

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

EMBEDDING_MODEL = "gemini-embedding-001"

caminhos_possiveis = [
    "data/manual_xiaomi_watch5.pdf",
    "sprint_1_fundamentos_rag/data/manual_xiaomi_watch5.pdf",
    "/home/usuario/Desktop/Navi-IA/dia_5/manual_xiaomi_watch5.pdf",
]
CAMINHO_PDF = next((p for p in caminhos_possiveis if os.path.exists(p)), "data/manual_xiaomi_watch5.pdf")

def gerar_embedding(texto: str) -> list[float]:
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=texto,
    )
    return response.embeddings[0].values

# 1. Carregar paginas do PDF para a comparacao com busca lexica
paginas_lexicas = []
if os.path.exists(CAMINHO_PDF):
    reader = PdfReader(CAMINHO_PDF)
    for i, pagina in enumerate(reader.pages, start=1):
        txt = (pagina.extract_text() or "").strip()
        if len(txt) > 30:
            paginas_lexicas.append({
                "pagina": i,
                "texto": txt
            })

# 2. Reabrir a colecao persistida no ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_data")
collection = chroma_client.get_or_create_collection(
    name="manual_xiaomi_watch5",
    metadata={"hnsw:space": "cosine"}
)

print("=" * 70)
print("BUSCADOR TECNICO DO MANUAL: BUSCA SEMANTICA vs. BUSCA LEXICA")
print(f"Colecao ChromaDB: {collection.name} ({collection.count()} paginas indexadas)")
print("Digite sua pergunta sobre o Smartwatch Xiaomi (ou 'sair' para encerrar)")
print("=" * 70)

while True:
    query = input("\nSua duvida sobre o relogio: ").strip()
    if query.lower() in ["sair", "exit", "quit"]:
        break
    if not query:
        continue

    # --- 1. BUSCA LEXICA (Procura palavras exatas da query no texto) ---
    print("\n--- 1. RESULTADOS DA BUSCA LEXICA (Palavras Exatas) ---")
    termos_query = [t for t in query.lower().split() if len(t) > 2]
    encontrados_lexico = []
    for pag in paginas_lexicas:
        texto_lower = pag["texto"].lower()
        if any(termo in texto_lower for termo in termos_query):
            encontrados_lexico.append(pag["pagina"])

    if encontrados_lexico:
        paginas_str = ", ".join(f"Pagina {p}" for p in encontrados_lexico[:4])
        print(f"  [Match Palavra-Chave]: {paginas_str}")
    else:
        print("  (Nenhuma pagina contem as palavras exatas digitadas)")

    # --- 2. BUSCA SEMANTICA (ChromaDB + Embeddings Gemini) ---
    print("\n--- 2. RESULTADOS DA BUSCA SEMANTICA (Similaridade de Cosseno) ---")
    vetor_query = gerar_embedding(query)
    resultados = collection.query(
        query_embeddings=[vetor_query],
        n_results=2
    )

    for i, (doc_texto, meta, dist) in enumerate(zip(
        resultados["documents"][0],
        resultados["metadatas"][0],
        resultados["distances"][0]
    ), 1):
        similaridade = 1.0 - dist
        primeiras_linhas = " ".join(doc_texto.split("\n")[:3])
        print(f"  [Top #{i}] Pagina {meta['pagina']:02d} do Manual (Similaridade: {similaridade:.2%})")
        print(f"         Trecho: \"{primeiras_linhas[:180]}...\"\n")