from dataclasses import dataclass
from datetime import datetime

@dataclass
class Maquina:
    id: int
    nome: str
    status: str = "Disponível"
    total_atividades: int = 0
    tempo_total_setup: float = 0.0

    def iniciar_atividade(self):
        if self.status == "Disponível":
            self.status = "Em Setup"
            return True
        return False

    def finalizar_atividade(self, tempo: float):
        self.status = "Disponível"
        self.total_atividades += 1
        self.tempo_total_setup += tempo

    def get_tempo_medio(self):
        return self.tempo_total_setup / self.total_atividades if self.total_atividades > 0 else 0
