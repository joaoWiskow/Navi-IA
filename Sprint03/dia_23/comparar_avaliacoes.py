import json
from pathlib import Path
from metricas import calcular_metricas
from juiz import julgar_resposta

def rodar_benchmark():
    casos = [
        {
            "nome": "alucinacao_parcial",
            "evidencia": "Print mostra erro 500 no microservico de pagamentos.",
            "resposta": "O microservico de pagamentos deu erro 500 e causou prejuizo de 1 milhao de reais.",
            "verdade": "Erro 500 confirmado em pagamentos. Prejuizo real desconhecido.",
            "nota_humana_groundedness": 0.5
        },
        {
            "nome": "resposta_perfeita",
            "evidencia": "Tabela indica: Filial Porto Alegre faturou R$ 150.000 em setembro.",
            "resposta": "A filial de Porto Alegre registrou faturamento de R$ 150.000 em setembro.",
            "verdade": "Faturamento Porto Alegre setembro: R$ 150.000.",
            "nota_humana_groundedness": 1.0
        }
    ]
    
    relatorio = []
    for c in casos:
        resultado_juiz = julgar_resposta(c["evidencia"], c["resposta"], c["verdade"])
        delta = round(resultado_juiz.nota_groundedness - c["nota_humana_groundedness"], 2)
        relatorio.append({
            "cenario": c["nome"],
            "nota_humana": c["nota_humana_groundedness"],
            "nota_juiz_ia": resultado_juiz.nota_groundedness,
            "delta_discrepancia": delta,
            "alucinacoes": resultado_juiz.alucinacoes_detectadas
        })
        
    Path("dia_23/resultado_benchmark.json").write_text(json.dumps(relatorio, indent=2, ensure_ascii=False))
    print("Benchmark concluido! Arquivo dia_23/resultado_benchmark.json gerado.")

if __name__ == "__main__":
    rodar_benchmark()