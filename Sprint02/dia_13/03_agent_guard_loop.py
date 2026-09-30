import importlib

nucleo = importlib.import_module("01_react_loop")


def buscar_registro(id_registro: str) -> dict:
    """Busca um registro de cliente pelo ID no sistema legado."""
    raise LookupError(f"Registro {id_registro} nao encontrado")


FERRAMENTAS = {"buscar_registro": buscar_registro}


class GuardaDeRepeticao:
    """Detecta quando o agente insiste na mesma chamada com os mesmos argumentos."""

    def __init__(self, limite: int = 2):
        self.limite = limite
        self.ultima = None
        self.repeticoes = 0

    def __call__(self, nome: str, args: dict):
        assinatura = (nome, tuple(sorted(args.items())))

        # TODO: se assinatura for igual a self.ultima, incremente self.repeticoes;
        #       senao zere e atualize self.ultima
        if assinatura == self.ultima:
            self.repeticoes += 1
        else:
            self.ultima = assinatura
            self.repeticoes = 0

        # TODO: se self.repeticoes >= self.limite, retorne um aviso pedindo
        #       que o modelo MUDE DE ESTRATEGIA ou encerre informando ao
        #       usuario que a acao e impossivel

        if self.repeticoes >= self.limite:
            return (
                f"O agente repetiu a ferramenta '{nome}' com os mesmos "
                "argumentos. Mude de estrategia ou informe ao usuario "
                "que a acao e impossivel."
            )

        return None


CASOS = [
    "Busque o registro R-999 e me diga o nome do cliente.",
    "Tente de novo o registro R-999 ate conseguir. Nao desista.",
]

if __name__ == "__main__":
    for pergunta in CASOS:
        guarda = GuardaDeRepeticao()
        texto, historico = nucleo.rodar_agente(
            pergunta, FERRAMENTAS, max_iterations=5, antes_de_executar=guarda
        )
        print("PERGUNTA:", pergunta)
        print("RESPOSTA:", texto)
        print("Mensagens no historico:", len(historico))
        print("-" * 60)