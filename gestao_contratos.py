import sys
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QTableWidget, QTableWidgetItem, QMessageBox, 
                             QHeaderView, QListWidget, QSplitter, 
                             QDialog, QComboBox, QFormLayout, QDialogButtonBox,
                             QAbstractItemView, QDateEdit, QTabWidget, QMenu,
                             QCheckBox, QListWidgetItem)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QAction, QColor, QFont

# --- 0. UTILITÁRIOS E COMPONENTES PERSONALIZADOS ---

class CurrencyInput(QLineEdit):
    """Campo de texto que formata como dinheiro (R$ 0,00) ao digitar"""
    def __init__(self, valor_inicial=0.0, parent=None):
        super().__init__(parent)
        self.valor_float = valor_inicial
        self.setText(self.formatar(self.valor_float))
        self.textChanged.connect(self.ao_mudar_texto)

    def formatar(self, valor):
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def ao_mudar_texto(self, text):
        # Remove tudo que não é dígito
        numeros = ''.join(filter(str.isdigit, text))
        if not numeros:
            self.valor_float = 0.0
        else:
            self.valor_float = float(numeros) / 100
        
        # Bloqueia sinal para não entrar em loop infinito
        self.blockSignals(True)
        self.setText(self.formatar(self.valor_float))
        # Move cursor para o final
        self.setCursorPosition(len(self.text()))
        self.blockSignals(False)

    def get_value(self):
        return self.valor_float

    def set_value(self, valor):
        self.valor_float = valor
        self.setText(self.formatar(valor))

def gerar_competencias(inicio_str, fim_str):
    """Gera lista de MM/YYYY entre duas datas"""
    try:
        dt_ini = datetime.strptime(inicio_str, "%m/%Y")
        dt_fim = datetime.strptime(fim_str, "%m/%Y")
        lista = []
        atual = dt_ini
        while atual <= dt_fim:
            lista.append(atual.strftime("%m/%Y"))
            # Avança um mês
            proximo_mes = atual.month + 1
            proximo_ano = atual.year
            if proximo_mes > 12:
                proximo_mes = 1
                proximo_ano += 1
            atual = datetime(proximo_ano, proximo_mes, 1)
        return lista
    except:
        return []

# --- 1. ESTRUTURA DE DADOS ---

class Aditivo:
    def __init__(self, tipo, valor=0.0, data_nova=None, descricao="", renovacao_valor=False):
        self.tipo = tipo  # "Valor" ou "Prazo"
        self.valor = valor
        self.data_nova = data_nova
        self.descricao = descricao
        self.renovacao_valor = renovacao_valor # Se True, é prazo COM valor

class SubContrato:
    def __init__(self, descricao, valor_estimado):
        self.descricao = descricao
        self.valor_estimado = valor_estimado

class Movimentacao:
    def __init__(self, tipo, valor, competencia=""):
        self.tipo = tipo
        self.valor = valor
        self.competencia = competencia 

class NotaEmpenho:
    def __init__(self, numero, valor, descricao, subcontrato_idx, fonte_recurso):
        self.numero = numero
        self.valor_inicial = valor
        self.descricao = descricao
        self.subcontrato_idx = subcontrato_idx 
        self.fonte_recurso = fonte_recurso # Novo Campo
        self.valor_pago = 0.0
        self.historico = []
        self.historico.append(Movimentacao("Emissão Original", valor, "-"))

    def realizar_pagamento(self, valor, competencia):
        saldo = self.valor_inicial - self.valor_pago
        if valor > saldo + 0.01: # Margem pequena pra float
            return False, f"Saldo insuficiente na NE! Resta: {saldo:.2f}"
        self.valor_pago += valor
        self.historico.append(Movimentacao("Pagamento", valor, competencia))
        return True, "Pagamento realizado."

    def excluir_movimentacao(self, index_movimentacao):
        if index_movimentacao < 0 or index_movimentacao >= len(self.historico):
            return False
        mov = self.historico[index_movimentacao]
        if mov.tipo == "Emissão Original":
            return False # Não exclui a origem
        if mov.tipo == "Pagamento":
            self.valor_pago -= mov.valor
        self.historico.pop(index_movimentacao)
        return True

    def editar_movimentacao(self, index, novo_valor, nova_comp):
        mov = self.historico[index]
        if mov.tipo == "Pagamento":
            # Reverte o antigo e aplica o novo
            self.valor_pago -= mov.valor
            saldo = self.valor_inicial - self.valor_pago
            if novo_valor > saldo + 0.01:
                self.valor_pago += mov.valor # Restaura o antigo se der erro
                return False, "Novo valor excede o saldo."
            self.valor_pago += novo_valor
            mov.valor = novo_valor
            mov.competencia = nova_comp
            return True, "Editado com sucesso"
        return False, "Tipo não editável"

    def calcular_media_mensal(self):
        if self.valor_pago == 0: return 0.0
        meses = set(m.competencia for m in self.historico if m.tipo == "Pagamento" and m.competencia)
        return self.valor_pago / len(meses) if len(meses) > 0 else 0.0

