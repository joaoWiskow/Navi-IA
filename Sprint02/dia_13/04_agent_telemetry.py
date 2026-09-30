import importlib
import time

nucleo = importlib.import_module("01_react_loop")
chained = importlib.import_module("02_chained_tools_agent")

VERDE, AMARELO, CINZA, RESET = "\033[92m", "\033[93m", "\033[90m", "\033[0m"
class Telemetria:
    def __init__(self):
        self.turnos = []

    def __call__(self, turno: int, response, segundos: float):
        uso = response.usage_metadata

        # TODO: guarde em self.turnos um dicionario com: turno, segundos, tokens_prompt (uso.prompt_token_count),
        #       tokens_total (uso.total_token_count) e ferramentas (lista de nomes em response.function_calls, ou [])

        ferramentas = [chamada.name for chamada in (response.function_calls or [])]

        dados = {
            "turno": turno,
            "segundos": segundos,
            "tokens_prompt": uso.prompt_token_count,
            "tokens_total": uso.total_token_count,
            "ferramentas": ferramentas,
        }

        self.turnos.append(dados)

        # TODO: imprima uma linha colorida por turno: numero, tempo em segundos e ferramentas chamadas

        print(
            f"{AMARELO}[Turno {turno}] "
            f"{segundos:.2f}s | "
            f"Ferramentas: {', '.join(ferramentas) if ferramentas else 'nenhuma'}"
            f"{RESET}"
        )

    def relatorio(self):
        print(f"{VERDE}=== Relatorio do agente ==={RESET}")

        # TODO: imprima o total de turnos, o tempo total, o total de tokens do ultimo turno
        #       (o contexto acumulado) e o turno mais lento

        total_turnos = len(self.turnos)
        tempo_total = sum(t["segundos"] for t in self.turnos)
        tokens_ultimo = self.turnos[-1]["tokens_total"]
        turno_lento = max(self.turnos, key=lambda t: t["segundos"])

        print(f"Total de turnos: {total_turnos}")
        print(f"Tempo total: {tempo_total:.2f}s")
        print(f"Tokens do ultimo turno: {tokens_ultimo}")
        print(
            f"Turno mais lento: {turno_lento['turno']} "
            f"({turno_lento['segundos']:.2f}s)"
        )
        
if __name__ == "__main__":
    telemetria = Telemetria()
    inicio = time.perf_counter()
    texto, _ = nucleo.rodar_agente(
        "Quanto a usuaria maria@empresa.com gastou no total?",
        chained.FERRAMENTAS,
        ao_fim_do_turno=telemetria,
    )
    print(texto)
    telemetria.relatorio()
    print(f"{CINZA}Tempo de parede: {time.perf_counter() - inicio:.2f}s{RESET}")