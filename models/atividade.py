from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class CronometroData:
    nome: str = ""
    tempo_decorrido: float = 0.0
    inicio: Optional[datetime] = None
    fim: Optional[datetime] = None
    ativo: bool = False

@dataclass
class Atividade:
    id: str
    descricao: str
    maquina_id: int
    maquina_nome: str
    responsavel: str
    tipo: str = "Setup"
    inicio: Optional[datetime] = None
    fim: Optional[datetime] = None
    status: str = "Pendente"
    cronometro_principal: CronometroData = field(default_factory=lambda: CronometroData("Principal"))
    cronometro_qualidade: CronometroData = field(default_factory=lambda: CronometroData("Qualidade"))
    cronometro_pcd: CronometroData = field(default_factory=lambda: CronometroData("PCD"))

    def iniciar(self):
        self.status = "Em andamento"
        self.inicio = datetime.now()

    def finalizar(self):
        self.status = "Concluído"
        self.fim = datetime.now()

    def pausar(self):
        self.status = "Pausado"

    def retomar(self):
        self.status = "Em andamento"

    def get_resumo(self):
        return {
            'id': self.id,
            'inicio': self.inicio.strftime("%H:%M:%S") if self.inicio else "",
            'fim': self.fim.strftime("%H:%M:%S") if self.fim else ""
        }
