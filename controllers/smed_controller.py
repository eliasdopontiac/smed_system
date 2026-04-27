from typing import List, Dict, Optional
from datetime import datetime
from models.maquina import Maquina
from models.atividade import Atividade

class SmedController:
    def __init__(self):
        self.maquinas: List[Maquina] = []
        self.atividades: List[Atividade] = []
        self.responsaveis: List[str] = ["João Silva", "Maria Santos", "Pedro Oliveira"]
        self.contador_atividades = 0

    def adicionar_maquina(self, maquina: Maquina):
        if maquina not in self.maquinas:
            self.maquinas.append(maquina)

    def get_maquinas(self):
        return self.maquinas

    def get_maquina_por_id(self, maquina_id: int):
        for m in self.maquinas:
            if m.id == maquina_id:
                return m
        return None

    def iniciar_atividade(self, maquina_id: int, descricao: str, responsavel: str, tipo: str):
        maquina = self.get_maquina_por_id(maquina_id)
        if not maquina:
            raise ValueError(f"Máquina {maquina_id} não encontrada")

        self.contador_atividades += 1
        atividade = Atividade(
            id=f"ATV{self.contador_atividades:04d}",
            descricao=descricao,
            maquina_id=maquina_id,
            maquina_nome=maquina.nome,
            responsavel=responsavel,
            tipo=tipo,
            inicio=datetime.now(),
            status="Em andamento"
        )

        maquina.status = "Em Setup"
        self.atividades.append(atividade)

        if responsavel not in self.responsaveis:
            self.responsaveis.append(responsavel)

        return atividade

    def get_atividades(self):
        return self.atividades

    def get_responsaveis(self):
        return self.responsaveis

    def atualizar_responsaveis(self, responsaveis):
        self.responsaveis = responsaveis

    def get_estatisticas(self):
        concluidas = [a for a in self.atividades if a.status == "Concluído"]
        em_andamento = [a for a in self.atividades if a.status == "Em andamento"]
        pausadas = [a for a in self.atividades if a.status == "Pausado"]

        tempo_total = sum(a.cronometro_principal.tempo_decorrido for a in concluidas)
        tempo_medio = tempo_total / len(concluidas) if concluidas else 0

        return {
            'total_maquinas': len(self.maquinas),
            'total_atividades': len(self.atividades),
            'atividades_concluidas': len(concluidas),
            'atividades_andamento': len(em_andamento),
            'atividades_pausadas': len(pausadas),
            'tempo_total': tempo_total,
            'tempo_medio': tempo_medio
        }
