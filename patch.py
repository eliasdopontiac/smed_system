with open('views/main_window.py', 'r', encoding='utf-8') as f:
    text = f.read()

bad = """        self.lbl_vazio = QLabel("Nenhuma máquina adicionada

Clique em '+ NOVA MÁQUINA' ou pressione Ctrl+N
para adicionar uma máquina e iniciar uma atividade SMED")"""
good = '        self.lbl_vazio = QLabel("Nenhuma máquina adicionada\n\nClique em \\'+ NOVA MÁQUINA\\' ou pressione Ctrl+N\npara adicionar uma máquina e iniciar uma atividade SMED")'

text = text.replace(bad, good)
with open('views/main_window.py', 'w', encoding='utf-8') as f:
    f.write(text)
