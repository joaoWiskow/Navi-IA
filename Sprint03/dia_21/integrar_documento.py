import json
import sys
from pathlib import Path
from visao import comparar_modalidades
from ocr import extrair_dados_estruturados

def auditar_diagrama(caminho: Path, rotulos_obrigatorios: list[str]) -> dict:
    descricoes = comparar_modalidades(caminho)
    analise = extrair_dados_estruturados(caminho)
    
    textos_encontrados = " ".join(e.texto_extraido for e in analise.elementos).casefold()
    
    conferencias = {}
    for rotulo in rotulos_obrigatorios:
        presente = rotulo.casefold() in textos_encontrados
        conferencias[rotulo] = "CONFIRMADO_VISUALMENTE" if presente else "ALERTA_NAO_ENCONTRADO"
        
    return {
        "arquivo": caminho.name,
        "conferencias": conferencias,
        "total_elementos_detectados": len(analise.elementos),
        "limitacoes_apontadas": analise.limitacoes_visuais
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python dia_21/integrar_documento.py amostras/diagrama.png")
        sys.exit(1)
        
    componentes_esperados = [
        "Frontend",
        "Backend",
        "Banco de Dados",
        "API",
        "Servidor"
    ]
    relatorio = auditar_diagrama(Path(sys.argv[1]), componentes_esperados)
    print(json.dumps(relatorio, indent=2, ensure_ascii=False))