class Contrato:
    def __init__(self, numero, prestador, descricao, valor_inicial, vig_inicio, vig_fim, comp_inicio, comp_fim, licitacao, dispensa):
        self.numero = numero
        self.prestador = prestador
        self.descricao = descricao
        self.valor_inicial = valor_inicial
        
        self.vigencia_inicio = vig_inicio
        self.vigencia_fim = vig_fim
        self.comp_inicio = comp_inicio
        self.comp_fim = comp_fim
        
        self.licitacao = licitacao
        self.dispensa = dispensa

        self.lista_notas_empenho = []
        self.lista_aditivos = []
        self.lista_servicos = []

    def get_valor_total_contrato(self):
        # Soma Valor inicial + aditivos do tipo Valor + aditivos de Prazo que tenham renovação de valor
        total_aditivos = sum(a.valor for a in self.lista_aditivos if (a.tipo == "Valor" or a.renovacao_valor))
        return self.valor_inicial + total_aditivos

    def get_vigencia_final_atual(self):
        aditivos_prazo = [a for a in self.lista_aditivos if a.tipo == "Prazo"]
        if aditivos_prazo:
            return aditivos_prazo[-1].data_nova
        return self.vigencia_fim

    def adicionar_nota_empenho(self, ne):
        total_empenhado_geral = sum(e.valor_inicial for e in self.lista_notas_empenho)
        saldo_livre_geral = self.get_valor_total_contrato() - total_empenhado_geral
        
        if ne.valor_inicial > saldo_livre_geral + 0.01:
            return False, "Valor indisponível no Saldo Geral do Contrato."

        if ne.subcontrato_idx < 0 or ne.subcontrato_idx >= len(self.lista_servicos):
            return False, "Subcontrato inválido."
        
        sub = self.lista_servicos[ne.subcontrato_idx]
        gasto_sub = sum(e.valor_inicial for e in self.lista_notas_empenho if e.subcontrato_idx == ne.subcontrato_idx)
        saldo_livre_sub = sub.valor_estimado - gasto_sub
        
        if ne.valor_inicial > saldo_livre_sub + 0.01:
             return False, f"Valor excede o saldo do serviço '{sub.descricao}'."

        self.lista_notas_empenho.append(ne)
        return True, "Nota de Empenho vinculada."

# --- 2. DIÁLOGOS ---

