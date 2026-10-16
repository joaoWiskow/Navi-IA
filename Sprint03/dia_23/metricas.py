import json

def calcular_metricas(afirmacoes: set[str], suportadas: set[str], verdadeiras: set[str]) -> dict[str, float]:
    """Calcula taxas normalizadas entre 0.0 e 1.0."""
    if not afirmacoes:
        return {"groundedness": 0.0, "precisao_factual": 0.0}
        
    taxa_groundedness = len(afirmacoes & suportadas) / len(afirmacoes)
    taxa_precisao = len(afirmacoes & verdadeiras) / len(afirmacoes)
    
    return {
        "groundedness": round(taxa_groundedness, 3),
        "precisao_factual": round(taxa_precisao, 3)
    }

def simular_cenario_auditoria() -> dict:
    # Cenário: Analisando uma nota fiscal e um chamado de suporte
    evidencia_disponivel = "A imagem mostra o produto A101 custando R$ 25,00. O estoque nao e informado."
    verdade_absoluta = "Catalogo de Estoque: A101 custa R$ 25,00 e temos 3 unidades em estoque."
    
    # O modelo respondeu: "O produto A101 custa R$ 25,00 e temos 3 unidades prontas para entrega."
    # Afirmações atômicas:
    # c1 = "A101 custa R$ 25,00" (consta na evidencia e e verdade no mundo)
    # c2 = "Temos 3 unidades" (E VERDADE no mundo, MAS NAO CONSTA na evidencia fornecida!)
    claims = {"c1": "A101 custa R$25", "c2": "Temos 3 unidades"}
    
    # Adicionando c3 = "A garantia é de 10 anos" (Falsa e sem suporte)
    claims["c3"] = "A garantia é de 10 anos"

    resultado = calcular_metricas(
        afirmacoes=set(claims.keys()),
        suportadas={"c1"},           # Apenas c1 esta sustentada pela imagem
        verdadeiras={"c1", "c2"}     # c3 é falsa, portanto não consta nas verdadeiras
    )
    
    return {
        "evidencia": evidencia_disponivel,
        "verdade": verdade_absoluta,
        "afirmacoes_analisadas": claims,
        "metricas": resultado
    }

if __name__ == "__main__":
    print(json.dumps(simular_cenario_auditoria(), indent=2, ensure_ascii=False))