import importlib

nucleo = importlib.import_module("01_react_loop")

USUARIOS = {"maria@empresa.com": "U-104", "joao@empresa.com": "U-221"}
PEDIDOS = {
    "U-104": [{"pedido": "P-1", "valor": 120.0}, {"pedido": "P-2", "valor": 89.9}, {"pedido": "P-3", "valor": 310.1}],
    "U-221": [{"pedido": "P-9", "valor": 45.0}],
}


def buscar_id_usuario(email: str) -> str:
    """Retorna o ID interno de um usuario a partir do e-mail cadastrado."""
    # TODO: retorne USUARIOS[email]; se nao existir, levante ValueError("Usuario nao encontrado")
    ...
    if not USUARIOS[email]:
        raise ValueError("Sem email relacionado")
    return USUARIOS[email]


def listar_pedidos_usuario(id_usuario: str) -> list[dict]:
    """Lista os pedidos de um usuario a partir do ID interno (formato U-123)."""
    return PEDIDOS.get(id_usuario, [])


def calcular_total_gasto(valores: list[float]) -> float:
    """Soma uma lista de valores em reais e retorna o total arredondado a 2 casas."""

    soma = 0.0

    for val in valores:
        soma += val
    return round(soma, 2)


FERRAMENTAS = {
    "buscar_id_usuario": buscar_id_usuario,
    "listar_pedidos_usuario": listar_pedidos_usuario,
    "calcular_total_gasto": calcular_total_gasto,
}


def nomes_das_ferramentas_chamadas(historico) -> list[str]:
    """Percorre o historico e retorna, em ordem, o nome de cada function_call feita pelo modelo."""
    nomes = []
    for mensagem in historico:
        for parte in mensagem.parts:
            # TODO: se parte.function_call existir, acrescente parte.function_call.name em nomes
            if parte.function_call:
                nomes.append(parte.function_call.name)
            
    return nomes


if __name__ == "__main__":
    texto, historico = nucleo.rodar_agente("Quanto a usuaria maria@empresa.com gastou no total?", FERRAMENTAS)
    print(texto)
    sequencia = nomes_das_ferramentas_chamadas(historico)
    print("Sequencia de ferramentas:", " -> ".join(sequencia))
    # TODO: verifique com assert que "buscar_id_usuario" veio ANTES de "listar_pedidos_usuario"
    # e que esta veio ANTES de "calcular_total_gasto"
    assert sequencia.index("buscar_id_usuario") < sequencia.index("listar_pedidos_usuario")
    assert sequencia.index("listar_pedidos_usuario") < sequencia.index("calcular_total_gasto")