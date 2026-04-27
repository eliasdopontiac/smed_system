"""
Script para criar toda a estrutura do projeto SMED
Execute: python criar_projeto.py
"""

import os


def criar_arquivo(caminho, conteudo):
    """Criar arquivo com conteúdo"""
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(conteudo)
    print(f"  ✅ {caminho}")


def main():
    raiz = "."

    # requirements.txt
    criar_arquivo(f"{raiz}/requirements.txt", "PyQt6==6.6.1\n")

    # main.py
    criar_arquivo(
        f"{raiz}/main.py",
        """import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
if hasattr(Qt, 'HighDpiScaleFactorRoundingPolicy'):
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
from views.main_window import MainWindow
app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
""",
    )

    # models/__init__.py
    criar_arquivo(
        f"{raiz}/models/__init__.py",
        "from .maquina import Maquina\nfrom .atividade import Atividade\n",
    )

    # models/maquina.py
    criar_arquivo(
        f"{raiz}/models/maquina.py",
        """from dataclasses import dataclass
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
""",
    )

    # models/atividade.py
    criar_arquivo(
        f"{raiz}/models/atividade.py",
        """from dataclasses import dataclass, field
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
""",
    )

    # controllers/__init__.py
    criar_arquivo(
        f"{raiz}/controllers/__init__.py",
        "from .smed_controller import SmedController\n",
    )

    # controllers/smed_controller.py
    criar_arquivo(
        f"{raiz}/controllers/smed_controller.py",
        """from typing import List, Dict, Optional
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
""",
    )

    # utils/__init__.py
    criar_arquivo(f"{raiz}/utils/__init__.py", "")

    # utils/constants.py
    criar_arquivo(
        f"{raiz}/utils/constants.py",
        """TEMPO_ATUALIZACAO_MS = 1000
TIPOS_ATIVIDADE = ["Setup", "Troca de Molde", "Manutenção", "Limpeza", "Ajuste"]
""",
    )

    # utils/data_manager.py
    criar_arquivo(
        f"{raiz}/utils/data_manager.py",
        """import json, os

class DataManager:
    @staticmethod
    def salvar_json(data, arquivo):
        os.makedirs(os.path.dirname(arquivo), exist_ok=True)
        with open(arquivo, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def carregar_json(arquivo, default=None):
        if os.path.exists(arquivo):
            with open(arquivo, 'r', encoding='utf-8') as f:
                return json.load(f)
        return default if default is not None else []
""",
    )

    # styles/__init__.py
    criar_arquivo(f"{raiz}/styles/__init__.py", "from .theme import Theme\n")

    # styles/theme.py
    criar_arquivo(
        f"{raiz}/styles/theme.py",
        '''class Theme:
    COR_PRIMARIA = "#1a73e8"
    COR_FUNDO = "#ffffff"
    COR_TEXTO = "#202124"
    COR_BORDA = "#dadce0"
    COR_SUCESSO = "#34a853"
    COR_PERIGO = "#ea4335"
    COR_AVISO = "#f9ab00"

    BOTAO_SUCESSO = """
        QPushButton { background-color: #34a853; color: white; border: none; padding: 8px 15px; border-radius: 4px; font-weight: bold; }
        QPushButton:hover { background-color: #2d9249; }
    """
    BOTAO_PERIGO = """
        QPushButton { background-color: #ea4335; color: white; border: none; padding: 8px 15px; border-radius: 4px; font-weight: bold; }
        QPushButton:hover { background-color: #d33828; }
    """
    BOTAO_PRIMARIO = """
        QPushButton { background-color: #1a73e8; color: white; border: none; padding: 8px 15px; border-radius: 4px; font-weight: bold; }
        QPushButton:hover { background-color: #1557b0; }
    """

    @classmethod
    def get_theme_light(cls):
        return f"""
        QMainWindow {{ background-color: {cls.COR_FUNDO}; }}
        QWidget {{ color: {cls.COR_TEXTO}; font-family: 'Segoe UI', Arial; }}
        QGroupBox {{ font-weight: bold; border: 2px solid {cls.COR_PRIMARIA}; border-radius: 8px; margin-top: 10px; padding-top: 15px; background-color: {cls.COR_FUNDO}; }}
        QGroupBox::title {{ color: {cls.COR_PRIMARIA}; padding: 0 10px; }}
        QLineEdit, QComboBox {{ padding: 8px; border: 2px solid {cls.COR_BORDA}; border-radius: 4px; background-color: white; }}
        QLineEdit:focus {{ border-color: {cls.COR_PRIMARIA}; }}
        QTableWidget {{ border: 1px solid {cls.COR_BORDA}; gridline-color: {cls.COR_BORDA}; }}
        QHeaderView::section {{ background-color: #f8f9fa; padding: 8px; border: 1px solid {cls.COR_BORDA}; font-weight: bold; }}
        QStatusBar {{ background-color: #f8f9fa; border-top: 1px solid {cls.COR_BORDA}; }}
        QScrollBar:vertical {{ width: 12px; background: {cls.COR_FUNDO}; }}
        QScrollBar::handle:vertical {{ background: {cls.COR_BORDA}; border-radius: 6px; }}
        QMenuBar {{ background-color: {cls.COR_FUNDO}; border-bottom: 1px solid {cls.COR_BORDA}; }}
        QMenuBar::item:selected {{ background-color: #e8f0fe; }}
        QMenu {{ background-color: white; border: 1px solid {cls.COR_BORDA}; }}
        QMenu::item:selected {{ background-color: #e8f0fe; }}
        """
''',
    )

    # views/__init__.py
    criar_arquivo(
        f"{raiz}/views/__init__.py",
        "from .main_window import MainWindow\nfrom .cronometro_widget import CronometroWidget\nfrom .dialogs import GerenciadorOperadoresDialog, EstatisticasDialog\n",
    )

    # views/cronometro_widget.py
    criar_arquivo(
        f"{raiz}/views/cronometro_widget.py",
        """from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

class CronometroWidget(QWidget):
    def __init__(self, titulo, cor="#1a73e8", parent=None):
        super().__init__(parent)
        self.titulo = titulo
        self.cor = cor
        self.tempo_decorrido = 0
        self.ativo = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.atualizar_tempo)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(3)
        layout.setContentsMargins(5, 5, 5, 5)

        titulo_label = QLabel(self.titulo)
        titulo_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        titulo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo_label.setStyleSheet(f"color: {self.cor}; border: none; background: transparent;")
        layout.addWidget(titulo_label)

        self.display = QLabel("00:00:00")
        self.display.setFont(QFont("Courier New", 18, QFont.Weight.Bold))
        self.display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.display.setMinimumHeight(35)
        self.display.setStyleSheet(f"color: {self.cor}; background-color: #f8f9fa; border: 2px solid {self.cor}; border-radius: 6px; padding: 6px;")
        layout.addWidget(self.display)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(3)

        self.btn_iniciar = QPushButton("▶")
        self.btn_iniciar.setFixedHeight(25)
        self.btn_iniciar.clicked.connect(self.iniciar)
        self.btn_iniciar.setStyleSheet("QPushButton { background-color: #34a853; color: white; border: none; padding: 3px 8px; border-radius: 3px; font-weight: bold; font-size: 10px; } QPushButton:hover { background-color: #2d9249; } QPushButton:disabled { background-color: #dadce0; }")
        btn_layout.addWidget(self.btn_iniciar)

        self.btn_pausar = QPushButton("⏸")
        self.btn_pausar.setFixedHeight(25)
        self.btn_pausar.clicked.connect(self.pausar)
        self.btn_pausar.setEnabled(False)
        self.btn_pausar.setStyleSheet("QPushButton { background-color: #f9ab00; color: #202124; border: none; padding: 3px 8px; border-radius: 3px; font-weight: bold; font-size: 10px; } QPushButton:hover { background-color: #e09500; } QPushButton:disabled { background-color: #dadce0; }")
        btn_layout.addWidget(self.btn_pausar)

        layout.addLayout(btn_layout)
        self.setLayout(layout)
        self.setStyleSheet("QWidget { background-color: #ffffff; border: 1px solid #dadce0; border-radius: 6px; }")

    def iniciar(self):
        if not self.ativo:
            self.ativo = True
            self.timer.start(1000)
            self.btn_iniciar.setEnabled(False)
            self.btn_pausar.setEnabled(True)

    def pausar(self):
        if self.ativo:
            self.ativo = False
            self.timer.stop()
            self.btn_iniciar.setEnabled(True)
            self.btn_pausar.setEnabled(False)
        else:
            self.iniciar()

    def reset(self):
        self.ativo = False
        self.timer.stop()
        self.tempo_decorrido = 0
        self.display.setText("00:00:00")
        self.btn_iniciar.setEnabled(True)
        self.btn_pausar.setEnabled(False)

    def atualizar_tempo(self):
        if self.ativo:
            self.tempo_decorrido += 1
            h, r = divmod(self.tempo_decorrido, 3600)
            m, s = divmod(r, 60)
            self.display.setText(f"{h:02d}:{m:02d}:{s:02d}")

    def get_tempo(self):
        return self.tempo_decorrido

    def get_tempo_formatado(self):
        h, r = divmod(self.tempo_decorrido, 3600)
        m, s = divmod(r, 60)
        return f"{h:02d}:{m:02d}:{s:02d}"
""",
    )

    # views/dialogs.py
    criar_arquivo(
        f"{raiz}/views/dialogs.py",
        """from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QDialogButtonBox, QListWidget, QMessageBox, QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from styles.theme import Theme

class GerenciadorOperadoresDialog(QDialog):
    operadores_atualizados = pyqtSignal(list)

    def __init__(self, operadores, parent=None):
        super().__init__(parent)
        self.operadores = operadores.copy() if operadores else []
        self.setWindowTitle("Gerenciar Responsáveis")
        self.setModal(True)
        self.setMinimumWidth(400)
        self.setMinimumHeight(450)
        self.setStyleSheet(Theme.get_theme_light())
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        titulo = QLabel("Responsáveis Técnicos")
        titulo.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("color: #1a73e8; padding: 10px;")
        layout.addWidget(titulo)

        self.list_widget = QListWidget()
        self.list_widget.addItems(self.operadores)
        layout.addWidget(QLabel("Cadastrados:"))
        layout.addWidget(self.list_widget)

        add_group = QGroupBox("Adicionar")
        add_layout = QHBoxLayout()
        self.novo_input = QLineEdit()
        self.novo_input.setPlaceholderText("Nome")
        add_layout.addWidget(self.novo_input)
        btn_add = QPushButton("Adicionar")
        btn_add.clicked.connect(self.adicionar)
        btn_add.setStyleSheet(Theme.BOTAO_SUCESSO)
        add_layout.addWidget(btn_add)
        add_group.setLayout(add_layout)
        layout.addWidget(add_group)

        btn_remover = QPushButton("Remover Selecionado")
        btn_remover.clicked.connect(self.remover)
        btn_remover.setStyleSheet(Theme.BOTAO_PERIGO)
        layout.addWidget(btn_remover)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.salvar)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def adicionar(self):
        nome = self.novo_input.text().strip()
        if nome and nome not in self.operadores:
            self.operadores.append(nome)
            self.list_widget.addItem(nome)
            self.novo_input.clear()

    def remover(self):
        item = self.list_widget.currentItem()
        if item:
            self.operadores.remove(item.text())
            self.list_widget.takeItem(self.list_widget.row(item))

    def salvar(self):
        self.operadores_atualizados.emit(self.operadores)
        self.accept()

class EstatisticasDialog(QDialog):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("Estatísticas")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        self.setStyleSheet(Theme.get_theme_light())
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)

        titulo = QLabel("📊 ESTATÍSTICAS")
        titulo.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("color: #1a73e8;")
        layout.addWidget(titulo)

        stats = self.controller.get_estatisticas()

        grupo = QGroupBox("Resumo")
        gl = QVBoxLayout()

        dados = [
            f"Total de Máquinas: {stats['total_maquinas']}",
            f"Total de Atividades: {stats['total_atividades']}",
            f"Concluídas: {stats['atividades_concluidas']}",
            f"Em Andamento: {stats['atividades_andamento']}",
            f"Pausadas: {stats['atividades_pausadas']}"
        ]

        for d in dados:
            lbl = QLabel(f"• {d}")
            lbl.setFont(QFont("Segoe UI", 11))
            lbl.setStyleSheet("padding: 5px;")
            gl.addWidget(lbl)

        # Tempo total
        tt = stats['tempo_total']
        h, r = divmod(int(tt), 3600)
        m, s = divmod(r, 60)
        lbl_tempo = QLabel(f"• Tempo Total: {h:02d}:{m:02d}:{s:02d}")
        lbl_tempo.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        lbl_tempo.setStyleSheet("color: #1a73e8; padding: 5px;")
        gl.addWidget(lbl_tempo)

        tm = stats['tempo_medio']
        if tm > 0:
            h2, r2 = divmod(int(tm), 3600)
            m2, s2 = divmod(r2, 60)
            lbl_medio = QLabel(f"• Tempo Médio: {h2:02d}:{m2:02d}:{s2:02d}")
        else:
            lbl_medio = QLabel("• Tempo Médio: --:--:--")
        lbl_medio.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        lbl_medio.setStyleSheet("color: #1a73e8; padding: 5px;")
        gl.addWidget(lbl_medio)

        grupo.setLayout(gl)
        layout.addWidget(grupo)

        # Tabela de concluídas
        grupo_tab = QGroupBox("Atividades Concluídas")
        tl = QVBoxLayout()
        tabela = QTableWidget()
        tabela.setColumnCount(4)
        tabela.setHorizontalHeaderLabels(["Máquina", "Descrição", "Responsável", "Tempo"])

        concluidas = [a for a in self.controller.get_atividades() if a.status == "Concluído"]
        tabela.setRowCount(len(concluidas))

        for i, atv in enumerate(concluidas):
            tabela.setItem(i, 0, QTableWidgetItem(atv.maquina_nome))
            tabela.setItem(i, 1, QTableWidgetItem(atv.descricao[:35]))
            tabela.setItem(i, 2, QTableWidgetItem(atv.responsavel))
            t = atv.cronometro_principal.tempo_decorrido
            h3, r3 = divmod(int(t), 3600)
            m3, s3 = divmod(r3, 60)
            tabela.setItem(i, 3, QTableWidgetItem(f"{h3:02d}:{m3:02d}:{s3:02d}"))
            for j in range(4):
                tabela.item(i, j).setBackground(QColor("#e8f5e9"))

        header = tabela.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        tl.addWidget(tabela)
        grupo_tab.setLayout(tl)
        layout.addWidget(grupo_tab)

        btn_fechar = QPushButton("Fechar")
        btn_fechar.clicked.connect(self.close)
        btn_fechar.setStyleSheet(Theme.BOTAO_PRIMARIO)
        btn_fechar.setMinimumHeight(35)
        layout.addWidget(btn_fechar)

        self.setLayout(layout)
""",
    )

    # views/main_window.py
    criar_arquivo(
        f"{raiz}/views/main_window.py",
        """from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QScrollArea, QFrame, QMessageBox, QStatusBar, QFileDialog)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QFont
from datetime import datetime
from typing import List
from models.maquina import Maquina
from controllers.smed_controller import SmedController
from views.cronometro_widget import CronometroWidget
from views.dialogs import GerenciadorOperadoresDialog, EstatisticasDialog
from styles.theme import Theme

class ParadaExternaWidget(QFrame):
    removida = pyqtSignal = lambda self, p: None  # simplificado

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tempo_decorrido = 0
        self.ativo = False
        self.finalizado = False
        self.inicio = None
        self.fim = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.atualizar)
        self.setup_ui()

    def setup_ui(self):
        self.setMaximumHeight(80)
        self.setStyleSheet("QFrame { background-color: #fff8e1; border: 1px solid #f9ab00; border-radius: 6px; padding: 6px; margin: 1px; }")
        layout = QVBoxLayout()
        layout.setSpacing(3)
        layout.setContentsMargins(6, 4, 6, 4)

        top = QHBoxLayout()
        self.label_titulo = QLabel("⏸ Parada")
        self.label_titulo.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.label_titulo.setStyleSheet("color: #e67e22; border: none;")
        top.addWidget(self.label_titulo)

        self.display = QLabel("00:00:00")
        self.display.setFont(QFont("Courier New", 14, QFont.Weight.Bold))
        self.display.setStyleSheet("color: #e67e22; border: none;")
        top.addWidget(self.display)
        top.addStretch()

        self.btn_iniciar = QPushButton("▶")
        self.btn_iniciar.setFixedSize(28, 22)
        self.btn_iniciar.clicked.connect(self.iniciar)
        self.btn_iniciar.setStyleSheet("QPushButton { background-color: #34a853; color: white; border: none; border-radius: 3px; font-size: 9px; }")
        top.addWidget(self.btn_iniciar)

        self.btn_pausar = QPushButton("⏸")
        self.btn_pausar.setFixedSize(28, 22)
        self.btn_pausar.clicked.connect(self.pausar)
        self.btn_pausar.setEnabled(False)
        self.btn_pausar.setStyleSheet("QPushButton { background-color: #f9ab00; color: white; border: none; border-radius: 3px; font-size: 9px; }")
        top.addWidget(self.btn_pausar)

        self.btn_finalizar = QPushButton("⏹")
        self.btn_finalizar.setFixedSize(28, 22)
        self.btn_finalizar.clicked.connect(self.finalizar)
        self.btn_finalizar.setEnabled(False)
        self.btn_finalizar.setStyleSheet("QPushButton { background-color: #ea4335; color: white; border: none; border-radius: 3px; font-size: 9px; }")
        top.addWidget(self.btn_finalizar)

        layout.addLayout(top)

        self.frame_desc = QFrame()
        self.frame_desc.setVisible(False)
        self.frame_desc.setStyleSheet("border: none; background: transparent;")
        dl = QHBoxLayout(self.frame_desc)
        dl.setContentsMargins(0, 0, 0, 0)
        self.descricao_input = QLineEdit()
        self.descricao_input.setPlaceholderText("Motivo...")
        self.descricao_input.setMaximumHeight(24)
        self.descricao_input.setStyleSheet("border: 1px solid #dadce0; border-radius: 3px; padding: 2px 6px; font-size: 10px;")
        dl.addWidget(self.descricao_input)
        layout.addWidget(self.frame_desc)
        self.setLayout(layout)

    def iniciar(self):
        if not self.ativo and not self.finalizado:
            self.ativo = True
            self.inicio = datetime.now()
            self.tempo_decorrido = 0
            self.timer.start(1000)
            self.btn_iniciar.setEnabled(False)
            self.btn_pausar.setEnabled(True)
            self.btn_finalizar.setEnabled(True)
            self.frame_desc.setVisible(False)

    def pausar(self):
        if self.ativo:
            self.ativo = False
            self.timer.stop()
            self.btn_iniciar.setEnabled(True)
            self.btn_pausar.setEnabled(False)
        else:
            self.iniciar()

    def finalizar(self):
        if self.ativo:
            self.ativo = False
            self.finalizado = True
            self.timer.stop()
            self.fim = datetime.now()
            self.btn_iniciar.setEnabled(False)
            self.btn_pausar.setEnabled(False)
            self.btn_finalizar.setEnabled(False)
            self.frame_desc.setVisible(True)
            self.descricao_input.setFocus()

    def atualizar(self):
        if self.ativo:
            self.tempo_decorrido += 1
            m, s = divmod(self.tempo_decorrido, 60)
            h, m = divmod(m, 60)
            self.display.setText(f"{h:02d}:{m:02d}:{s:02d}")

    def get_tempo(self):
        return self.tempo_decorrido

    def get_dados(self):
        return {'descricao': self.descricao_input.text() if self.finalizado else "", 'tempo': self.tempo_decorrido, 'inicio': self.inicio.strftime("%H:%M:%S") if self.inicio else "", 'fim': self.fim.strftime("%H:%M:%S") if self.fim else ""}


class BlocoMaquina(QFrame):
    removido = pyqtSignal = lambda self, b: None
    iniciar_atividade = pyqtSignal = lambda self, b: None

    def __init__(self, maquina, parent=None):
        super().__init__(parent)
        self.maquina = maquina
        self.atividade_atual = None
        self.cronometros = []
        self.paradas_externas = []
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(6)
        layout.setContentsMargins(12, 10, 12, 10)

        # Header
        h = QHBoxLayout()
        self.label_titulo = QLabel(f"🏭 {self.maquina.nome}")
        self.label_titulo.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self.label_titulo.setStyleSheet("color: #202124; border: none;")
        h.addWidget(self.label_titulo)

        self.label_status = QLabel(self.maquina.status)
        self.label_status.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        h.addWidget(self.label_status)
        h.addStretch()

        self.label_hora_inicio = QLabel("")
        self.label_hora_inicio.setFont(QFont("Segoe UI", 8))
        self.label_hora_inicio.setStyleSheet("color: #34a853; border: none;")
        self.label_hora_inicio.setVisible(False)
        h.addWidget(self.label_hora_inicio)

        self.label_hora_fim = QLabel("")
        self.label_hora_fim.setFont(QFont("Segoe UI", 8))
        self.label_hora_fim.setStyleSheet("color: #ea4335; border: none;")
        self.label_hora_fim.setVisible(False)
        h.addWidget(self.label_hora_fim)

        btn_x = QPushButton("✕")
        btn_x.setFixedSize(24, 24)
        btn_x.clicked.connect(lambda: self.removido.emit(self))
        btn_x.setStyleSheet("QPushButton { background: transparent; color: #5f6368; border: none; font-size: 12px; font-weight: bold; border-radius: 12px; } QPushButton:hover { background: #fce8e6; color: #ea4335; }")
        h.addWidget(btn_x)
        layout.addLayout(h)

        # Form
        self.frame_form = QFrame()
        self.frame_form.setStyleSheet("border: 1px solid #e0e0e0; border-radius: 6px; padding: 8px;")
        fl = QHBoxLayout(self.frame_form)
        fl.setSpacing(8)
        fl.setContentsMargins(8, 5, 8, 5)

        self.descricao_input = QLineEdit()
        self.descricao_input.setPlaceholderText("Descreva a atividade...")
        self.descricao_input.setMinimumHeight(32)
        fl.addWidget(self.descricao_input, stretch=3)

        self.responsavel_input = QLineEdit()
        self.responsavel_input.setPlaceholderText("Responsável")
        self.responsavel_input.setMinimumHeight(32)
        self.responsavel_input.setMaximumWidth(150)
        fl.addWidget(self.responsavel_input, stretch=1)

        self.btn_iniciar_bloco = QPushButton("▶ INICIAR")
        self.btn_iniciar_bloco.clicked.connect(self.iniciar_click)
        self.btn_iniciar_bloco.setMinimumHeight(32)
        self.btn_iniciar_bloco.setMaximumWidth(120)
        self.btn_iniciar_bloco.setStyleSheet("QPushButton { background-color: #34a853; color: white; border: none; padding: 6px 15px; border-radius: 4px; font-weight: bold; font-size: 11px; } QPushButton:hover { background-color: #2d9249; }")
        fl.addWidget(self.btn_iniciar_bloco)
        layout.addWidget(self.frame_form)

        # Cronômetros
        self.frame_cron = QFrame()
        self.frame_cron.setStyleSheet("border: none;")
        self.frame_cron.setVisible(False)
        cl = QHBoxLayout(self.frame_cron)
        cl.setSpacing(6)
        cl.setContentsMargins(0, 0, 0, 0)

        self.cron_principal = CronometroWidget("Atividade", "#1a73e8")
        self.cron_qualidade = CronometroWidget("Qualidade", "#e67e22")
        self.cron_pcd = CronometroWidget("PCD", "#9b59b6")
        self.cronometros = [self.cron_principal, self.cron_qualidade, self.cron_pcd]

        for c in self.cronometros:
            cl.addWidget(c)
        layout.addWidget(self.frame_cron)

        # Paradas
        self.frame_paradas = QFrame()
        self.frame_paradas.setStyleSheet("border: none;")
        self.frame_paradas.setVisible(False)
        pl = QVBoxLayout(self.frame_paradas)
        pl.setSpacing(3)
        pl.setContentsMargins(0, 0, 0, 0)

        ph = QHBoxLayout()
        self.label_paradas = QLabel("⏸ Paradas Externas")
        self.label_paradas.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.label_paradas.setStyleSheet("color: #e67e22; border: none;")
        ph.addWidget(self.label_paradas)
        ph.addStretch()

        btn_add_p = QPushButton("+ Parada")
        btn_add_p.clicked.connect(self.add_parada)
        btn_add_p.setMaximumHeight(25)
        btn_add_p.setStyleSheet("QPushButton { background-color: #e67e22; color: white; border: none; padding: 3px 10px; border-radius: 3px; font-weight: bold; font-size: 10px; } QPushButton:hover { background-color: #d35400; }")
        ph.addWidget(btn_add_p)
        pl.addLayout(ph)

        self.container_paradas = QWidget()
        self.layout_paradas = QVBoxLayout(self.container_paradas)
        self.layout_paradas.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout_paradas.setSpacing(3)
        self.layout_paradas.setContentsMargins(0, 0, 0, 0)
        pl.addWidget(self.container_paradas)
        layout.addWidget(self.frame_paradas)

        # Controles
        self.frame_ctrl = QFrame()
        self.frame_ctrl.setStyleSheet("border: none;")
        self.frame_ctrl.setVisible(False)
        ctrl_l = QHBoxLayout(self.frame_ctrl)
        ctrl_l.setContentsMargins(0, 0, 0, 0)

        self.btn_pausar = QPushButton("⏸ PAUSAR")
        self.btn_pausar.clicked.connect(self.pausar_click)
        self.btn_pausar.setStyleSheet("QPushButton { background-color: #f9ab00; color: #202124; border: none; padding: 6px 15px; border-radius: 4px; font-weight: bold; font-size: 11px; } QPushButton:hover { background-color: #e09500; }")
        ctrl_l.addWidget(self.btn_pausar)

        self.btn_finalizar = QPushButton("⏹ FINALIZAR")
        self.btn_finalizar.clicked.connect(self.finalizar_click)
        self.btn_finalizar.setStyleSheet("QPushButton { background-color: #ea4335; color: white; border: none; padding: 6px 15px; border-radius: 4px; font-weight: bold; font-size: 11px; } QPushButton:hover { background-color: #d33828; }")
        ctrl_l.addWidget(self.btn_finalizar)
        layout.addWidget(self.frame_ctrl)

        # Resumo
        self.frame_resumo = QFrame()
        self.frame_resumo.setStyleSheet("QFrame { background-color: #e8f5e9; border: 2px solid #34a853; border-radius: 6px; padding: 8px; }")
        self.frame_resumo.setVisible(False)
        rl = QVBoxLayout(self.frame_resumo)
        rl.setSpacing(3)
        rl.setContentsMargins(8, 5, 8, 5)

        self.label_resumo = QLabel("")
        self.label_resumo.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.label_resumo.setStyleSheet("color: #34a853; border: none;")
        self.label_resumo.setWordWrap(True)
        rl.addWidget(self.label_resumo)

        self.label_resumo_p = QLabel("")
        self.label_resumo_p.setFont(QFont("Segoe UI", 9))
        self.label_resumo_p.setStyleSheet("color: #5f6368; border: none;")
        self.label_resumo_p.setWordWrap(True)
        rl.addWidget(self.label_resumo_p)
        layout.addWidget(self.frame_resumo)

        self.setLayout(layout)
        self.atualizar_estilo()

    def atualizar_estilo(self):
        cores = {"Disponível": "#34a853", "Em Setup": "#1a73e8", "Pausado": "#f9ab00"}
        cor = cores.get(self.maquina.status, "#dadce0")
        self.setStyleSheet(f"QFrame {{ background-color: #ffffff; border: 2px solid {cor}; border-radius: 8px; margin: 4px; padding: 5px; }}")
        self.label_status.setText(self.maquina.status)
        self.label_status.setStyleSheet(f"color: {cor}; font-weight: bold; font-size: 9px; padding: 2px 8px; border: 1px solid {cor}; border-radius: 10px; background: transparent;")

    def add_parada(self):
        p = ParadaExternaWidget()
        self.layout_paradas.addWidget(p)
        self.paradas_externas.append(p)

    def iniciar_click(self):
        d = self.descricao_input.text().strip()
        r = self.responsavel_input.text().strip()
        if not d or not r:
            QMessageBox.warning(self, "Aviso", "Preencha todos os campos!")
            return
        self.iniciar_atividade.emit(self)

    def iniciar_cronometros(self):
        agora = datetime.now()
        self.label_hora_inicio.setText(f"Início: {agora.strftime('%H:%M:%S')}")
        self.label_hora_inicio.setVisible(True)
        self.frame_form.setVisible(False)
        self.frame_cron.setVisible(True)
        self.frame_paradas.setVisible(True)
        self.frame_ctrl.setVisible(True)
        self.frame_resumo.setVisible(False)
        self.cron_principal.iniciar()
        self.maquina.status = "Em Setup"
        self.atualizar_estilo()

    def pausar_click(self):
        if self.maquina.status == "Em Setup":
            self.cron_principal.pausar()
            self.btn_pausar.setText("▶ RETOMAR")
            self.maquina.status = "Pausado"
        else:
            self.cron_principal.iniciar()
            self.btn_pausar.setText("⏸ PAUSAR")
            self.maquina.status = "Em Setup"
        self.atualizar_estilo()

    def finalizar_click(self):
        if self.maquina.status not in ["Em Setup", "Pausado"]:
            return

        resposta = QMessageBox.question(self, "Confirmar", "Finalizar atividade?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if resposta != QMessageBox.StandardButton.Yes:
            return

        agora = datetime.now()
        self.label_hora_fim.setText(f"Fim: {agora.strftime('%H:%M:%S')}")
        self.label_hora_fim.setVisible(True)

        tp = self.cron_principal.get_tempo()
        tq = self.cron_qualidade.get_tempo()
        tpc = self.cron_pcd.get_tempo()

        if self.atividade_atual:
            self.atividade_atual.cronometro_principal.tempo_decorrido = tp
            self.atividade_atual.cronometro_qualidade.tempo_decorrido = tq
            self.atividade_atual.cronometro_pcd.tempo_decorrido = tpc
            self.atividade_atual.fim = agora
            self.atividade_atual.status = "Concluído"
            self.atividade_atual.finalizar()

        self.cron_principal.timer.stop()
        self.cron_principal.ativo = False
        self.cron_qualidade.timer.stop()
        self.cron_qualidade.ativo = False
        self.cron_pcd.timer.stop()
        self.cron_pcd.ativo = False

        self.maquina.status = "Disponível"

        h, m, s = tp // 3600, (tp % 3600) // 60, tp % 60
        self.label_resumo.setText(f"✅ CONCLUÍDO | ⏱ {h:02d}:{m:02d}:{s:02d} | 🔍 {tq//60:02d}:{tq%60:02d} | 📏 {tpc//60:02d}:{tpc%60:02d}")
        self.label_resumo_p.setText("")

        self.frame_cron.setVisible(False)
        self.frame_paradas.setVisible(False)
        self.frame_ctrl.setVisible(False)
        self.frame_resumo.setVisible(True)

        self.atualizar_estilo()
        self.cron_principal.reset()
        self.cron_qualidade.reset()
        self.cron_pcd.reset()
        self.btn_pausar.setText("⏸ PAUSAR")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.controller = SmedController()
        self.setWindowTitle("SMED - Controle de Atividades")
        self.setGeometry(100, 100, 1100, 750)
        self.blocos: List[BlocoMaquina] = []
        self.setup_menu()
        self.setup_ui()
        self.setup_status()
        self.setStyleSheet(Theme.get_theme_light())

    def setup_menu(self):
        m = self.menuBar()
        arq = m.addMenu("&Arquivo")
        arq.addAction(QAction("&Nova Máquina (Ctrl+N)", self, triggered=self.add_bloco))
        arq.addAction(QAction("📊 &Exportar Relatório (Ctrl+E)", self, triggered=self.exportar))
        arq.addSeparator()
        arq.addAction(QAction("&Sair (Ctrl+Q)", self, triggered=self.close))

        ger = m.addMenu("&Gerenciar")
        ger.addAction(QAction("&Responsáveis", self, triggered=self.gerenciar_resp))

        vis = m.addMenu("&Visualizar")
        vis.addAction(QAction("&Estatísticas", self, triggered=self.estatisticas))

        ajuda = m.addMenu("&Ajuda")
        ajuda.addAction(QAction("&Sobre", self, triggered=self.sobre))

    def setup_ui(self):
        cw = QWidget()
        self.setCentralWidget(cw)
        ml = QVBoxLayout(cw)

        # Header
        h = QHBoxLayout()
        t = QLabel("SISTEMA SMED")
        t.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        t.setStyleSheet("color: #1a73e8;")
        h.addWidget(t)
        h.addStretch()

        btn_exp = QPushButton("📊 Exportar")
        btn_exp.clicked.connect(self.exportar)
        btn_exp.setStyleSheet("QPushButton { background-color: #3498db; color: white; border: none; padding: 10px 18px; border-radius: 6px; font-weight: bold; font-size: 12px; } QPushButton:hover { background-color: #2980b9; }")
        h.addWidget(btn_exp)

        self.btn_add = QPushButton("+ NOVA MÁQUINA")
        self.btn_add.clicked.connect(self.add_bloco)
        self.btn_add.setStyleSheet("QPushButton { background-color: #1a73e8; color: white; border: none; padding: 10px 18px; border-radius: 6px; font-weight: bold; font-size: 12px; } QPushButton:hover { background-color: #1557b0; }")
        h.addWidget(self.btn_add)
        ml.addLayout(h)

        # Scroll
        sa = QScrollArea()
        sa.setWidgetResizable(True)
        sa.setStyleSheet("QScrollArea { border: none; background-color: #f8f9fa; }")

        self.container = QWidget()
        self.lb = QVBoxLayout(self.container)
        self.lb.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.lb.setSpacing(5)
        sa.setWidget(self.container)
        ml.addWidget(sa)

        # Vazio
        self.lbl_vazio = QLabel("Nenhuma máquina adicionada\n\nClique em '+ NOVA MÁQUINA' ou pressione Ctrl+N\npara adicionar uma máquina e iniciar uma atividade SMED")
        self.lbl_vazio.setFont(QFont("Segoe UI", 14))
        self.lbl_vazio.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_vazio.setStyleSheet("color: #5f6368; padding: 60px; border: 2px dashed #dadce0; border-radius: 12px; background-color: #ffffff; margin: 20px;")
        self.lb.addWidget(self.lbl_vazio)

    def setup_status(self):
        self.sb = QStatusBar()
        self.setStatusBar(self.sb)
        self.sb_label = QLabel("Pronto")
        self.sb.addWidget(self.sb_label)
        self.sb_count = QLabel("Máquinas: 0")
        self.sb.addPermanentWidget(self.sb_count)
        self.sb_hora = QLabel(datetime.now().strftime("%H:%M:%S"))
        self.sb.addPermanentWidget(self.sb_hora)
        self.timer_hora = QTimer()
        self.timer_hora.timeout.connect(lambda: self.sb_hora.setText(datetime.now().strftime("%H:%M:%S")))
        self.timer_hora.start(1000)

    def add_bloco(self):
        if self.lbl_vazio.isVisible():
            self.lb.removeWidget(self.lbl_vazio)
            self.lbl_vazio.setVisible(False)

        n = len(self.blocos) + 1
        maq = Maquina(id=n, nome=f"Máquina {n:02d}")
        b = BlocoMaquina(maq)
        b.removido.connect(self.rem_bloco)
        b.iniciar_atividade.connect(self.ini_bloco)

        self.lb.addWidget(b)
        self.blocos.append(b)
        self.controller.adicionar_maquina(maq)
        self.sb_label.setText(f"{maq.nome} adicionada")
        self.sb_count.setText(f"Máquinas: {len(self.blocos)}")

    def rem_bloco(self, b):
        r = QMessageBox.question(self, "Confirmar", f"Remover {b.maquina.nome}?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if r == QMessageBox.StandardButton.Yes:
            self.lb.removeWidget(b)
            self.blocos.remove(b)
            b.deleteLater()
            if len(self.blocos) == 0:
                self.lbl_vazio.setVisible(True)
            self.sb_count.setText(f"Máquinas: {len(self.blocos)}")

    def ini_bloco(self, b):
        try:
            atv = self.controller.iniciar_atividade(b.maquina.id, b.descricao_input.text().strip(), b.responsavel_input.text().strip(), "Setup")
            b.atividade_atual = atv
            b.iniciar_cronometros()
            self.sb_label.setText(f"✅ Atividade iniciada em {b.maquina.nome}")
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))

    def exportar(self):
        import csv, subprocess
        dados = []
        for b in self.blocos:
            info = {'maquina': b.maquina.nome, 'status': b.maquina.status}
            info['descricao'] = b.descricao_input.text() or "-"
            info['responsavel'] = b.responsavel_input.text() or "-"
            info['inicio'] = b.label_hora_inicio.text().replace("Início: ", "") if b.label_hora_inicio.isVisible() else "-"
            info['fim'] = b.label_hora_fim.text().replace("Fim: ", "") if b.label_hora_fim.isVisible() else "-"
            info['tempo_total'] = b.cron_principal.get_tempo_formatado() if b.frame_resumo.isVisible() else "-"
            info['tempo_qualidade'] = b.cron_qualidade.get_tempo_formatado() if b.frame_resumo.isVisible() else "-"
            info['tempo_pcd'] = b.cron_pcd.get_tempo_formatado() if b.frame_resumo.isVisible() else "-"
            info['paradas'] = " | ".join([f"{p.get_dados()['descricao']} ({p.get_tempo()}s)" for p in b.paradas_externas if p.finalizado]) or "-"
            dados.append(info)

        if not dados:
            QMessageBox.warning(self, "Aviso", "Sem dados!")
            return

        arquivo, _ = QFileDialog.getSaveFileName(self, "Exportar", f"relatorio_smed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", "CSV (*.csv)")
        if not arquivo:
            return

        with open(arquivo, 'w', newline='', encoding='utf-8-sig') as f:
            w = csv.writer(f, delimiter=';')
            w.writerow(["Máquina", "Status", "Descrição", "Responsável", "Início", "Fim", "Tempo Total", "Tempo Qualidade", "Tempo PCD", "Paradas"])
            for d in dados:
                w.writerow([d['maquina'], d['status'], d['descricao'], d['responsavel'], d['inicio'], d['fim'], d['tempo_total'], d['tempo_qualidade'], d['tempo_pcd'], d['paradas']])

        self.sb_label.setText(f"✅ Exportado: {arquivo}")
        if QMessageBox.question(self, "Sucesso", f"Relatório exportado!\n\nAbrir arquivo?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            subprocess.Popen(['start', arquivo], shell=True)

    def gerenciar_resp(self):
        d = GerenciadorOperadoresDialog(self.controller.get_responsaveis(), self)
        d.operadores_atualizados.connect(self.controller.atualizar_responsaveis)
        d.exec()

    def estatisticas(self):
        EstatisticasDialog(self.controller, self).exec()

    def sobre(self):
        QMessageBox.about(self, "Sobre", "SMED System v2.0\\n\\nSistema de controle de atividades SMED\\ncom cronômetros independentes.")
""",
    )

    print("\n✅ Projeto criado com sucesso!")
    print("\nExecute:")
    print("  pip install PyQt6")
    print("  python main.py")


if __name__ == "__main__":
    main()
