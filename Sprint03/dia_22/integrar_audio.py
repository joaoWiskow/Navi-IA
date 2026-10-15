import json
import sys
from pathlib import Path
from pydantic import BaseModel, Field
from resumir import processar_audio_com_llm
from transcrever import transcrever_audio

class ChamadoSuporte(BaseModel):
    solicitante: str = Field(description="Nome da pessoa identificada na fala ou 'Nao identificado'")
    filial_ou_setor: str = Field(description="Setor ou filial mencionado")
    servico_afetado: str = Field(description="Componente de TI mencionado")
    prioridade: str = Field(description="ALTA, MEDIA ou BAIXA de acordo com a urgencia expressa")
    resumo_chamado: str = Field(description="Descricao tecnica clara do problema")

def gerar_chamado_de_audio(caminho: Path) -> dict:
    transcricao = transcrever_audio(caminho)
    analise = processar_audio_com_llm(caminho)
    
    return {
        "arquivo": caminho.name,
        "fala_transcrita": transcricao["texto"],
        "resumo_executivo": analise.resumo_executivo,
        "itens_com_tempo": [item.model_dump() for item in analise.acoes_identificadas],
        "tempo_total_processamento_ms": transcricao["tempo_processamento_ms"]
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python dia_22/integrar_audio.py amostras/chamado.wav")
        sys.exit(1)
        
    resultado = gerar_chamado_de_audio(Path(sys.argv[1]))
    print(json.dumps(resultado, indent=2, ensure_ascii=False))