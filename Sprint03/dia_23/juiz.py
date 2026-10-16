import json
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

load_dotenv()
MODEL = "gemini-3.5-flash-lite"

class JulgamentoAuditoria(BaseModel):
    nota_groundedness: float = Field(ge=0.0, le=1.0, description="Nota de 0 a 1 indicando quanto a resposta e suportada apenas pela evidencia")
    nota_precisao: float = Field(ge=0.0, le=1.0, description="Nota de 0 a 1 indicando veracidade factual em relacao a verdade de referencia")
    trechos_da_evidencia_usados: list[str] = Field(description="Citacoes literais curtas da evidencia que sustentam a resposta")
    alucinacoes_detectadas: list[str] = Field(description="Afirmacoes feitas na resposta que nao possuem comprovacao na evidencia")
    veredito_final: str = Field(description="Justificativa sintetica do julgamento")

def julgar_resposta(evidencia: str, resposta_candidata: str, verdade_referencia: str) -> JulgamentoAuditoria:
    cliente = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    
    # Instrução de sistema: orientar o Juiz a ser estrito, determinístico e conservador.
    # Deve identificar alucinações, citar trechos literais usados como suporte e atribuir
    # notas de 0.0 a 1.0 conforme regras claras. Seja factual e sucinto.
    system_instruction = (
        "Você é um Juiz Auditor IMPLACÁVEL de respostas de LLM. Execute uma avaliação fria," 
        "determinística e conservadora entre a resposta candidata e a evidência fornecida. "
        "REGRAS DE AVALIAÇÃO (seguir estritamente): "
        "1) Somente considere como 'sustentado pela evidência' aquilo que aparece explicitamente na "
        "evidência fornecida (frases, números, timestamps, nomes). Qualquer afirmação que não esteja "
        "literalmente presente na evidência deve ser marcada como 'alucinação' e listada em "
        "'alucinacoes_detectadas'. Não infira nem suponha informação ausente. "
        "2) Para cada trecho da resposta que você considera suportado, inclua em "
        "'trechos_da_evidencia_usados' a citação literal curta da evidência (máx. 3 frases). "
        "3) Calcule 'nota_groundedness' como: (# afirmações da resposta suportadas pela evidência) / "
        "(total de afirmações da resposta). Valor entre 0.0 e 1.0. Seja numérico com 3 casas decimais. "
        "4) Calcule 'nota_precisao' como: (# afirmações verdadeiras segundo a verdade de referência) / "
        "(total de afirmações da resposta). Não use a evidência para esta métrica — use apenas a "
        "'verdade_absoluta_referencia' fornecida. Valor entre 0.0 e 1.0 com 3 casas decimais. "
        "5) 'alucinacoes_detectadas' deve conter as frases/extras da resposta que não têm suporte literal na evidência. "
        "6) 'veredito_final' deve ser uma justificativa sucinta (1-3 frases) que resuma por que a nota foi dada e "
        "incluir uma recomendação imediata (ex.: 'consultar logs', 'corrigir dados de entrada', 'fornecer evidência adicional'). "
        "FORMATO DA RESPOSTA: Retorne estritamente um JSON compatível com o schema solicitado. "
        "Tono: objetivo, sem floreios, sem desculpas, sem suposições. Temperatura: 0."
    )
    
    payload = json.dumps({
        "evidencia_fornecida": evidencia,
        "resposta_candidata": resposta_candidata,
        "verdade_absoluta_referencia": verdade_referencia
    }, ensure_ascii=False)
    
    resposta = cliente.models.generate_content(
        model=MODEL,
        contents=[payload],
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.0,
            response_mime_type="application/json",
            response_schema=JulgamentoAuditoria
        )
    )
    
    return JulgamentoAuditoria.model_validate_json(resposta.text or "{}")

if __name__ == "__main__":
    evidencia = "A imagem do print mostra: Erro 504 no servico auth-service as 14:10."
    resposta_teste = "Ocorreu um erro 504 no servico de autenticacao as 14:10, e 500 usuarios foram desconectados."
    verdade = "Log oficial: Erro 504 Gateway Timeout em auth-service as 14:10. Total real de desconexoes: 500."
    
    julgamento = julgar_resposta(evidencia, resposta_teste, verdade)
    print(julgamento.model_dump_json(indent=2))