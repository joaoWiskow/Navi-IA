import json
import sys
from functools import lru_cache
from pathlib import Path
from time import perf_counter
from typing import TypedDict
import numpy as np
import whisper
from whisper.model import Whisper

class Segmento(TypedDict):
    inicio: float
    fim: float
    texto: str

class Transcricao(TypedDict):
    texto: str
    segmentos: list[Segmento]
    duracao_segundos: float
    tempo_processamento_ms: float
    fator_tempo_real: float

@lru_cache(maxsize=1)
def obter_modelo() -> Whisper:
    """Mantem o modelo em memoria cache para nao recarregar os pesos a cada chamada."""
    print("Carregando pesos do Whisper tiny na CPU...")
    return whisper.load_model("tiny", device="cpu")

def transcrever_audio(caminho: Path) -> Transcricao:
    inicio = perf_counter()
    
    if not caminho.is_file() or caminho.stat().st_size > 10_000_000:
        raise ValueError("Informe um arquivo de audio existente de ate 10 MB.")
        
    audio = whisper.load_audio(str(caminho))
    duracao = len(audio) / whisper.audio.SAMPLE_RATE
    
    if not 0 < duracao <= 45:
        raise ValueError("Para os laboratorios, utilize audios curtos de ate 45 segundos.")
        
    # Verificacao basica de energia RMS (rejeita arquivos de silencio absoluto)
    energia_rms = float(np.sqrt(np.mean(audio ** 2)))
    if energia_rms < 0.001:
        raise ValueError("Audio silencioso ou inaudivel. Grave uma fala clara.")
        
    modelo = obter_modelo()
    resultado = modelo.transcribe(audio, language="pt", fp16=False, verbose=False)
    
    segmentos: list[Segmento] = [
        {
            "inicio": round(float(s["start"]), 2),
            "fim": round(float(s["end"]), 2),
            "texto": str(s["text"]).strip()
        }
        for s in resultado["segments"]
    ]
    
    texto_completo = str(resultado["text"]).strip()
    tempo_total = perf_counter() - inicio
    
    # Fator de Tempo Real (RTF): tempo_total / duracao
    # Exemplo: se a duração for 10s e o processamento levar 5s, o RTF será 0.5,
    # indicando processamento mais rápido que o tempo real.
    rtf = round(tempo_total / duracao, 2)
    
    return {
        "texto": texto_completo,
        "segmentos": segmentos,
        "duracao_segundos": round(duracao, 2),
        "tempo_processamento_ms": round(tempo_total * 1000, 1),
        "fator_tempo_real": rtf
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python dia_22/transcrever.py amostras/comando.wav")
        sys.exit(1)
        
    resultado = transcrever_audio(Path(sys.argv[1]))
    print(json.dumps(resultado, indent=2, ensure_ascii=False))