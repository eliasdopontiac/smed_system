# SMED System — Sistema de Controle de Atividades

Sistema desktop para controle de atividades **SMED** (Single Minute Exchange of Die) em ambiente industrial. Gerencia múltiplas máquinas com cronômetros independentes, paradas externas e exportação de relatórios.

---

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Funcionalidades](#funcionalidades)
- [Tecnologias](#tecnologias)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Instalação](#instalação)
- [Como Usar](#como-usar)
- [Exportação CSV](#exportação-csv)
- [Atalhos de Teclado](#atalhos-de-teclado)

---

## Visão Geral

O SMED System permite monitorar em tempo real o tempo de setup de máquinas industriais. Cada máquina possui um bloco independente com:

- Cronômetro principal da atividade
- Cronômetro de tempo de qualidade
- Cronômetro de PCD (tempo de processo)
- Registro de paradas externas com motivo
- Resumo ao finalizar com todos os tempos

![Interface Principal](docs/screenshot.png)

---

## Funcionalidades

### Máquinas
- ➕ Adicionar múltiplas máquinas simultaneamente
- 🏷️ Descrição da atividade exibida no cabeçalho do bloco
- 🟢 Badge de status em tempo real: **Disponível**, **Em Setup**, **Pausado**
- ❌ Remover máquina com confirmação

### Cronômetros
- **Atividade** — cronômetro principal, controlado pelo botão PAUSAR/RETOMAR
- **Qualidade** — acionado manualmente, independente
- **PCD** — acionado manualmente, independente
- Ao pausar a atividade, **todos os cronômetros em execução são pausados** simultaneamente

### Paradas Externas
- Adicionar paradas a qualquer momento durante a atividade
- Cada parada tem seus próprios controles: iniciar, pausar e finalizar
- Campo de motivo aparece após finalizar a parada
- O tempo de parada é acumulado corretamente ao pausar e retomar

### Resumo ao Finalizar
- Exibe tempo total de atividade, qualidade e PCD
- Lista todas as paradas externas com motivo e duração
- Horários de início e fim registrados no cabeçalho

### Estatísticas
- Total de máquinas, atividades, concluídas, em andamento e pausadas
- Tempo total e tempo médio das atividades concluídas
- Tabela detalhada com todas as atividades finalizadas

### Gerenciar Responsáveis
- Cadastrar e remover responsáveis técnicos
- Lista persistente durante a sessão

### Exportação CSV
- Relatório com dados de todas as máquinas
- Separador ponto-e-vírgula (compatível com Excel)
- Encoding UTF-8 com BOM (acentos corretos no Windows)
- Opção de abrir o arquivo direto após exportar

---

## Tecnologias

| Tecnologia | Versão | Uso |
|---|---|---|
| Python | 3.12 | Linguagem principal |
| PyQt6 | 6.6.1+ | Interface gráfica |

Arquitetura **MVC**:
- **Models** — `Maquina`, `Atividade`, `CronometroData`
- **Views** — janela principal, widgets, diálogos
- **Controllers** — lógica de negócio, estatísticas

---

## Estrutura do Projeto

```
smed_system/
│
├── main.py                    # Ponto de entrada da aplicação
├── requirements.txt           # Dependências Python
│
├── models/
│   ├── maquina.py             # Classe Maquina (id, nome, status, contadores)
│   └── atividade.py           # Classe Atividade + CronometroData
│
├── views/
│   ├── main_window.py         # Janela principal, BlocoMaquina, ParadaExternaWidget
│   ├── cronometro_widget.py   # Widget de cronômetro reutilizável
│   └── dialogs.py             # Diálogos: Estatísticas e Gerenciar Responsáveis
│
├── controllers/
│   └── smed_controller.py     # Lógica de negócio e estatísticas
│
├── styles/
│   └── theme.py               # Sistema de cores, botões e stylesheet global
│
└── utils/
    └── constants.py           # Constantes globais
```

---

## Instalação

### Pré-requisitos

- **Python 3.12** instalado  
  Verifique: `python --version`  
  Caso o comando não funcione no Windows, localize o executável:
  ```
  C:\Users\<usuario>\AppData\Local\Programs\Python\Python312\python.exe
  ```

> ⚠️ **Windows:** Se `python` abrir a Microsoft Store em vez de rodar, desative o alias em:  
> Configurações → Aplicativos → Configurações avançadas do aplicativo → Aliases de execução do aplicativo

### Passo a passo

**1. Clone o repositório**
```bash
git clone https://github.com/seu-usuario/smed_system.git
cd smed_system
```

**2. Crie o ambiente virtual**
```bash
python -m venv .venv
```

**3. Ative o ambiente virtual**

Windows (PowerShell):
```powershell
.\.venv\Scripts\Activate.ps1
```

Windows (CMD):
```cmd
.venv\Scripts\activate.bat
```

Linux / macOS:
```bash
source .venv/bin/activate
```

**4. Instale as dependências**
```bash
pip install -r requirements.txt
```

**5. Execute a aplicação**
```bash
python main.py
```

Ou sem ativar o venv (Windows):
```bash
.venv\Scripts\python.exe main.py
```

### Executar via Zed (task)

Se estiver usando o editor **Zed**, pressione `Ctrl+Shift+B` e selecione:

- **▶ Rodar SMED** — inicia a aplicação
- **📦 Instalar dependências** — executa o pip install
- **🐍 Criar ambiente virtual** — cria o .venv

---

## Como Usar

### 1. Adicionar uma máquina
Clique em **＋ Nova Máquina** no cabeçalho ou pressione `Ctrl+N`.  
Um bloco aparece com formulário de descrição e responsável.

### 2. Iniciar uma atividade
Preencha a **descrição** e o **responsável**, depois clique em **▶ INICIAR**.  
O formulário é substituído pelos cronômetros. A descrição aparece no cabeçalho do bloco.

### 3. Controlar os cronômetros
- **Atividade** — inicia automaticamente. Use **⏸ PAUSAR** para pausar/retomar.
- **Qualidade / PCD** — clique em **▶ Iniciar** dentro de cada card individualmente.
- Pausar a atividade pausa **todos** os cronômetros em execução.

### 4. Registrar paradas externas
Clique em **+ Parada** para adicionar uma parada.  
Use os botões ▶ ⏸ ⏹ para controlar cada parada.  
Após finalizar, preencha o **motivo** no campo que aparece.

### 5. Finalizar a atividade
Clique em **⏹ FINALIZAR** e confirme.  
O resumo exibe os tempos totais, qualidade, PCD e as paradas registradas.

### 6. Remover uma máquina
Clique no botão **×** no canto superior direito do bloco.

---

## Exportação CSV

Clique em **📊 Exportar** ou pressione `Ctrl+E`.

O relatório gerado contém as colunas:

| Coluna | Descrição |
|---|---|
| Máquina | Nome da máquina |
| Status | Status atual |
| Descrição | Descrição da atividade |
| Responsável | Nome do responsável |
| Início | Horário de início |
| Fim | Horário de finalização |
| Tempo Total | Duração total da atividade (HH:MM:SS) |
| Tempo Qualidade | Tempo do cronômetro de qualidade |
| Tempo PCD | Tempo do cronômetro de PCD |
| Paradas | Lista de paradas com motivo e duração |

> 💡 O separador é `;` (ponto-e-vírgula), compatível com Excel em PT-BR.

---

## Atalhos de Teclado

| Atalho | Ação |
|---|---|
| `Ctrl+N` | Nova máquina |
| `Ctrl+E` | Exportar relatório CSV |
| `Ctrl+T` | Abrir estatísticas |
| `Ctrl+Q` | Fechar aplicação |

---

## Observações

- **Dados em memória:** o sistema não usa banco de dados. Os dados são perdidos ao fechar a aplicação — use a exportação CSV para persistir os registros.
- **Múltiplas máquinas:** cada bloco é completamente independente. É possível ter várias máquinas em diferentes estados simultaneamente.
- **Uma atividade por máquina:** cada bloco gerencia uma atividade por vez. Após finalizar, os dados ficam no resumo até a máquina ser removida.