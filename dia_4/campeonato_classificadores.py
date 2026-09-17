import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODELO_FLASH = "gemini-3.1-flash-lite"

CASOS_TESTE = [
    {
        "id": 1,
        "texto": "URGENTE!!! SOCORRO!! Preciso que alterem a foto do meu perfil agora para a reuniao das 15h!",
        "urgencia_esperada": "BAIXA",
        "motivo": "Falsa urgencia emocional. Impacto operacional nulo nas atividades da empresa."
    },
    {
        "id": 2,
        "texto": "A API de pagamentos esta retornando HTTP 500 para 35% das requisicoes desde as 14h.",
        "urgencia_esperada": "ALTA",
        "motivo": "Incidente critico em producao com perda direta de receita e impacto a clientes."
    },
    {
        "id": 3,
        "texto": "O botao de exportar relatorio em Excel sumiu na versao desktop, mas funciona via web.",
        "urgencia_esperada": "MEDIA",
        "motivo": "Falha de funcionalidade secundaria com solucao de contorno (workaround) ativa."
    },
    {
        "id": 4,
        "texto": "Recebi um e-mail de alerta e ao logar estou vendo os dados cadastrais de outro cliente.",
        "urgencia_esperada": "ALTA",
        "motivo": "Incidente de seguranca grave com exposicao de dados sensiveis (violacao LGPD)."
    },
    {
        "id": 5,
        "texto": "Seria interessante se o fundo do painel tivesse uma opcao de modo escuro.",
        "urgencia_esperada": "BAIXA",
        "motivo": "Sugestao de melhoria visual (feature request), sem nenhum impacto operacional."
    },
    {
        "id": 6,
        "texto": "A emissao de notas fiscais eletronicas travou ha 30 minutos com 800 notas na fila.",
        "urgencia_esperada": "ALTA",
        "motivo": "Parada operacional bloqueante em processo fiscal de alta criticidade."
    },
    {
        "id": 7,
        "texto": "O tempo de carregamento da listagem de produtos subiu de 1.2s para 3.8s no pico.",
        "urgencia_esperada": "MEDIA",
        "motivo": "Degradacao de desempenho perceptivel, mas sem indisponibilidade de servico."
    },
    {
        "id": 8,
        "texto": "Parabens a equipe, a nova atualizacao do painel ficou muito mais rapida e intuitiva!",
        "urgencia_esperada": "BAIXA",
        "motivo": "Mensagem de feedback positivo. Nao requer intervencao tecnica de suporte."
    },
    {
        "id": 9,
        "texto": "Um usuario nao consegue redefinir a senha porque o link recebido expira em 2 minutos.",
        "urgencia_esperada": "MEDIA",
        "motivo": "Bug que bloqueia um usuario especifico, com fluxo de atendimento alternativo."
    },
    {
        "id": 10,
        "texto": "Detectamos tentativas nao autenticadas acessando o endpoint /internal/admin/metrics.",
        "urgencia_esperada": "ALTA",
        "motivo": "Atividade anomala indicando reconhecimento ou tentativa ativa de invasao."
    }
]

def classificar_zero_shot(texto_chamado: str) -> str:
    prompt = f"""
Voce e um triador tecnico de suporte de TI.
Classifique a urgencia do chamado estritamente como BAIXA, MEDIA ou ALTA.
Considere o impacto operacional real do incidente, ignorando o desespero emocional do usuario.
Responda APENAS com a palavra da categoria (BAIXA, MEDIA ou ALTA).

Chamado: "{texto_chamado}"
Urgencia:"""
    response = client.models.generate_content(
        model=MODELO_FLASH,
        contents=prompt
    )
    return response.text.strip().upper()

def classificar_few_shot_cot(texto_chamado: str) -> str:
    prompt = f"""
Voce e um triador senior de incidentes de TI corporativo.
Analise a urgencia operacional real (BAIXA, MEDIA ou ALTA), avaliando impacto e abrangencia.

Exemplo 1:
Chamado: "PELO AMOR DE DEUS ME AJUDEM! Meu mouse sem fio parou de funcionar e tenho reuniao hoje!"
Raciocinio: O usuario expressa panico emocional, mas trata-se de periferico individual com facil substituicao fisica. Impacto corporativo nulo.
Urgencia: BAIXA

Exemplo 2:
Chamado: "Constatamos lentidao no servico de autenticacao SSO afetando 60% da empresa inteira."
Raciocinio: Afeta a maioria dos colaboradores bloqueando acessos a ferramentas de trabalho. Gravidade estrutural alta.
Urgencia: ALTA

Exemplo 3:
Chamado: "O grafico semanal de vendas nao atualizou automaticamente, mas o relatorio em PDF baixa normal."
Raciocinio: Inconveniente em funcionalidade secundaria com alternativa funcional direta disponivel.
Urgencia: MEDIA

Agora analise o chamado abaixo. Apresente uma linha curta de raciocinio e finalize com "Urgencia: [CATEGORIA]".

Chamado: "{texto_chamado}"
"""
    response = client.models.generate_content(
        model=MODELO_FLASH,
        contents=prompt
    )
    saida = response.text.strip()
    for linha in reversed(saida.split("\n")):
        linha_upper = linha.upper()
        if "URGENCIA:" in linha_upper:
            for categoria in ["ALTA", "MEDIA", "BAIXA"]:
                if categoria in linha_upper:
                    return categoria
    for categoria in ["ALTA", "MEDIA", "BAIXA"]:
        if categoria in saida.upper():
            return categoria
    return "DESCONHECIDO"

def executar_campeonato():
    print("=" * 70)
    print("CAMPEONATO DE CLASSIFICADORES: ZERO-SHOT vs FEW-SHOT + CoT")
    print("=" * 70)
    
    placar = {"zero_shot": 0, "few_shot_cot": 0}
    
    for item in CASOS_TESTE:
        cid = item["id"]
        texto = item["texto"]
        esperado = item["urgencia_esperada"]
        
        pred_zero = classificar_zero_shot(texto)
        pred_cot = classificar_few_shot_cot(texto)
        
        ok_zero = (esperado in pred_zero)
        ok_cot = (esperado in pred_cot)
        
        if ok_zero:
            placar["zero_shot"] += 1
        if ok_cot:
            placar["few_shot_cot"] += 1
            
        print(f"\n[Chamado #{cid}]")
        print(f"Texto: \"{texto}\"")
        print(f"Gabarito: {esperado} ({item['motivo']})")
        print(f"  - Zero-Shot:     {pred_zero} -> {'CORRETO' if ok_zero else 'ERROU'}")
        print(f"  - Few-Shot+CoT:  {pred_cot} -> {'CORRETO' if ok_cot else 'ERROU'}")

    total = len(CASOS_TESTE)
    acc_zero = (placar["zero_shot"] / total) * 100
    acc_cot = (placar["few_shot_cot"] / total) * 100

    print("\n" + "=" * 70)
    print("RESULTADO FINAL DO CAMPEONATO:")
    print(f"Zero-Shot:        {placar['zero_shot']}/{total} acertos ({acc_zero:.1f}%)")
    print(f"Few-Shot + CoT:   {placar['few_shot_cot']}/{total} acertos ({acc_cot:.1f}%)")
    print("=" * 70)

if __name__ == "__main__":
    executar_campeonato()