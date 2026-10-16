import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from transcrever import transcrever_audio

load_dotenv()
MODEL = "gemini-3.5-flash-lite"

class ItemAcao(BaseModel):
    descricao: str = Field(description="Acao ou fato importante extraido do audio")
    intervalo_tempo: str = Field(description="Timestamp formatado como [inicio - fim] em segundos onde a fala ocorreu")

class AnaliseAudio(BaseModel):
    resumo_executivo: str = Field(description="Sintese clara e objetiva do que foi falado")
    acoes_identificadas: list[ItemAcao] = Field(description="Lista de itens de acao com seus respectivos tempos")
    ambiguidades_ou_ruidos: list[str] = Field(description="Alertas de trechos inaudiveis ou codigos com duvida")

def processar_audio_com_llm(caminho: Path) -> AnaliseAudio:
    transcricao = transcrever_audio(caminho)
    cliente = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    
    # Formatamos os segmentos para alimentar o modelo com timestamps precisos
    segmentos_str = json.dumps(transcricao["segmentos"], ensure_ascii=False, indent=2)
    
    # TODO: Crie a system instruction orientando o modelo a nao inventar informacoes
    # e a fundamentar rigorosamente cada acao nos intervalos de tempo recebidos.
    system_prompt = (
        "Voce e um analista de operacoes de audio. "
        "Analise apenas os segmentos transcritos e seus timestamps fornecidos. "
        "Nao invente fatos, nomes, numeros, ordem de eventos ou detalhes que nao estejam claramente presentes no audio. "
        "Fundamente cada acao identificada exclusivamente no intervalo de tempo correspondente. "
        "Se houver trechos duvidosos, ruidos, termos incompreensiveis ou falas inaudiveis, registre-os em ambiguidades_ou_ruidos. "
        "Para cada acao identificada, cite o intervalo [inicio - fim] correspondente nos segmentos. "
        "Em resumo_executivo, mantenha uma sintese objetiva e fiel ao conteudo ouvido."
    )
    
    resposta = cliente.models.generate_content(
        model=MODEL,
        contents=[f"Segmentos de fala recebidos:\n{segmentos_str}"],
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.0,
            response_mime_type="application/json",
            response_schema=AnaliseAudio
        )
    )
    
    return AnaliseAudio.model_validate_json(resposta.text or "{}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python dia_22/resumir.py amostras/comando.wav")
        sys.exit(1)
        
    resultado = processar_audio_com_llm(Path(sys.argv[1]))
    print(resultado.model_dump_json(indent=2))