class DialogoCriarContrato(QDialog):
    def __init__(self, contrato_editar=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cadastro de Contrato")
        self.setFixedWidth(500)
        layout = QFormLayout(self)

        self.inp_numero = QLineEdit()
        self.inp_prestador = QLineEdit()
        self.inp_desc = QLineEdit()
        self.inp_valor = CurrencyInput()
        
        self.inp_licitacao = QLineEdit()
        self.inp_dispensa = QLineEdit()

        self.date_vig_ini = QDateEdit(QDate.currentDate())
        self.date_vig_ini.setCalendarPopup(True)
        self.date_vig_fim = QDateEdit(QDate.currentDate().addYears(1))
        self.date_vig_fim.setCalendarPopup(True)

        self.inp_comp_ini = QLineEdit(QDate.currentDate().toString("MM/yyyy"))
        self.inp_comp_fim = QLineEdit(QDate.currentDate().addYears(1).toString("MM/yyyy"))
        self.inp_comp_ini.setInputMask("99/9999")
        self.inp_comp_fim.setInputMask("99/9999")

        layout.addRow("Número Contrato:", self.inp_numero)
        layout.addRow("Prestador:", self.inp_prestador)
        layout.addRow("Objeto:", self.inp_desc)
        layout.addRow("Valor Inicial:", self.inp_valor)
        layout.addRow("Licitação/Edital:", self.inp_licitacao)
        layout.addRow("Inexigibilidade/Disp:", self.inp_dispensa)
        layout.addRow("Início Vigência:", self.date_vig_ini)
        layout.addRow("Fim Vigência:", self.date_vig_fim)
        layout.addRow("Competência Inicial:", self.inp_comp_ini)
        layout.addRow("Competência Final:", self.inp_comp_fim)

        # Preenchimento se for edição
        if contrato_editar:
            self.inp_numero.setText(contrato_editar.numero)
            self.inp_prestador.setText(contrato_editar.prestador)
            self.inp_desc.setText(contrato_editar.descricao)
            self.inp_valor.set_value(contrato_editar.valor_inicial)
            self.inp_licitacao.setText(contrato_editar.licitacao)
            self.inp_dispensa.setText(contrato_editar.dispensa)
            self.date_vig_ini.setDate(QDate.fromString(contrato_editar.vigencia_inicio, "dd/MM/yyyy"))
            self.date_vig_fim.setDate(QDate.fromString(contrato_editar.vigencia_fim, "dd/MM/yyyy"))
            self.inp_comp_ini.setText(contrato_editar.comp_inicio)
            self.inp_comp_fim.setText(contrato_editar.comp_fim)

        botoes = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        botoes.accepted.connect(self.accept)
        botoes.rejected.connect(self.reject)
        layout.addWidget(botoes)

    def get_dados(self):
        return (self.inp_numero.text(), self.inp_prestador.text(), self.inp_desc.text(), self.inp_valor.get_value(),
                self.date_vig_ini.text(), self.date_vig_fim.text(),
                self.inp_comp_ini.text(), self.inp_comp_fim.text(),
                self.inp_licitacao.text(), self.inp_dispensa.text())

class DialogoNovoEmpenho(QDialog):
    def __init__(self, lista_subcontratos, ne_editar=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nota de Empenho")
        self.setFixedWidth(400)
        layout = QFormLayout(self)
        
        self.inp_num = QLineEdit()
        self.inp_desc = QLineEdit()
        self.inp_fonte = QLineEdit()
        self.inp_val = CurrencyInput()
        
        self.combo_sub = QComboBox()
        for sub in lista_subcontratos:
            self.combo_sub.addItem(f"{sub.descricao} (Total: {sub.valor_estimado:,.2f})")
            
        layout.addRow("Número da Nota:", self.inp_num)
        layout.addRow("Descrição:", self.inp_desc)
        layout.addRow("Fonte de Recurso:", self.inp_fonte)
        layout.addRow("Vincular a Serviço:", self.combo_sub)
        layout.addRow("Valor:", self.inp_val)

        if ne_editar:
            self.inp_num.setText(ne_editar.numero)
            self.inp_desc.setText(ne_editar.descricao)
            self.inp_fonte.setText(ne_editar.fonte_recurso)
            self.inp_val.set_value(ne_editar.valor_inicial)
            if ne_editar.subcontrato_idx < self.combo_sub.count():
                self.combo_sub.setCurrentIndex(ne_editar.subcontrato_idx)

        botoes = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        botoes.accepted.connect(self.accept)
        layout.addWidget(botoes)

    def get_dados(self):
        return self.inp_num.text(), self.inp_desc.text(), self.combo_sub.currentIndex(), self.inp_val.get_value(), self.inp_fonte.text()

class DialogoAditivo(QDialog):
    def __init__(self, aditivo_editar=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Aditivo")
        layout = QFormLayout(self)
        
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["Valor (Acréscimo/Decréscimo)", "Prazo (Prorrogação)"])
        self.combo_tipo.currentIndexChanged.connect(self.mudar_tipo)

        self.chk_renovacao = QCheckBox("Haverá renovação de valor?")
        self.chk_renovacao.setVisible(False)
        self.chk_renovacao.toggled.connect(self.mudar_tipo)

        self.inp_valor = CurrencyInput()
        self.date_nova = QDateEdit(QDate.currentDate())
        self.date_nova.setCalendarPopup(True)
        self.date_nova.setEnabled(False)
        
        self.inp_desc = QLineEdit()

        layout.addRow("Tipo:", self.combo_tipo)
        layout.addRow("", self.chk_renovacao)
        layout.addRow("Valor:", self.inp_valor)
        layout.addRow("Nova Data Fim:", self.date_nova)
        layout.addRow("Justificativa:", self.inp_desc)

        if aditivo_editar:
            idx = 0 if aditivo_editar.tipo == "Valor" else 1
            self.combo_tipo.setCurrentIndex(idx)
            self.inp_valor.set_value(aditivo_editar.valor)
            if aditivo_editar.data_nova:
                self.date_nova.setDate(QDate.fromString(aditivo_editar.data_nova, "dd/MM/yyyy"))
            self.inp_desc.setText(aditivo_editar.descricao)
            self.chk_renovacao.setChecked(aditivo_editar.renovacao_valor)
            self.mudar_tipo()

        botoes = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        botoes.accepted.connect(self.accept)
        layout.addWidget(botoes)

    def mudar_tipo(self):
        is_prazo = self.combo_tipo.currentText().startswith("Prazo")
        
        if is_prazo:
            self.chk_renovacao.setVisible(True)
            self.date_nova.setEnabled(True)
            # Se é prazo e quer renovar valor, habilita valor. Se não, desabilita.
            self.inp_valor.setEnabled(self.chk_renovacao.isChecked())
        else:
            # É apenas Valor
            self.chk_renovacao.setVisible(False)
            self.chk_renovacao.setChecked(False)
            self.inp_valor.setEnabled(True)
            self.date_nova.setEnabled(False)

    def get_dados(self):
        tipo = "Valor" if self.combo_tipo.currentText().startswith("Valor") else "Prazo"
        val = self.inp_valor.get_value()
        return tipo, val, self.date_nova.text(), self.inp_desc.text(), self.chk_renovacao.isChecked()

class DialogoPagamento(QDialog):
    def __init__(self, comp_inicio, comp_fim, pg_editar=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pagamento")
        layout = QFormLayout(self)
        
        self.combo_comp = QComboBox()
        lista_meses = gerar_competencias(comp_inicio, comp_fim)
        if not lista_meses:
            lista_meses = ["Configuração de datas inválida"]
        self.combo_comp.addItems(lista_meses)
        
        self.inp_valor = CurrencyInput()
        
        layout.addRow("Competência:", self.combo_comp)
        layout.addRow("Valor:", self.inp_valor)

        if pg_editar:
            # Tentar setar a competencia existente
            index = self.combo_comp.findText(pg_editar.competencia)
            if index >= 0: self.combo_comp.setCurrentIndex(index)
            self.inp_valor.set_value(pg_editar.valor)

        botoes = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        botoes.accepted.connect(self.accept)
        layout.addWidget(botoes)

    def get_dados(self):
        return self.combo_comp.currentText(), self.inp_valor.get_value()

class DialogoSubContrato(QDialog):
    def __init__(self, sub_editar=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Serviço / Subcontrato")
        layout = QFormLayout(self)
        self.inp_desc = QLineEdit()
        self.inp_valor = CurrencyInput()
        layout.addRow("Descrição:", self.inp_desc)
        layout.addRow("Valor Estimado:", self.inp_valor)
        
        if sub_editar:
            self.inp_desc.setText(sub_editar.descricao)
            self.inp_valor.set_value(sub_editar.valor_estimado)
            
        botoes = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        botoes.accepted.connect(self.accept)
        layout.addWidget(botoes)
    
    def get_dados(self):
        return self.inp_desc.text(), self.inp_valor.get_value()

# --- 3. SISTEMA PRINCIPAL ---

class SistemaGestao(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db_contratos = [] 
        self.contrato_selecionado = None
        self.ne_selecionada = None 
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("SGF - Gestão Profissional")
        self.setGeometry(100, 100, 1280, 800) 

        # Menus
        mb = self.menuBar()
        m_arq = mb.addMenu("Arquivo")
        m_arq.addAction("Sair", self.close)
        
        m_con = mb.addMenu("Contratos")
        m_con.addAction("Novo Contrato...", self.abrir_novo_contrato)
        m_con.addAction("Listar Contratos", lambda: None) # Já visível na tela principal

        # Layout Principal
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(splitter)

        # PAINEL ESQUERDO: LISTA DE CONTRATOS
        p_esq = QWidget()
        l_esq = QVBoxLayout(p_esq)
        l_esq.addWidget(QLabel("<b>Lista de Contratos</b>"))
        
        self.lista_contratos_widget = QListWidget()
        self.lista_contratos_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.lista_contratos_widget.customContextMenuRequested.connect(self.menu_contrato)
        self.lista_contratos_widget.itemClicked.connect(self.selecionar_contrato)
        l_esq.addWidget(self.lista_contratos_widget)
        splitter.addWidget(p_esq)

        # PAINEL DIREITO: DETALHES
        p_dir = QWidget()
        self.layout_dir = QVBoxLayout(p_dir)
        
        # Cabeçalho
        self.lbl_titulo = QLabel("Selecione um contrato")
        self.lbl_titulo.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.layout_dir.addWidget(self.lbl_titulo)
        
        self.lbl_prestador = QLabel("")
        self.lbl_prestador.setStyleSheet("color: #555; font-weight: bold; font-size: 12px;")
        self.layout_dir.addWidget(self.lbl_prestador)

        self.lbl_saldo = QLabel("")
        self.lbl_saldo.setStyleSheet("font-size: 14px; margin-bottom: 5px")
        self.layout_dir.addWidget(self.lbl_saldo)

        # Abas
        self.abas = QTabWidget()
        self.layout_dir.addWidget(self.abas)

        # --- ABA 0: DADOS DO CONTRATO ---
        self.tab_dados = QWidget()
        l_dados = QFormLayout(self.tab_dados)
        self.lbl_d_licitacao = QLabel("-")
        self.lbl_d_dispensa = QLabel("-")
        self.lbl_d_vigencia = QLabel("-")
        self.lbl_d_comp = QLabel("-")
        l_dados.addRow("Licitação/Edital:", self.lbl_d_licitacao)
        l_dados.addRow("Inexigibilidade/Dispensa:", self.lbl_d_dispensa)
        l_dados.addRow("Período de Vigência:", self.lbl_d_vigencia)
        l_dados.addRow("Período de Competência:", self.lbl_d_comp)
        self.abas.addTab(self.tab_dados, "Dados do Contrato")

        # --- ABA 1: FINANCEIRO (Notas de Empenho) ---
        tab_fin = QWidget()
        l_fin = QVBoxLayout(tab_fin)
        
        btns_fin = QHBoxLayout()
        b_ne = QPushButton("+ Nova Nota de Empenho")
        b_ne.clicked.connect(self.dialogo_nova_ne)
        b_pg = QPushButton("Registrar Pagamento")
        b_pg.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold")
        b_pg.clicked.connect(self.abrir_pagamento)
        btns_fin.addWidget(b_ne)
        btns_fin.addWidget(b_pg)
        btns_fin.addStretch()
        l_fin.addLayout(btns_fin)

        self.tab_empenhos = QTableWidget()
        self.tab_empenhos.setColumnCount(8) 
        self.tab_empenhos.setHorizontalHeaderLabels(["Nota (NE)", "Fonte", "Serviço/Sub", "Descrição", "Valor NE", "Pago", "Saldo NE", "Média"])
        self.tab_empenhos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tab_empenhos.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tab_empenhos.itemClicked.connect(self.selecionar_ne)
        self.tab_empenhos.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tab_empenhos.customContextMenuRequested.connect(self.menu_empenho)
        l_fin.addWidget(self.tab_empenhos)

        l_fin.addWidget(QLabel("Histórico da Nota Selecionada:"))
        self.tab_mov = QTableWidget()
        self.tab_mov.setColumnCount(4)
        self.tab_mov.setHorizontalHeaderLabels(["Comp.", "Tipo", "Valor Mov.", "Saldo Nota"])
        self.tab_mov.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tab_mov.setMaximumHeight(200)
        self.tab_mov.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tab_mov.customContextMenuRequested.connect(self.menu_movimentacao)
        l_fin.addWidget(self.tab_mov)

        self.abas.addTab(tab_fin, "Financeiro (Notas de Empenho)")

        # --- ABA 2: SERVIÇOS (Subcontratos) ---
        tab_serv = QWidget()
        l_serv = QVBoxLayout(tab_serv)
        
        btn_novo_serv = QPushButton("+ Novo Serviço/Subcontrato")
        btn_novo_serv.clicked.connect(self.abrir_novo_servico)
        l_serv.addWidget(btn_novo_serv)

        self.tab_subcontratos = QTableWidget()
        self.tab_subcontratos.setColumnCount(4)
        self.tab_subcontratos.setHorizontalHeaderLabels(["Descrição Serviço", "Valor Estimado", "Empenhado", "Saldo Serviço"])
        self.tab_subcontratos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tab_subcontratos.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tab_subcontratos.customContextMenuRequested.connect(self.menu_subcontrato)
        l_serv.addWidget(self.tab_subcontratos)
        self.abas.addTab(tab_serv, "Serviços / Subcontratos")
        
        # --- ABA 3: ADITIVOS ---
        tab_adit = QWidget()
        l_adit = QVBoxLayout(tab_adit)
        
        btn_novo_adit = QPushButton("+ Novo Aditivo")
        btn_novo_adit.clicked.connect(self.abrir_novo_aditivo)
        l_adit.addWidget(btn_novo_adit)

        self.tab_aditivos = QTableWidget()
        self.tab_aditivos.setColumnCount(5)
        self.tab_aditivos.setHorizontalHeaderLabels(["Tipo", "Renov. Valor?", "Valor", "Nova Data", "Justificativa"])
        self.tab_aditivos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tab_aditivos.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tab_aditivos.customContextMenuRequested.connect(self.menu_aditivo)
        l_adit.addWidget(self.tab_aditivos)
        self.abas.addTab(tab_adit, "Aditivos")

        splitter.addWidget(p_dir)
        splitter.setSizes([300, 950])

    # --- LÓGICA DE MENUS DE CONTEXTO ---

    def menu_contrato(self, pos):
        item = self.lista_contratos_widget.itemAt(pos)
        if not item: return
        menu = QMenu()
        menu.addAction("Editar Contrato", self.editar_contrato)
        menu.addAction("Excluir Contrato", self.excluir_contrato)
        menu.exec(self.lista_contratos_widget.mapToGlobal(pos))

    def menu_empenho(self, pos):
        if not self.ne_selecionada: return
        menu = QMenu()
        menu.addAction("Editar NE", self.editar_ne)
        menu.addAction("Excluir NE", self.excluir_ne)
        menu.exec(self.tab_empenhos.mapToGlobal(pos))

    def menu_subcontrato(self, pos):
        item = self.tab_subcontratos.itemAt(pos)
        if not item: return
        row = item.row()
        menu = QMenu()
        menu.addAction("Editar Serviço", lambda: self.editar_servico(row))
        menu.addAction("Excluir Serviço", lambda: self.excluir_servico(row))
        menu.exec(self.tab_subcontratos.mapToGlobal(pos))

    def menu_aditivo(self, pos):
        item = self.tab_aditivos.itemAt(pos)
        if not item: return
        row = item.row()
        menu = QMenu()
        menu.addAction("Editar Aditivo", lambda: self.editar_aditivo(row))
        menu.addAction("Excluir Aditivo", lambda: self.excluir_aditivo(row))
        menu.exec(self.tab_aditivos.mapToGlobal(pos))
    
    def menu_movimentacao(self, pos):
        item = self.tab_mov.itemAt(pos)
        if not item: return
        row = item.row()
        # Verificar se é original
        mov = self.ne_selecionada.historico[row]
        if mov.tipo == "Emissão Original": return
        
        menu = QMenu()
        menu.addAction("Editar Pagamento", lambda: self.editar_pagamento(row))
        menu.addAction("Excluir Pagamento", lambda: self.excluir_pagamento(row))
        menu.exec(self.tab_mov.mapToGlobal(pos))

    # --- FUNÇÕES DE CRUD (Create, Read, Update, Delete) ---

    def abrir_novo_contrato(self):
        dial = DialogoCriarContrato(parent=self)
        if dial.exec():
            # Desempacotar
            dados = dial.get_dados()
            c = Contrato(*dados)
            self.db_contratos.append(c)
            self.atualizar_lista_contratos()

    def editar_contrato(self):
        c = self.contrato_selecionado
        if not c: return
        dial = DialogoCriarContrato(contrato_editar=c, parent=self)
        if dial.exec():
            dados = dial.get_dados()
            # Atualiza atributos
            c.numero, c.prestador, c.descricao, c.valor_inicial, \
            c.vigencia_inicio, c.vigencia_fim, c.comp_inicio, c.comp_fim, \
            c.licitacao, c.dispensa = dados
            self.atualizar_lista_contratos()
            self.atualizar_painel_detalhes()

    def excluir_contrato(self):
        if not self.contrato_selecionado: return
        res = QMessageBox.question(self, "Excluir", "Excluir este contrato e todos os dados?", 
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if res == QMessageBox.StandardButton.Yes:
            self.db_contratos.remove(self.contrato_selecionado)
            self.contrato_selecionado = None
            self.ne_selecionada = None
            self.atualizar_lista_contratos()
            self.lbl_titulo.setText("Selecione um contrato")

    def dialogo_nova_ne(self):
        if not self.contrato_selecionado: return
        if not self.contrato_selecionado.lista_servicos:
            QMessageBox.warning(self, "Atenção", "Crie pelo menos um Serviço/Subcontrato antes.")
            return

        dial = DialogoNovoEmpenho(self.contrato_selecionado.lista_servicos, parent=self)
        if dial.exec():
            num, desc, idx, val, fonte = dial.get_dados()
            nova_ne = NotaEmpenho(num, val, desc, idx, fonte)
            ok, msg = self.contrato_selecionado.adicionar_nota_empenho(nova_ne)
            if ok: self.atualizar_painel_detalhes()
            else: QMessageBox.critical(self, "Erro de Saldo", msg)

    def editar_ne(self):
        ne = self.ne_selecionada
        if not ne: return
        # Logica simplificada: permite editar texto, mas valor é complexo pois afeta saldo
        # Para simplificar, permitimos editar dados cadastrais. Valor só se não tiver pagamentos.
        
        dial = DialogoNovoEmpenho(self.contrato_selecionado.lista_servicos, ne_editar=ne, parent=self)
        # Se ja tiver pagamentos, bloqueia valor
        if len(ne.historico) > 1:
            dial.inp_val.setEnabled(False)
            dial.setWindowTitle("Editar NE (Valor fixo pois há pagamentos)")

        if dial.exec():
            num, desc, idx, val, fonte = dial.get_dados()
            ne.numero = num
            ne.descricao = desc
            ne.fonte_recurso = fonte
            ne.subcontrato_idx = idx
            
            # Atualiza valor se permitido
            if len(ne.historico) == 1:
                ne.valor_inicial = val
                ne.historico[0].valor = val
            
            self.atualizar_painel_detalhes()

    def excluir_ne(self):
        if not self.ne_selecionada: return
        res = QMessageBox.question(self, "Excluir", "Excluir esta Nota de Empenho?", 
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if res == QMessageBox.StandardButton.Yes:
            self.contrato_selecionado.lista_notas_empenho.remove(self.ne_selecionada)
            self.ne_selecionada = None
            self.atualizar_painel_detalhes()

    def abrir_novo_aditivo(self):
        if not self.contrato_selecionado: return
        dial = DialogoAditivo(parent=self)
        if dial.exec():
            dados = dial.get_dados() # tipo, val, data, desc, renova_bool
            adt = Aditivo(*dados)
            self.contrato_selecionado.lista_aditivos.append(adt)
            self.atualizar_painel_detalhes()

    def editar_aditivo(self, row):
        adt = self.contrato_selecionado.lista_aditivos[row]
        dial = DialogoAditivo(aditivo_editar=adt, parent=self)
        if dial.exec():
            tipo, val, data, desc, renova = dial.get_dados()
            adt.tipo = tipo
            adt.valor = val
            adt.data_nova = data
            adt.descricao = desc
            adt.renovacao_valor = renova
            self.atualizar_painel_detalhes()

    def excluir_aditivo(self, row):
        del self.contrato_selecionado.lista_aditivos[row]
        self.atualizar_painel_detalhes()

    def abrir_novo_servico(self):
        if not self.contrato_selecionado: return
        dial = DialogoSubContrato(parent=self)
        if dial.exec():
            desc, val = dial.get_dados()
            sub = SubContrato(desc, val)
            self.contrato_selecionado.lista_servicos.append(sub)
            self.atualizar_painel_detalhes()

    def editar_servico(self, row):
        sub = self.contrato_selecionado.lista_servicos[row]
        dial = DialogoSubContrato(sub_editar=sub, parent=self)
        if dial.exec():
            d, v = dial.get_dados()
            sub.descricao = d
            sub.valor_estimado = v
            self.atualizar_painel_detalhes()

    def excluir_servico(self, row):
        # Verificar se tem NEs vinculadas
        tem_vinculo = any(ne.subcontrato_idx == row for ne in self.contrato_selecionado.lista_notas_empenho)
        if tem_vinculo:
            QMessageBox.warning(self, "Erro", "Não pode excluir serviço com NEs vinculadas.")
            return
        del self.contrato_selecionado.lista_servicos[row]
        self.atualizar_painel_detalhes()

    def abrir_pagamento(self):
        if not self.ne_selecionada: 
            QMessageBox.warning(self, "Aviso", "Selecione uma Nota de Empenho.")
            return
        
        c_ini = self.contrato_selecionado.comp_inicio
        c_fim = self.contrato_selecionado.comp_fim
        d = DialogoPagamento(c_ini, c_fim, parent=self)
        
        if d.exec():
            comp, val = d.get_dados()
            ok, msg = self.ne_selecionada.realizar_pagamento(val, comp)
            if not ok: QMessageBox.warning(self, "Erro", msg)
            self.atualizar_painel_detalhes()
            self.atualizar_movimentos()

    def editar_pagamento(self, row):
        mov = self.ne_selecionada.historico[row]
        c_ini = self.contrato_selecionado.comp_inicio
        c_fim = self.contrato_selecionado.comp_fim
        d = DialogoPagamento(c_ini, c_fim, pg_editar=mov, parent=self)
        if d.exec():
            comp, val = d.get_dados()
            ok, msg = self.ne_selecionada.editar_movimentacao(row, val, comp)
            if ok: 
                self.atualizar_painel_detalhes()
                self.atualizar_movimentos()
            else:
                QMessageBox.warning(self, "Erro", msg)

    def excluir_pagamento(self, row):
        ok = self.ne_selecionada.excluir_movimentacao(row)
        if ok:
            self.atualizar_painel_detalhes()
            self.atualizar_movimentos()
        else:
            QMessageBox.warning(self, "Erro", "Não foi possível excluir.")

    # --- ATUALIZAÇÕES DE UI ---

    def atualizar_lista_contratos(self):
        self.lista_contratos_widget.clear()
        for c in self.db_contratos:
            item = QListWidgetItem(f"{c.numero}\n{c.prestador}")
            self.lista_contratos_widget.addItem(item)

    def selecionar_contrato(self, item):
        row = self.lista_contratos_widget.row(item)
        self.contrato_selecionado = self.db_contratos[row]
        self.ne_selecionada = None 
        self.atualizar_painel_detalhes()

    def atualizar_painel_detalhes(self):
        if not self.contrato_selecionado: return
        c = self.contrato_selecionado
        
        self.lbl_titulo.setText(f"Contrato {c.numero} - {c.descricao}")
        self.lbl_prestador.setText(f"Prestador: {c.prestador}")
        
        # Aba Dados
        self.lbl_d_licitacao.setText(c.licitacao)
        self.lbl_d_dispensa.setText(c.dispensa)
        self.lbl_d_vigencia.setText(f"{c.vigencia_inicio} a {c.get_vigencia_final_atual()}")
        self.lbl_d_comp.setText(f"{c.comp_inicio} a {c.comp_fim}")

        val_total = c.get_valor_total_contrato()
        val_empenhado_geral = sum(e.valor_inicial for e in c.lista_notas_empenho)
        saldo_livre = val_total - val_empenhado_geral
        
        # Cor verde para saldo
        cor_verde = "#27ae60"
        txt_saldo = f"Total Contrato: R$ {val_total:,.2f} | Empenhado: R$ {val_empenhado_geral:,.2f} | <span style='color:{cor_verde}'><b>Saldo Livre: R$ {saldo_livre:,.2f}</b></span>"
        self.lbl_saldo.setText(txt_saldo)

        # Atualiza Tabelas
        self.tab_empenhos.setRowCount(0)
        self.tab_mov.setRowCount(0)
        
        for row, ne in enumerate(c.lista_notas_empenho):
            self.tab_empenhos.insertRow(row)
            nome_servico = "Desconhecido"
            if 0 <= ne.subcontrato_idx < len(c.lista_servicos):
                nome_servico = c.lista_servicos[ne.subcontrato_idx].descricao

            self.tab_empenhos.setItem(row, 0, QTableWidgetItem(ne.numero))
            self.tab_empenhos.setItem(row, 1, QTableWidgetItem(ne.fonte_recurso))
            self.tab_empenhos.setItem(row, 2, QTableWidgetItem(nome_servico))
            self.tab_empenhos.setItem(row, 3, QTableWidgetItem(ne.descricao))
            self.tab_empenhos.setItem(row, 4, QTableWidgetItem(f"{ne.valor_inicial:,.2f}"))
            self.tab_empenhos.setItem(row, 5, QTableWidgetItem(f"{ne.valor_pago:,.2f}"))
            
            saldo_ne = ne.valor_inicial - ne.valor_pago
            item_saldo = QTableWidgetItem(f"{saldo_ne:,.2f}")
            item_saldo.setForeground(QColor(cor_verde)) # Verde
            item_saldo.setFont(QFont("Arial", 9, QFont.Weight.Bold))
            self.tab_empenhos.setItem(row, 6, item_saldo)
            
            self.tab_empenhos.setItem(row, 7, QTableWidgetItem(f"{ne.calcular_media_mensal():,.2f}"))
            self.tab_empenhos.item(row, 0).setData(Qt.ItemDataRole.UserRole, ne)

        self.tab_subcontratos.setRowCount(0)
        for idx, sub in enumerate(c.lista_servicos):
            empenhado_sub = sum(ne.valor_inicial for ne in c.lista_notas_empenho if ne.subcontrato_idx == idx)
            saldo_sub = sub.valor_estimado - empenhado_sub
            
            row = self.tab_subcontratos.rowCount()
            self.tab_subcontratos.insertRow(row)
            self.tab_subcontratos.setItem(row, 0, QTableWidgetItem(sub.descricao))
            self.tab_subcontratos.setItem(row, 1, QTableWidgetItem(f"{sub.valor_estimado:,.2f}"))
            self.tab_subcontratos.setItem(row, 2, QTableWidgetItem(f"{empenhado_sub:,.2f}"))
            item_saldo_sub = QTableWidgetItem(f"{saldo_sub:,.2f}")
            item_saldo_sub.setForeground(QColor(cor_verde if saldo_sub >= 0 else "red"))
            self.tab_subcontratos.setItem(row, 3, item_saldo_sub)

        self.tab_aditivos.setRowCount(0)
        for row, adt in enumerate(c.lista_aditivos):
            self.tab_aditivos.insertRow(row)
            self.tab_aditivos.setItem(row, 0, QTableWidgetItem(adt.tipo))
            self.tab_aditivos.setItem(row, 1, QTableWidgetItem("Sim" if adt.renovacao_valor else "Não"))
            val_txt = f"{adt.valor:,.2f}" if (adt.tipo == "Valor" or adt.renovacao_valor) else "-"
            self.tab_aditivos.setItem(row, 2, QTableWidgetItem(val_txt))
            data_txt = adt.data_nova if adt.tipo == "Prazo" else "-"
            self.tab_aditivos.setItem(row, 3, QTableWidgetItem(data_txt))
            self.tab_aditivos.setItem(row, 4, QTableWidgetItem(adt.descricao))

    def selecionar_ne(self, item):
        row = item.row()
        self.ne_selecionada = self.tab_empenhos.item(row, 0).data(Qt.ItemDataRole.UserRole)
        self.atualizar_movimentos()

    def atualizar_movimentos(self):
        if not self.ne_selecionada: return
        self.tab_mov.setRowCount(0)
        saldo_corrente = self.ne_selecionada.valor_inicial
        
        for row, m in enumerate(self.ne_selecionada.historico):
            self.tab_mov.insertRow(row)
            if m.tipo == "Pagamento":
                saldo_corrente -= m.valor
            
            self.tab_mov.setItem(row, 0, QTableWidgetItem(m.competencia))
            self.tab_mov.setItem(row, 1, QTableWidgetItem(m.tipo))
            self.tab_mov.setItem(row, 2, QTableWidgetItem(f"{m.valor:,.2f}"))
            
            item_saldo = QTableWidgetItem(f"{saldo_corrente:,.2f}")
            item_saldo.setForeground(QColor("#27ae60")) # Verde
            self.tab_mov.setItem(row, 3, item_saldo)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = SistemaGestao()
    win.show()
    sys.exit(app.exec())