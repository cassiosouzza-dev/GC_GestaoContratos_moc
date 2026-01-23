import sys
import csv
import json
import os
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QTableWidget, QTableWidgetItem, QMessageBox,
                             QHeaderView, QListWidget, QSplitter,
                             QDialog, QComboBox, QFormLayout, QDialogButtonBox,
                             QAbstractItemView, QDateEdit, QTabWidget, QMenu,
                             QCheckBox, QStackedWidget, QFrame, QFileDialog, QInputDialog)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QAction, QColor, QFont, QPalette


def fmt_br(valor):
    """Formata float para BRL: 1234.50 vira 1.234,50"""
    if valor is None: return "0,00"
    texto = f"{valor:,.2f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")

class TabelaExcel(QTableWidget):
    """Uma tabela que permite copiar dados (Ctrl+C) e BLOQUEIA edição direta"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Esta linha desativa a edição ao clicar duas vezes
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_C and (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            self.copiar_selecao()
        else:
            super().keyPressEvent(event)

    def copiar_selecao(self):
        selecao = self.selectedIndexes()
        if not selecao: return
        rows = sorted(list(set(index.row() for index in selecao)))
        cols = sorted(list(set(index.column() for index in selecao)))
        texto_final = ""
        for r in rows:
            linha_texto = []
            for c in cols:
                item = self.item(r, c)
                if item and self.isPersistentEditorOpen(item) == False:
                    linha_texto.append(item.text())
                else:
                    linha_texto.append("")
            texto_final += "\t".join(linha_texto) + "\n"
        QApplication.clipboard().setText(texto_final)


# --- 0. UTILITÁRIOS ---

class CurrencyInput(QLineEdit):
    def __init__(self, valor_inicial=0.0, parent=None):
        super().__init__(parent)
        self.valor_float = valor_inicial
        self.setText(self.formatar(self.valor_float))
        self.textChanged.connect(self.ao_mudar_texto)

    def formatar(self, valor):
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def ao_mudar_texto(self, text):
        numeros = ''.join(filter(str.isdigit, text))
        if not numeros:
            self.valor_float = 0.0
        else:
            self.valor_float = float(numeros) / 100
        self.blockSignals(True)
        self.setText(self.formatar(self.valor_float))
        self.setCursorPosition(len(self.text()))
        self.blockSignals(False)

    def get_value(self):
        return self.valor_float

    def set_value(self, valor):
        self.valor_float = valor
        self.setText(self.formatar(valor))


def str_to_date(date_str):
    try:
        return datetime.strptime(date_str, "%d/%m/%Y")
    except:
        return datetime.now()


def parse_float_br(valor_str):
    if not valor_str: return 0.0
    v = valor_str.strip()
    if ',' in v and '.' in v:
        v = v.replace('.', '').replace(',', '.')
    elif ',' in v:
        v = v.replace(',', '.')
    try:
        return float(v)
    except:
        return 0.0


def gerar_competencias(inicio_str, fim_str):
    try:
        dt_ini = datetime.strptime(inicio_str, "%m/%Y")
        dt_fim = datetime.strptime(fim_str, "%m/%Y")
        lista = []
        atual = dt_ini
        while atual <= dt_fim:
            lista.append(atual.strftime("%m/%Y"))
            if atual.month == 12:
                atual = datetime(atual.year + 1, 1, 1)
            else:
                atual = datetime(atual.year, atual.month + 1, 1)
        return lista
    except:
        return []


# --- 1. ESTRUTURA DE DADOS ---

class Movimentacao:
    def __init__(self, tipo, valor, competencia=""):
        self.tipo = tipo
        self.valor = valor
        self.competencia = competencia

    def to_dict(self): return self.__dict__

    @staticmethod
    def from_dict(d): return Movimentacao(d['tipo'], d['valor'], d['competencia'])


class NotaEmpenho:
    def __init__(self, numero, valor, descricao, subcontrato_idx, fonte_recurso, data_emissao, ciclo_id,
                 aditivo_vinculado_id=None):
        self.numero = numero
        self.valor_inicial = valor
        self.descricao = descricao
        self.subcontrato_idx = subcontrato_idx
        self.fonte_recurso = fonte_recurso
        self.data_emissao = data_emissao
        self.ciclo_id = ciclo_id
        self.aditivo_vinculado_id = aditivo_vinculado_id
        self.valor_pago = 0.0
        self.historico = []
        self.historico.append(Movimentacao("Emissão Original", valor, "-"))

    def realizar_pagamento(self, valor, competencia):
        saldo = self.valor_inicial - self.valor_pago
        if valor > saldo + 0.01: return False, f"Saldo insuficiente! Resta: {saldo:.2f}"
        self.valor_pago += valor
        self.historico.append(Movimentacao("Pagamento", valor, competencia))
        return True, "Pagamento realizado."

    def excluir_movimentacao(self, index):
        if index < 0 or index >= len(self.historico): return False
        mov = self.historico[index]
        if mov.tipo == "Emissão Original": return False
        if mov.tipo == "Pagamento": self.valor_pago -= mov.valor
        self.historico.pop(index)
        return True

    def editar_movimentacao(self, index, novo_valor, nova_comp):
        mov = self.historico[index]
        if mov.tipo == "Pagamento":
            self.valor_pago -= mov.valor
            saldo = self.valor_inicial - self.valor_pago
            if novo_valor > saldo + 0.01:
                self.valor_pago += mov.valor
                return False, "Novo valor excede o saldo."
            self.valor_pago += novo_valor
            mov.valor = novo_valor;
            mov.competencia = nova_comp
            return True, "Sucesso"
        return False, "Erro"

    def calcular_media_mensal(self):
        if self.valor_pago == 0: return 0.0
        meses = set(m.competencia for m in self.historico if m.tipo == "Pagamento" and m.competencia)
        return self.valor_pago / len(meses) if len(meses) > 0 else 0.0

    def to_dict(self):
        d = self.__dict__.copy()
        d['historico'] = [h.to_dict() for h in self.historico]
        return d

    @staticmethod
    def from_dict(d):
        ne = NotaEmpenho(d['numero'], d['valor_inicial'], d['descricao'], d['subcontrato_idx'],
                         d['fonte_recurso'], d['data_emissao'], d.get('ciclo_id', 0), d.get('aditivo_vinculado_id'))
        ne.valor_pago = d['valor_pago']
        ne.historico = [Movimentacao.from_dict(h) for h in d['historico']]
        return ne


class Aditivo:
    def __init__(self, id_aditivo, tipo, valor=0.0, data_nova=None, descricao="", renovacao_valor=False,
                 data_inicio_vigencia=None, servico_idx=-1):
        self.id_aditivo = id_aditivo
        self.tipo = tipo
        self.valor = valor
        self.data_nova = data_nova
        self.descricao = descricao
        self.renovacao_valor = renovacao_valor
        self.data_inicio_vigencia = data_inicio_vigencia
        self.ciclo_pertencente_id = -1
        self.servico_idx = servico_idx 

    def to_dict(self): return self.__dict__

    @staticmethod
    def from_dict(d):
        adt = Aditivo(d['id_aditivo'], d['tipo'], d['valor'], d['data_nova'], d['descricao'], d['renovacao_valor'],
                      d['data_inicio_vigencia'], d.get('servico_idx', -1))
        adt.ciclo_pertencente_id = d.get('ciclo_pertencente_id', -1)
        return adt


class SubContrato:
    def __init__(self, descricao, valor_inicial=0.0):
        self.descricao = descricao
        self.valores_por_ciclo = {0: valor_inicial}

    def get_valor_ciclo(self, id_ciclo):
        return self.valores_por_ciclo.get(id_ciclo, 0.0)

    def set_valor_ciclo(self, id_ciclo, valor):
        self.valores_por_ciclo[id_ciclo] = valor

    def to_dict(self):
        d = self.__dict__.copy()
        d['valores_por_ciclo'] = {str(k): v for k, v in self.valores_por_ciclo.items()}
        return d

    @staticmethod
    def from_dict(d):
        val = d.get('valor_estimado', 0.0)
        sub = SubContrato(d['descricao'], val)
        if 'valores_por_ciclo' in d:
            sub.valores_por_ciclo = {int(k): v for k, v in d['valores_por_ciclo'].items()}
        return sub


class CicloFinanceiro:
    def __init__(self, id_ciclo, nome, valor_base):
        self.id_ciclo = id_ciclo
        self.nome = nome
        self.valor_base = valor_base
        self.aditivos_valor = []

    def get_teto_total(self):
        return self.valor_base + sum(a.valor for a in self.aditivos_valor)

    def to_dict(self):
        d = self.__dict__.copy()
        if 'aditivos_valor' in d: del d['aditivos_valor']
        return d

    @staticmethod
    def from_dict(d): return CicloFinanceiro(d['id_ciclo'], d['nome'], d['valor_base'])


class Contrato:
    def __init__(self, numero, prestador, descricao, valor_inicial, vig_inicio, vig_fim, comp_inicio, comp_fim,
                 licitacao, dispensa):
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

        self.ciclos = []
        self.ciclos.append(CicloFinanceiro(0, "Contrato Inicial", valor_inicial))

        self.lista_notas_empenho = []
        self.lista_aditivos = []
        self.lista_servicos = []
        self._contador_aditivos = 0

    def get_vigencia_final_atual(self):
        aditivos_prazo = [a for a in self.lista_aditivos if a.tipo == "Prazo"]
        if aditivos_prazo: return aditivos_prazo[-1].data_nova
        return self.vigencia_fim

    def adicionar_aditivo(self, adt):
        self._contador_aditivos += 1
        adt.id_aditivo = self._contador_aditivos
        self.lista_aditivos.append(adt)
        
        qtd_prazos = len([a for a in self.lista_aditivos if a.tipo == "Prazo"])
        qtd_valores = len([a for a in self.lista_aditivos if a.tipo == "Valor"])
        
        if adt.tipo == "Prazo" and adt.renovacao_valor:
            id_ciclo_anterior = len(self.ciclos) - 1
            novo_id = len(self.ciclos)
            nome_ciclo = f"{qtd_prazos}º TA Prazo/Valor"
            
            novo_ciclo = CicloFinanceiro(novo_id, nome_ciclo, adt.valor)
            self.ciclos.append(novo_ciclo)
            adt.ciclo_pertencente_id = novo_id
            
            for serv in self.lista_servicos:
                valor_antigo = serv.get_valor_ciclo(id_ciclo_anterior)
                serv.set_valor_ciclo(novo_id, valor_antigo)
                
            return f"Novo Ciclo Criado: {nome_ciclo}. Serviços replicados."

        elif adt.tipo == "Valor":
            ciclo_atual = self.ciclos[-1]
            ciclo_atual.aditivos_valor.append(adt)
            adt.ciclo_pertencente_id = ciclo_atual.id_ciclo
            adt.descricao = f"{qtd_valores}º TA Valor - " + adt.descricao
            
            if adt.servico_idx >= 0 and adt.servico_idx < len(self.lista_servicos):
                serv = self.lista_servicos[adt.servico_idx]
                valor_atual = serv.get_valor_ciclo(ciclo_atual.id_ciclo)
                serv.set_valor_ciclo(ciclo_atual.id_ciclo, valor_atual + adt.valor)
                return f"Valor somado ao serviço '{serv.descricao}' no ciclo atual."
                
            return f"Valor vinculado ao ciclo: {ciclo_atual.nome} (Sem serviço específico)"
            
        return "Aditivo registrado (Apenas Prazo)"

    def get_saldo_ciclo_geral(self, id_ciclo):
        if id_ciclo < 0 or id_ciclo >= len(self.ciclos): return 0.0
        c = self.ciclos[id_ciclo]
        teto = c.get_teto_total()
        empenhado = sum(ne.valor_inicial for ne in self.lista_notas_empenho if ne.ciclo_id == id_ciclo)
        return teto - empenhado

    def get_saldo_aditivo_especifico(self, id_aditivo):
        aditivo_alvo = next((a for a in self.lista_aditivos if a.id_aditivo == id_aditivo), None)
        if not aditivo_alvo: return 0.0
        gasto_especifico = sum(
            ne.valor_inicial for ne in self.lista_notas_empenho if ne.aditivo_vinculado_id == id_aditivo)
        return aditivo_alvo.valor - gasto_especifico

    def adicionar_nota_empenho(self, ne):
        saldo_ciclo = self.get_saldo_ciclo_geral(ne.ciclo_id)
        if ne.valor_inicial > saldo_ciclo + 0.01: return False, f"Valor indisponível no Saldo Geral do Ciclo. Resta: {saldo_ciclo:,.2f}"
        
        if ne.aditivo_vinculado_id:
            saldo_adt = self.get_saldo_aditivo_especifico(ne.aditivo_vinculado_id)
            if ne.valor_inicial > saldo_adt + 0.01: return False, f"Valor excede o saldo do Aditivo. Resta: {saldo_adt:,.2f}"
            
        if 0 <= ne.subcontrato_idx < len(self.lista_servicos):
            sub = self.lista_servicos[ne.subcontrato_idx]
            
            gasto_sub = sum(e.valor_inicial for e in self.lista_notas_empenho 
                            if e.subcontrato_idx == ne.subcontrato_idx and e.ciclo_id == ne.ciclo_id)
            
            valor_servico_no_ciclo = sub.get_valor_ciclo(ne.ciclo_id)
            
            saldo_sub = valor_servico_no_ciclo - gasto_sub
            if ne.valor_inicial > saldo_sub + 0.01: return False, f"Valor excede o saldo do serviço '{sub.descricao}' neste ciclo."
            
        self.lista_notas_empenho.append(ne)
        return True, "Nota de Empenho vinculada."

    def to_dict(self):
        d = self.__dict__.copy()
        d['ciclos'] = [c.to_dict() for c in self.ciclos]
        d['lista_notas_empenho'] = [ne.to_dict() for ne in self.lista_notas_empenho]
        d['lista_aditivos'] = [adt.to_dict() for adt in self.lista_aditivos]
        d['lista_servicos'] = [sub.to_dict() for sub in self.lista_servicos]
        return d

    @staticmethod
    def from_dict(d):
        c = Contrato(d['numero'], d['prestador'], d['descricao'], d['valor_inicial'], d['vigencia_inicio'],
                     d['vigencia_fim'], d['comp_inicio'], d['comp_fim'], d.get('licitacao', ''), d.get('dispensa', ''))
        c.ciclos = [CicloFinanceiro.from_dict(cd) for cd in d['ciclos']]
        c.lista_servicos = [SubContrato.from_dict(sd) for sd in d['lista_servicos']]
        c.lista_aditivos = [Aditivo.from_dict(ad) for ad in d['lista_aditivos']]
        c.lista_notas_empenho = [NotaEmpenho.from_dict(nd) for nd in d['lista_notas_empenho']]
        c._contador_aditivos = d.get('_contador_aditivos', 0)

        for adt in c.lista_aditivos:
            if adt.tipo == "Valor" and adt.ciclo_pertencente_id != -1:
                for ciclo in c.ciclos:
                    if ciclo.id_ciclo == adt.ciclo_pertencente_id:
                        ciclo.aditivos_valor.append(adt)
                        break
        return c


# --- 2. DIÁLOGOS ---

class DialogoCriarContrato(QDialog):
    def __init__(self, contrato_editar=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cadastro de Contrato")
        self.setFixedWidth(600)
        layout = QFormLayout(self)
        self.inp_numero = QLineEdit();
        self.inp_prestador = QLineEdit()
        self.inp_desc = QLineEdit();
        self.inp_valor = CurrencyInput()
        self.inp_licitacao = QLineEdit();
        self.inp_dispensa = QLineEdit()
        self.date_vig_ini = QDateEdit(QDate.currentDate());
        self.date_vig_ini.setCalendarPopup(True)
        self.date_vig_fim = QDateEdit(QDate.currentDate().addYears(1));
        self.date_vig_fim.setCalendarPopup(True)
        self.inp_comp_ini = QLineEdit(QDate.currentDate().toString("MM/yyyy"));
        self.inp_comp_ini.setInputMask("99/9999")
        self.inp_comp_fim = QLineEdit(QDate.currentDate().addYears(1).toString("MM/yyyy"));
        self.inp_comp_fim.setInputMask("99/9999")
        layout.addRow("Número Contrato:", self.inp_numero);
        layout.addRow("Prestador:", self.inp_prestador)
        layout.addRow("Objeto:", self.inp_desc);
        layout.addRow("Valor Inicial (Ciclo 0):", self.inp_valor)
        layout.addRow("Licitação/Edital:", self.inp_licitacao);
        layout.addRow("Inexigibilidade/Disp:", self.inp_dispensa)
        layout.addRow("Início Vigência:", self.date_vig_ini);
        layout.addRow("Fim Vigência:", self.date_vig_fim)
        layout.addRow("Competência Inicial:", self.inp_comp_ini);
        layout.addRow("Competência Final:", self.inp_comp_fim)
        if contrato_editar:
            self.inp_numero.setText(contrato_editar.numero);
            self.inp_prestador.setText(contrato_editar.prestador)
            self.inp_desc.setText(contrato_editar.descricao);
            self.inp_valor.set_value(contrato_editar.valor_inicial);
            self.inp_valor.setReadOnly(True)
            self.inp_licitacao.setText(contrato_editar.licitacao);
            self.inp_dispensa.setText(contrato_editar.dispensa)
            self.date_vig_ini.setDate(str_to_date(contrato_editar.vigencia_inicio));
            self.date_vig_fim.setDate(str_to_date(contrato_editar.vigencia_fim))
            self.inp_comp_ini.setText(contrato_editar.comp_inicio);
            self.inp_comp_fim.setText(contrato_editar.comp_fim)
        botoes = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        botoes.accepted.connect(self.accept);
        botoes.rejected.connect(self.reject);
        layout.addWidget(botoes)

    def get_dados(self): return (self.inp_numero.text(), self.inp_prestador.text(), self.inp_desc.text(),
                                 self.inp_valor.get_value(), self.date_vig_ini.text(), self.date_vig_fim.text(),
                                 self.inp_comp_ini.text(), self.inp_comp_fim.text(), self.inp_licitacao.text(),
                                 self.inp_dispensa.text())

class DialogoNovoEmpenho(QDialog):
    def __init__(self, contrato, ne_editar=None, parent=None):
        super().__init__(parent); self.contrato = contrato; self.setWindowTitle("Nota de Empenho"); self.setFixedWidth(500)
        layout = QFormLayout(self)
        self.inp_num = QLineEdit(); self.inp_desc = QLineEdit(); self.inp_fonte = QLineEdit(); self.date_emissao = QDateEdit(QDate.currentDate()); self.date_emissao.setCalendarPopup(True); self.inp_val = CurrencyInput()
        self.combo_ciclo = QComboBox(); self.combo_ciclo.currentIndexChanged.connect(self.atualizar_combo_aditivos); self.combo_aditivo = QComboBox()
        self.combo_sub = QComboBox()

        ultimo_ciclo_id = contrato.ciclos[-1].id_ciclo if contrato.ciclos else 0
        for sub in contrato.lista_servicos:
            val_atual = sub.get_valor_ciclo(ultimo_ciclo_id)
            self.combo_sub.addItem(f"{sub.descricao} (Ciclo Atual: {fmt_br(val_atual)})")

        for c in contrato.ciclos:
            saldo = contrato.get_saldo_ciclo_geral(c.id_ciclo)
            if ne_editar and ne_editar.ciclo_id == c.id_ciclo: saldo += ne_editar.valor_inicial
            self.combo_ciclo.addItem(f"{c.nome} (Livre: R$ {fmt_br(saldo)})", c.id_ciclo)

        layout.addRow("1. Ciclo Financeiro:", self.combo_ciclo); layout.addRow("2. Vincular a Aditivo de Valor (Opcional):", self.combo_aditivo)
        layout.addRow("Número da Nota:", self.inp_num); layout.addRow("Data de Emissão:", self.date_emissao); layout.addRow("Fonte de Recurso:", self.inp_fonte)
        layout.addRow("Descrição:", self.inp_desc); layout.addRow("Vincular a Serviço:", self.combo_sub); layout.addRow("Valor:", self.inp_val)
        
        if ne_editar:
            self.inp_num.setText(ne_editar.numero); self.inp_desc.setText(ne_editar.descricao); self.inp_fonte.setText(ne_editar.fonte_recurso)
            self.date_emissao.setDate(str_to_date(ne_editar.data_emissao)); self.inp_val.set_value(ne_editar.valor_inicial)
            idx_c = self.combo_ciclo.findData(ne_editar.ciclo_id); 
            if idx_c >= 0: self.combo_ciclo.setCurrentIndex(idx_c)
            self.atualizar_combo_aditivos() 
            if ne_editar.aditivo_vinculado_id:
                idx_a = self.combo_aditivo.findData(ne_editar.aditivo_vinculado_id)
                if idx_a >= 0: self.combo_aditivo.setCurrentIndex(idx_a)
            if ne_editar.subcontrato_idx < self.combo_sub.count(): self.combo_sub.setCurrentIndex(ne_editar.subcontrato_idx)
            if len(ne_editar.historico) > 1: self.inp_val.setEnabled(False) 
        else:
            self.combo_ciclo.setCurrentIndex(self.combo_ciclo.count()-1); self.atualizar_combo_aditivos()
        
        botoes = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        botoes.accepted.connect(self.accept)
        botoes.rejected.connect(self.reject) # <--- LINHA QUE FALTAVA
        layout.addWidget(botoes)

    def atualizar_combo_aditivos(self):
        self.combo_aditivo.clear(); self.combo_aditivo.addItem("--- Usar Saldo Geral do Ciclo ---", None)
        id_ciclo_atual = self.combo_ciclo.currentData(); 
        if id_ciclo_atual is None: return
        ciclo_obj = next((c for c in self.contrato.ciclos if c.id_ciclo == id_ciclo_atual), None)
        if ciclo_obj:
            for adt in ciclo_obj.aditivos_valor:
                saldo = self.contrato.get_saldo_aditivo_especifico(adt.id_aditivo)
                self.combo_aditivo.addItem(f"{adt.descricao} (Resta: R$ {fmt_br(saldo)})", adt.id_aditivo)

    def get_dados(self): return (self.inp_num.text(), self.inp_desc.text(), self.combo_sub.currentIndex(), self.inp_val.get_value(), self.inp_fonte.text(), self.date_emissao.text(), self.combo_ciclo.currentData(), self.combo_aditivo.currentData())

class DialogoAditivo(QDialog):
    def __init__(self, contrato, aditivo_editar=None, parent=None):
        super().__init__(parent); self.contrato = contrato 
        self.setWindowTitle("Aditivo Contratual"); self.setFixedWidth(450)
        layout = QFormLayout(self)
        
        self.combo_tipo = QComboBox(); self.combo_tipo.addItems(["Valor (Acréscimo/Decréscimo)", "Prazo (Prorrogação)"])
        self.combo_tipo.currentIndexChanged.connect(self.mudar_tipo)
        
        self.chk_renovacao = QCheckBox("Haverá renovação de valor? (Cria Novo Ciclo/Saldo)")
        self.chk_renovacao.setVisible(False); self.chk_renovacao.toggled.connect(self.mudar_tipo)
        
        self.lbl_info = QLabel(""); self.lbl_info.setStyleSheet("color: blue; font-size: 10px")
        
        self.combo_servico = QComboBox()
        self.combo_servico.addItem("--- Nenhum / Genérico ---", -1)
        for i, serv in enumerate(contrato.lista_servicos):
            self.combo_servico.addItem(f"{serv.descricao} (Base: {fmt_br(serv.get_valor_ciclo(0))})", i)

        self.inp_valor = CurrencyInput(); self.date_inicio = QDateEdit(QDate.currentDate()); self.date_inicio.setCalendarPopup(True)
        self.date_nova = QDateEdit(QDate.currentDate().addYears(1)); self.date_nova.setCalendarPopup(True); self.date_nova.setEnabled(False)
        self.inp_desc = QLineEdit()
        
        layout.addRow("Tipo:", self.combo_tipo)
        layout.addRow("", self.chk_renovacao)
        layout.addRow("", self.lbl_info)
        layout.addRow("Vincular a Serviço (Valor):", self.combo_servico)
        layout.addRow("Início da Vigência:", self.date_inicio)
        layout.addRow("Valor do Aditivo:", self.inp_valor)
        layout.addRow("Nova Data Fim (Contrato):", self.date_nova)
        layout.addRow("Justificativa:", self.inp_desc)
        
        if aditivo_editar:
            idx = 0 if aditivo_editar.tipo == "Valor" else 1
            self.combo_tipo.setCurrentIndex(idx); self.inp_valor.set_value(aditivo_editar.valor)
            if aditivo_editar.data_nova: self.date_nova.setDate(str_to_date(aditivo_editar.data_nova))
            if aditivo_editar.data_inicio_vigencia: self.date_inicio.setDate(str_to_date(aditivo_editar.data_inicio_vigencia))
            self.inp_desc.setText(aditivo_editar.descricao); self.chk_renovacao.setChecked(aditivo_editar.renovacao_valor)
            
            idx_serv = self.combo_servico.findData(aditivo_editar.servico_idx)
            if idx_serv >= 0: self.combo_servico.setCurrentIndex(idx_serv)
            
            self.mudar_tipo()
            
        botoes = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        botoes.accepted.connect(self.accept)
        botoes.rejected.connect(self.reject) # <--- LINHA QUE FALTAVA
        layout.addWidget(botoes)

    def mudar_tipo(self):
        is_prazo = self.combo_tipo.currentText().startswith("Prazo")
        if is_prazo:
            self.chk_renovacao.setVisible(True); self.date_nova.setEnabled(True)
            self.inp_valor.setEnabled(self.chk_renovacao.isChecked()); self.date_inicio.setEnabled(True)
            self.combo_servico.setEnabled(False) 
            if self.chk_renovacao.isChecked(): self.combo_servico.setEnabled(True)
            self.lbl_info.setText("Este aditivo iniciará um NOVO 'Ciclo Financeiro'." if self.chk_renovacao.isChecked() else "Apenas prorrogação de data.")
        else:
            self.chk_renovacao.setVisible(False); self.chk_renovacao.setChecked(False)
            self.inp_valor.setEnabled(True); self.date_nova.setEnabled(False); self.date_inicio.setEnabled(False)
            self.combo_servico.setEnabled(True) 
            self.lbl_info.setText("Valor somado ao Ciclo Atual.")

    def get_dados(self):
        tipo = "Valor" if self.combo_tipo.currentText().startswith("Valor") else "Prazo"
        return tipo, self.inp_valor.get_value(), self.date_nova.text(), self.inp_desc.text(), self.chk_renovacao.isChecked(), self.date_inicio.text(), self.combo_servico.currentData()
    
class DialogoPagamento(QDialog):
    def __init__(self, comp_inicio, comp_fim, pg_editar=None, parent=None):
        super().__init__(parent);
        self.setWindowTitle("Pagamento");
        layout = QFormLayout(self)
        self.combo_comp = QComboBox();
        lista_meses = gerar_competencias(comp_inicio, comp_fim);
        if not lista_meses: lista_meses = ["Erro datas contrato"]
        self.combo_comp.addItems(lista_meses);
        self.inp_valor = CurrencyInput()
        layout.addRow("Competência:", self.combo_comp);
        layout.addRow("Valor:", self.inp_valor)
        if pg_editar:
            idx = self.combo_comp.findText(pg_editar.competencia);
            if idx >= 0: self.combo_comp.setCurrentIndex(idx)
            self.inp_valor.set_value(pg_editar.valor)
        botoes = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel);
        botoes.accepted.connect(self.accept)
        botoes.rejected.connect(self.reject) # <--- LINHA QUE FALTAVA
        layout.addWidget(botoes)

    def get_dados(self):
        return self.combo_comp.currentText(), self.inp_valor.get_value()

class DialogoSubContrato(QDialog):
    def __init__(self, sub_editar=None, valor_editar=None, parent=None):
        super().__init__(parent); self.setWindowTitle("Serviço / Subcontrato"); layout = QFormLayout(self)
        self.inp_desc = QLineEdit(); self.inp_valor = CurrencyInput()
        layout.addRow("Descrição:", self.inp_desc); layout.addRow("Valor Estimado (Neste Ciclo):", self.inp_valor)
        
        if sub_editar: 
            self.inp_desc.setText(sub_editar.descricao)
            if valor_editar is not None: self.inp_valor.set_value(valor_editar)
            else: self.inp_valor.set_value(sub_editar.get_valor_ciclo(0))
            
        botoes = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        botoes.accepted.connect(self.accept)
        botoes.rejected.connect(self.reject) # <--- LINHA QUE FALTAVA
        layout.addWidget(botoes)

    def get_dados(self): return self.inp_desc.text(), self.inp_valor.get_value()




# --- 3. SISTEMA PRINCIPAL ---

class SistemaGestao(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db_contratos = []
        self.contrato_selecionado = None
        self.ne_selecionada = None
        self.arquivo_db = "dados_sistema.json"

        self.tema_escuro = False 

        self.init_ui()
        self.carregar_dados()

    def closeEvent(self, event):
        self.salvar_dados()
        event.accept()

    def salvar_dados(self):
        dados = [c.to_dict() for c in self.db_contratos]
        try:
            with open(self.arquivo_db, 'w', encoding='utf-8-sig') as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar: {e}")

    def carregar_dados(self):
        if not os.path.exists(self.arquivo_db): return
        try:
            with open(self.arquivo_db, 'r', encoding='utf-8-sig') as f:
                dados = json.load(f)
                self.db_contratos = [Contrato.from_dict(d) for d in dados]
            self.filtrar_contratos()
        except Exception as e:
            QMessageBox.critical(self, "Erro ao Carregar", f"Não foi possível ler os dados salvos:\n{str(e)}")

    def alternar_tema(self):
        self.tema_escuro = not self.tema_escuro
        app = QApplication.instance()

        if self.tema_escuro:
            palette = QPalette()
            palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
            palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
            app.setPalette(palette)
        else:
            app.setPalette(QPalette())

    def init_ui(self):
        self.setWindowTitle("SGF - Gestão de Contratos")
        self.setGeometry(50, 50, 1300, 850)
        mb = self.menuBar()
        
        m_arq = mb.addMenu("Arquivo")
        m_exp = m_arq.addMenu("Exportar para Excel (CSV)...")
        m_exp.addAction("Contrato Completo (Selecionado)", self.exportar_contrato_completo)
        m_exp.addAction("Nota de Empenho Selecionada", self.exportar_ne_atual)
        m_arq.addSeparator()
        
        acao_salvar = QAction("Salvar Agora", self)
        acao_salvar.setShortcut("Ctrl+S")
        acao_salvar.triggered.connect(self.salvar_dados)
        m_arq.addAction(acao_salvar)
        m_arq.addAction("Sair", self.close)

        m_con = mb.addMenu("Contratos")
        m_con.addAction("Novo Contrato...", self.abrir_novo_contrato)
        m_con.addAction("Listar / Pesquisar Contratos", self.voltar_para_pesquisa)

        m_imp = mb.addMenu("Importação (Lote)")
        m_imp.addAction("Importar Contratos (CSV)...", self.importar_contratos)
        m_imp.addAction("Importar Serviços (CSV)...", self.importar_servicos)
        m_imp.addAction("Importar Empenhos (CSV)...", self.importar_empenhos)
        m_imp.addAction("Importar Pagamentos (CSV)...", self.importar_pagamentos)

        m_exi = mb.addMenu("Exibir")
        m_exi.addAction("Alternar Tema (Claro/Escuro)", self.alternar_tema)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.page_pesquisa = QWidget()
        layout_p = QVBoxLayout(self.page_pesquisa); layout_p.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        container = QFrame(); container.setFixedWidth(900); l_cont = QVBoxLayout(container)
        
        lbl_logo = QLabel("Pesquisa de Contratos")
        lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_logo.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        lbl_logo.setStyleSheet("color: #2c3e50; margin-bottom: 20px; margin-top: 50px")
        
        self.inp_search = QLineEdit()
        self.inp_search.setPlaceholderText("Digite para pesquisar...")
        self.inp_search.setStyleSheet("font-size: 16px; padding: 10px;")
        self.inp_search.textChanged.connect(self.filtrar_contratos)
        
        self.tabela_resultados = QTableWidget()
        self.tabela_resultados.setColumnCount(4)
        self.tabela_resultados.setHorizontalHeaderLabels(["Número", "Prestador", "Objeto", "Status"])
        self.tabela_resultados.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabela_resultados.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela_resultados.cellDoubleClicked.connect(self.abrir_contrato_pesquisa)
        self.tabela_resultados.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tabela_resultados.customContextMenuRequested.connect(self.menu_pesquisa)
        
        l_cont.addWidget(lbl_logo); l_cont.addWidget(self.inp_search); l_cont.addWidget(self.tabela_resultados)
        layout_h = QHBoxLayout(); layout_h.addStretch(); layout_h.addWidget(container); layout_h.addStretch(); layout_p.addLayout(layout_h)

        self.page_detalhes = QWidget()
        self.layout_detalhes = QVBoxLayout(self.page_detalhes)

        top_bar = QHBoxLayout()
        btn_voltar = QPushButton("← Voltar")
        btn_voltar.clicked.connect(self.voltar_para_pesquisa)

        header_text_layout = QVBoxLayout()
        self.lbl_prestador = QLabel("NOME DO PRESTADOR")
        self.lbl_prestador.setFont(QFont("Arial", 15, QFont.Weight.Bold))
        self.lbl_prestador.setStyleSheet("color: #2c3e50;")

        self.lbl_titulo = QLabel("Contrato nº ...")
        self.lbl_titulo.setFont(QFont("Arial", 13))
        self.lbl_titulo.setStyleSheet("color: #555;")

        header_text_layout.addWidget(self.lbl_prestador)
        header_text_layout.addWidget(self.lbl_titulo)

        top_bar.addWidget(btn_voltar); top_bar.addSpacing(20); top_bar.addLayout(header_text_layout); top_bar.addStretch()
        self.layout_detalhes.addLayout(top_bar)

        layout_filtro = QHBoxLayout()
        layout_filtro.setContentsMargins(0, 10, 0, 0)
        
        lbl_filtro = QLabel("Visualizar dados do Ciclo:")
        lbl_filtro.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        
        self.combo_ciclo_visualizacao = QComboBox() 
        self.combo_ciclo_visualizacao.setFixedWidth(300)
        self.combo_ciclo_visualizacao.currentIndexChanged.connect(self.atualizar_painel_detalhes)
        
        layout_filtro.addWidget(lbl_filtro)
        layout_filtro.addWidget(self.combo_ciclo_visualizacao)
        layout_filtro.addStretch()
        
        self.layout_detalhes.addLayout(layout_filtro)

        self.abas = QTabWidget()
        self.layout_detalhes.addWidget(self.abas)

        self.tab_dados = QWidget(); l_dados = QFormLayout(self.tab_dados)
        self.lbl_d_licitacao = QLabel("-"); self.lbl_d_dispensa = QLabel("-")
        self.lbl_d_vigencia = QLabel("-"); self.lbl_d_comp = QLabel("-"); self.lbl_d_resumo_ciclos = QLabel("-")
        l_dados.addRow("Licitação:", self.lbl_d_licitacao); l_dados.addRow("Dispensa:", self.lbl_d_dispensa)
        l_dados.addRow("Vigência:", self.lbl_d_vigencia); l_dados.addRow("Competência:", self.lbl_d_comp)
        l_dados.addRow("Ciclos:", self.lbl_d_resumo_ciclos)
        self.abas.addTab(self.tab_dados, "Dados")

        tab_fin = QWidget(); l_fin = QVBoxLayout(tab_fin)
        
        from PyQt6.QtWidgets import QGroupBox, QGridLayout
        self.grp_detalhes_ne = QGroupBox("Detalhes da Nota de Empenho Selecionada")
        self.grp_detalhes_ne.setMaximumHeight(100)
        layout_det_ne = QGridLayout(self.grp_detalhes_ne)
        
        self.lbl_ne_ciclo = QLabel("Ciclo: -"); self.lbl_ne_emissao = QLabel("Emissão: -")
        self.lbl_ne_aditivo = QLabel("Aditivo: -"); self.lbl_ne_desc = QLabel("Descrição: -"); self.lbl_ne_desc.setWordWrap(True)
        
        font_bold = QFont("Arial", 9, QFont.Weight.Bold)
        for l in [self.lbl_ne_ciclo, self.lbl_ne_emissao, self.lbl_ne_aditivo, self.lbl_ne_desc]: l.setFont(font_bold)
        
        layout_det_ne.addWidget(self.lbl_ne_ciclo, 0, 0); layout_det_ne.addWidget(self.lbl_ne_emissao, 0, 1)
        layout_det_ne.addWidget(self.lbl_ne_aditivo, 0, 2); layout_det_ne.addWidget(self.lbl_ne_desc, 1, 0, 1, 3)
        l_fin.addWidget(self.grp_detalhes_ne)

        btns_fin = QHBoxLayout()
        b_ne = QPushButton("+ NE"); b_ne.clicked.connect(self.dialogo_nova_ne)
        b_pg = QPushButton("Pagar"); b_pg.clicked.connect(self.abrir_pagamento)
        btns_fin.addWidget(b_ne); btns_fin.addWidget(b_pg); btns_fin.addStretch()
        l_fin.addLayout(btns_fin)

        self.tab_empenhos = TabelaExcel()
        self.tab_empenhos.setColumnCount(7)
        self.tab_empenhos.setHorizontalHeaderLabels(["NE", "Fonte", "Serviço", "Valor Original", "Pago", "Saldo", "Média do Serviço"])
        self.tab_empenhos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tab_empenhos.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tab_empenhos.itemClicked.connect(self.selecionar_ne)
        self.tab_empenhos.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tab_empenhos.customContextMenuRequested.connect(self.menu_empenho)
        l_fin.addWidget(self.tab_empenhos)

        l_fin.addWidget(QLabel("Histórico Financeiro:"))
        self.tab_mov = TabelaExcel()
        self.tab_mov.setColumnCount(4)
        self.tab_mov.setHorizontalHeaderLabels(["Comp.", "Tipo", "Valor", "Saldo"])
        self.tab_mov.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tab_mov.setMaximumHeight(200)
        self.tab_mov.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tab_mov.customContextMenuRequested.connect(self.menu_movimentacao)
        l_fin.addWidget(self.tab_mov)
        
        self.abas.addTab(tab_fin, "Financeiro")

        tab_serv = QWidget(); l_serv = QVBoxLayout(tab_serv)
        
        b_nserv = QPushButton("+ Serviço")
        b_nserv.setFixedWidth(150)
        b_nserv.clicked.connect(self.abrir_novo_servico)
        l_serv.addWidget(b_nserv)
        
        self.tab_subcontratos = TabelaExcel()
        self.tab_subcontratos.setColumnCount(6)
        self.tab_subcontratos.setHorizontalHeaderLabels(["Descrição", 
            "Orçamento", 
            "Empenhado", 
            "Saldo a Empenhar",  # (Orç - Empenhado)
            "A Pagar (NEs)",     # (Empenhado - Pago)
            "Saldo Real (Caixa)" # (Orç - Pago)
        ])

        self.tab_subcontratos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tab_subcontratos.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tab_subcontratos.customContextMenuRequested.connect(self.menu_subcontrato)
        l_serv.addWidget(self.tab_subcontratos)
        
        self.abas.addTab(tab_serv, "Serviços")

        tab_adit = QWidget(); l_adit = QVBoxLayout(tab_adit)
        
        b_nadit = QPushButton("+ Aditivo")
        b_nadit.setFixedWidth(150)
        b_nadit.clicked.connect(self.abrir_novo_aditivo)
        l_adit.addWidget(b_nadit)
        
        self.tab_aditivos = TabelaExcel()
        self.tab_aditivos.setColumnCount(6)
        self.tab_aditivos.setHorizontalHeaderLabels(["Tipo", "Renova?", "Início Vigência", "Fim Vigência", "Valor", "Descrição"])
        self.tab_aditivos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tab_aditivos.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tab_aditivos.customContextMenuRequested.connect(self.menu_aditivo)
        l_adit.addWidget(self.tab_aditivos)
        
        self.abas.addTab(tab_adit, "Aditivos")

        self.stack.addWidget(self.page_pesquisa)
        self.stack.addWidget(self.page_detalhes)
        self.stack.setCurrentIndex(0)

    # --- LÓGICA GERAL ---

    def voltar_para_pesquisa(self):
        self.salvar_dados()
        self.contrato_selecionado = None;
        self.ne_selecionada = None;
        self.inp_search.setText("");
        self.filtrar_contratos();
        self.stack.setCurrentIndex(0)

    def filtrar_contratos(self):
        texto = self.inp_search.text().lower();
        self.tabela_resultados.setRowCount(0)
        
        def item_centro(txt):
            i = QTableWidgetItem(str(txt))
            i.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            return i

        for c in self.db_contratos:
            if (texto in c.numero.lower() or texto in c.prestador.lower() or texto in c.descricao.lower() or texto == ""):
                row = self.tabela_resultados.rowCount();
                self.tabela_resultados.insertRow(row)
                self.tabela_resultados.setItem(row, 0, item_centro(c.numero));
                self.tabela_resultados.setItem(row, 1, item_centro(c.prestador));
                self.tabela_resultados.setItem(row, 2, item_centro(c.descricao))
                hoje = datetime.now();
                fim = str_to_date(c.get_vigencia_final_atual());
                st = "Vigente" if fim >= hoje else "Vencido";
                i_st = QTableWidgetItem(st); i_st.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                i_st.setForeground(QColor("green" if st == "Vigente" else "red"));
                self.tabela_resultados.setItem(row, 3, i_st)
                self.tabela_resultados.item(row, 0).setData(Qt.ItemDataRole.UserRole, c)

    def abrir_contrato_pesquisa(self, row, col):
        self.contrato_selecionado = self.tabela_resultados.item(row, 0).data(Qt.ItemDataRole.UserRole);
        self.ne_selecionada = None;
        self.atualizar_painel_detalhes();
        self.stack.setCurrentIndex(1)

    def menu_pesquisa(self, pos):
        item = self.tabela_resultados.itemAt(pos)
        if item:
            c = self.tabela_resultados.item(item.row(), 0).data(Qt.ItemDataRole.UserRole)
            menu = QMenu(self)
            menu.addAction("Abrir", lambda: self.abrir_contrato_pesquisa(item.row(), 0))
            menu.addAction("Editar", lambda: self.editar_contrato_externo(c))
            menu.addAction("Excluir", lambda: self.excluir_contrato_externo(c))
            menu.exec(self.tabela_resultados.mapToGlobal(pos))

    def abrir_novo_contrato(self):
        dial = DialogoCriarContrato(parent=self)
        if dial.exec(): self.db_contratos.append(
            Contrato(*dial.get_dados())); self.filtrar_contratos(); self.salvar_dados()

    def editar_contrato_externo(self, c):
        dial = DialogoCriarContrato(contrato_editar=c, parent=self)
        if dial.exec():
            d = dial.get_dados()
            c.numero, c.prestador, c.descricao, _, c.vigencia_inicio, c.vigencia_fim, c.comp_inicio, c.comp_fim, c.licitacao, c.dispensa = d
            self.filtrar_contratos();
            self.salvar_dados()

    def excluir_contrato_externo(self, c):
        if QMessageBox.question(self, "Excluir", f"Excluir {c.numero}?") == QMessageBox.StandardButton.Yes:
            self.db_contratos.remove(c);
            self.filtrar_contratos();
            self.salvar_dados()

    def dialogo_nova_ne(self):
        if not self.contrato_selecionado: return
        if not self.contrato_selecionado.lista_servicos: QMessageBox.warning(self, "Aviso",
                                                                             "Cadastre um Serviço antes."); return
        dial = DialogoNovoEmpenho(self.contrato_selecionado, parent=self)
        if dial.exec():
            num, desc, idx, val, fonte, data_em, id_ciclo, id_aditivo = dial.get_dados()
            nova_ne = NotaEmpenho(num, val, desc, idx, fonte, data_em, id_ciclo, id_aditivo)
            ok, msg = self.contrato_selecionado.adicionar_nota_empenho(nova_ne)
            if ok:
                self.atualizar_painel_detalhes(); self.salvar_dados()
            else:
                QMessageBox.critical(self, "Bloqueio", msg)

    def abrir_pagamento(self):
        if not self.ne_selecionada:
            QMessageBox.warning(self, "Aviso", "Selecione uma Nota de Empenho primeiro.")
            return
        dial = DialogoPagamento(self.contrato_selecionado.comp_inicio, self.contrato_selecionado.comp_fim, parent=self)
        if dial.exec():
            c, v = dial.get_dados();
            ok, msg = self.ne_selecionada.realizar_pagamento(v, c)
            if not ok: QMessageBox.warning(self, "Erro", msg)
            self.atualizar_painel_detalhes();
            self.atualizar_movimentos();
            self.salvar_dados()

    def abrir_novo_servico(self):
        if not self.contrato_selecionado: return
        dial = DialogoSubContrato(parent=self);
        if dial.exec(): self.contrato_selecionado.lista_servicos.append(
            SubContrato(*dial.get_dados())); self.atualizar_painel_detalhes(); self.salvar_dados()

    def abrir_novo_aditivo(self):
        if not self.contrato_selecionado: return
        dial = DialogoAditivo(self.contrato_selecionado, parent=self)
        if dial.exec():
            # Pegamos o novo campo servico_idx (o último retorno)
            tipo, valor, data_n, desc, renova, data_ini, serv_idx = dial.get_dados()
            adt = Aditivo(0, tipo, valor, data_n, desc, renova, data_ini, serv_idx) 
            msg = self.contrato_selecionado.adicionar_aditivo(adt)
            QMessageBox.information(self, "Aditivo", msg)
            self.atualizar_painel_detalhes(); self.salvar_dados()

    # --- EXPORTAÇÃO E IMPORTAÇÃO ---

    def exportar_contrato_completo(self):
        if not self.contrato_selecionado: QMessageBox.warning(self, "Aviso", "Selecione um contrato."); return
        fname, _ = QFileDialog.getSaveFileName(self, "Exportar Contrato", f"Contrato_{self.contrato_selecionado.numero}.csv", "CSV Files (*.csv)")
        if not fname: return
        
        # Pega o ciclo atual da visualização para exportar os valores de serviço corretos
        ciclo_view_id = self.combo_ciclo_visualizacao.currentData()
        if ciclo_view_id is None: ciclo_view_id = 0
        
        try:
            with open(fname, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f, delimiter=';'); c = self.contrato_selecionado
                writer.writerow(["=== DADOS GERAIS ==="])
                writer.writerow(["Número", "Prestador", "Objeto", "Vigência"])
                writer.writerow([c.numero, c.prestador, c.descricao, f"{c.vigencia_inicio} a {c.get_vigencia_final_atual()}"])
                writer.writerow([])
                
                writer.writerow(["=== ADITIVOS ==="])
                writer.writerow(["Tipo", "Valor", "Data Nova", "Descrição"])
                for adt in c.lista_aditivos: writer.writerow([adt.tipo, fmt_br(adt.valor), adt.data_nova, adt.descricao])
                writer.writerow([])
                
                writer.writerow([f"=== SERVIÇOS (CICLO VISUALIZADO: {ciclo_view_id}) ==="])
                writer.writerow(["Descrição", "Orçamento Ciclo", "Empenhado", "Saldo"])
                for idx, sub in enumerate(c.lista_servicos):
                    # CORREÇÃO: Pega valor do ciclo e gastos do ciclo
                    val_ciclo = sub.get_valor_ciclo(ciclo_view_id)
                    gasto = sum(ne.valor_inicial for ne in c.lista_notas_empenho if ne.subcontrato_idx == idx and ne.ciclo_id == ciclo_view_id)
                    writer.writerow([sub.descricao, fmt_br(val_ciclo), fmt_br(gasto), fmt_br(val_ciclo - gasto)])
                writer.writerow([])
                
                writer.writerow(["=== NOTAS DE EMPENHO (GERAL) ==="])
                writer.writerow(["Número", "Ciclo", "Data", "Serviço", "Valor Inicial", "Valor Pago", "Saldo NE"])
                for ne in c.lista_notas_empenho:
                    serv = c.lista_servicos[ne.subcontrato_idx].descricao if 0 <= ne.subcontrato_idx < len(c.lista_servicos) else "?"
                    writer.writerow([ne.numero, ne.ciclo_id, ne.data_emissao, serv, fmt_br(ne.valor_inicial), fmt_br(ne.valor_pago), fmt_br(ne.valor_inicial - ne.valor_pago)])
                writer.writerow([])

                writer.writerow(["=== HISTÓRICO FINANCEIRO ==="])
                writer.writerow(["NE", "Competência", "Tipo", "Valor"])
                for ne in c.lista_notas_empenho:
                    for mov in ne.historico: writer.writerow([ne.numero, mov.competencia, mov.tipo, fmt_br(mov.valor)])

            QMessageBox.information(self, "Sucesso", "Exportado com sucesso!")
        except Exception as e: QMessageBox.critical(self, "Erro", str(e))
    
    def exportar_ne_atual(self):
        if not self.ne_selecionada: QMessageBox.warning(self, "Aviso", "Selecione uma NE."); return
        fname, _ = QFileDialog.getSaveFileName(self, "Exportar NE", f"NE_{self.ne_selecionada.numero}.csv",
                                               "CSV Files (*.csv)")
        if not fname: return
        try:
            with open(fname, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f, delimiter=';');
                ne = self.ne_selecionada
                writer.writerow(["NE", ne.numero, "Valor", fmt_br(ne.valor_inicial)])
                writer.writerow(["Histórico"]);
                writer.writerow(["Comp", "Tipo", "Valor"])
                for m in ne.historico:
                    writer.writerow([m.competencia, m.tipo, fmt_br(m.valor)])
            QMessageBox.information(self, "Sucesso", "Exportado!")
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))


    def importar_contratos(self):
        instrucao = "CSV (ponto e vírgula):\nNum;Prest;Obj;Valor;VigIni;VigFim;CompIni;CompFim;Lic;Disp"
        QMessageBox.information(self, "Instruções", instrucao)
        fname, _ = QFileDialog.getOpenFileName(self, "CSV Contratos", "", "CSV (*.csv)")
        if not fname: return
        try:
            with open(fname, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter=';');
                next(reader, None)
                for row in reader:
                    if len(row) < 10: continue
                    self.db_contratos.append(
                        Contrato(row[0], row[1], row[2], parse_float_br(row[3]), row[4], row[5], row[6], row[7], row[8],
                                 row[9]))
            self.filtrar_contratos();
            self.salvar_dados();
            QMessageBox.information(self, "Sucesso", "Importado!")
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))

    def importar_empenhos(self):
        if not self.contrato_selecionado: QMessageBox.warning(self, "Aviso", "Abra um contrato."); return
        instrucao = "CSV:\nNE;Valor;Desc;NomeServico;Fonte;Data"
        QMessageBox.information(self, "Instruções", instrucao)
        fname, _ = QFileDialog.getOpenFileName(self, "CSV Empenhos", "", "CSV (*.csv)")
        if not fname: return
        try:
            with open(fname, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter=';');
                next(reader, None)
                for row in reader:
                    if len(row) < 6: continue
                    idx_serv = -1
                    for idx, s in enumerate(self.contrato_selecionado.lista_servicos):
                        if s.descricao.lower() == row[3].strip().lower(): idx_serv = idx; break
                    if idx_serv == -1: continue
                    ne = NotaEmpenho(row[0], parse_float_br(row[1]), row[2], idx_serv, row[4], row[5], 0, None)
                    self.contrato_selecionado.adicionar_nota_empenho(ne)
            self.atualizar_painel_detalhes();
            self.salvar_dados();
            QMessageBox.information(self, "Sucesso", "Importado!")
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))

    def importar_servicos(self):
        if not self.contrato_selecionado:
            QMessageBox.warning(self, "Aviso", "Selecione (abra) um contrato primeiro na tela de pesquisa.")
            return

        # --- NOVO: PERGUNTAR O CICLO ALVO ---
        lista_ciclos = [c.nome for c in self.contrato_selecionado.ciclos]
        # Pega o índice do ciclo atual (último) para sugerir como padrão
        idx_padrao = len(lista_ciclos) - 1
        
        nome_ciclo, ok = QInputDialog.getItem(self, "Selecionar Ciclo", 
                                              "Para qual ciclo financeiro estes valores pertencem?", 
                                              lista_ciclos, idx_padrao, False)
        
        if not ok: return # Usuário cancelou
        
        # Descobrir o ID do ciclo escolhido baseado no nome
        id_ciclo_alvo = 0
        for c in self.contrato_selecionado.ciclos:
            if c.nome == nome_ciclo:
                id_ciclo_alvo = c.id_ciclo
                break
        # ------------------------------------

        instrucao = (
            f"IMPORTANDO PARA: {nome_ciclo}\n\n"
            "ESTRUTURA DO CSV (Separador: ponto e vírgula ';')\n"
            "Colunas: Descrição; Valor"
        )
        QMessageBox.information(self, "Instruções", instrucao)

        fname, _ = QFileDialog.getOpenFileName(self, "Selecionar CSV Serviços", "", "Arquivos CSV (*.csv)")
        if not fname: return

        sucesso = 0
        try:
            with open(fname, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter=';')
                next(reader, None)  # Pula cabeçalho
                for row in reader:
                    if len(row) < 2: continue

                    desc = row[0].strip()
                    val = parse_float_br(row[1])

                    if desc:
                        # 1. Cria o serviço com valor 0.0 inicialmente (no Ciclo 0)
                        sub = SubContrato(desc, 0.0)
                        
                        # 2. Define o valor APENAS no ciclo que o usuário escolheu
                        sub.set_valor_ciclo(id_ciclo_alvo, val)

                        self.contrato_selecionado.lista_servicos.append(sub)
                        sucesso += 1

            # Atualiza o painel visualizando o ciclo onde importamos os dados
            idx_combo = self.combo_ciclo_visualizacao.findData(id_ciclo_alvo)
            if idx_combo >= 0: self.combo_ciclo_visualizacao.setCurrentIndex(idx_combo)
            
            self.atualizar_painel_detalhes()
            self.salvar_dados()
            QMessageBox.information(self, "Concluído", f"{sucesso} serviços importados para o ciclo '{nome_ciclo}'!")

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro na importação: {str(e)}")

    def importar_pagamentos(self):
        if not self.contrato_selecionado:
            QMessageBox.warning(self, "Aviso", "Selecione (abra) um contrato primeiro.")
            return

        instrucao = (
            "ESTRUTURA DO CSV PARA PAGAMENTOS (Separador: ponto e vírgula ';')\n\n"
            "O sistema buscará a Nota de Empenho pelo NÚMERO exato.\n"
            "Colunas necessárias:\n"
            "1. Número da NE (Deve já existir no contrato)\n"
            "2. Valor do Pagamento (ex: 500,00)\n"
            "3. Competência (MM/AAAA)\n"
        )
        QMessageBox.information(self, "Instruções", instrucao)

        fname, _ = QFileDialog.getOpenFileName(self, "Selecionar CSV Pagamentos", "", "Arquivos CSV (*.csv)")
        if not fname: return

        sucesso = 0
        erros = []

        try:
            with open(fname, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter=';')
                next(reader, None)  # Pula cabeçalho
                for i, row in enumerate(reader):
                    if len(row) < 3: continue

                    num_ne = row[0].strip()
                    valor_pg = parse_float_br(row[1])
                    competencia = row[2].strip()

                    # 1. Encontrar a NE
                    ne_alvo = None
                    for ne in self.contrato_selecionado.lista_notas_empenho:
                        if ne.numero.strip() == num_ne:
                            ne_alvo = ne
                            break

                    if not ne_alvo:
                        erros.append(f"Linha {i + 2}: NE '{num_ne}' não encontrada.")
                        continue

                    # 2. Realizar Pagamento
                    ok, msg = ne_alvo.realizar_pagamento(valor_pg, competencia)
                    if ok:
                        sucesso += 1
                    else:
                        erros.append(f"Linha {i + 2} (NE {num_ne}): {msg}")

            self.atualizar_painel_detalhes()
            self.atualizar_movimentos()  # Caso esteja visualizando a NE importada
            self.salvar_dados()

            resumo = f"Importação de Pagamentos Concluída.\nSucessos: {sucesso}"
            if erros:
                resumo += f"\nErros: {len(erros)}\n\n" + "\n".join(erros[:5])
                if len(erros) > 5: resumo += "\n..."

            QMessageBox.information(self, "Relatório", resumo)

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro na importação: {str(e)}")

    # --- MENUS CONTEXTO E AUXILIARES ---

    def selecionar_ne(self, item):
        self.ne_selecionada = self.tab_empenhos.item(item.row(), 0).data(Qt.ItemDataRole.UserRole)

        # Atualizar o Painel de Detalhes Superior
        if self.ne_selecionada and self.contrato_selecionado:
            c = self.contrato_selecionado
            ne = self.ne_selecionada

            # Buscar nome do Ciclo
            nome_ciclo = "?"
            for ciclo in c.ciclos:
                if ciclo.id_ciclo == ne.ciclo_id:
                    nome_ciclo = ciclo.nome
                    break

            # Buscar info Aditivo Vinculado
            info_aditivo = "Não vinculado"
            if ne.aditivo_vinculado_id:
                for a in c.lista_aditivos:
                    if a.id_aditivo == ne.aditivo_vinculado_id:
                        info_aditivo = f"{a.descricao} (ID {a.id_aditivo})"
                        break

            self.lbl_ne_ciclo.setText(f"Ciclo: {nome_ciclo}")
            self.lbl_ne_emissao.setText(f"Emissão: {ne.data_emissao}")
            self.lbl_ne_aditivo.setText(f"Aditivo: {info_aditivo}")
            self.lbl_ne_desc.setText(f"Descrição: {ne.descricao}")

        self.atualizar_movimentos()

    def menu_empenho(self, pos):
        if self.ne_selecionada:
            menu = QMenu(self)
            menu.addAction("Editar", self.editar_ne)
            menu.addAction("Exportar (Detalhado)", self.exportar_ne_atual) # <--- NOVA OPÇÃO
            menu.addAction("Excluir", self.excluir_ne)
            menu.exec(self.tab_empenhos.mapToGlobal(pos))

    def editar_ne(self):
        if not self.ne_selecionada: return
        dial = DialogoNovoEmpenho(self.contrato_selecionado, ne_editar=self.ne_selecionada, parent=self)
        if dial.exec():
            num, desc, idx, val, fonte, data_em, id_ciclo, id_adt = dial.get_dados()
            self.ne_selecionada.numero = num;
            self.ne_selecionada.descricao = desc;
            self.ne_selecionada.fonte_recurso = fonte
            self.ne_selecionada.data_emissao = data_em;
            self.ne_selecionada.subcontrato_idx = idx
            self.ne_selecionada.ciclo_id = id_ciclo;
            self.ne_selecionada.aditivo_vinculado_id = id_adt
            if len(self.ne_selecionada.historico) == 1: self.ne_selecionada.valor_inicial = val;
            self.ne_selecionada.historico[0].valor = val
            self.atualizar_painel_detalhes();
            self.salvar_dados()

    def excluir_ne(self):
        if self.ne_selecionada and QMessageBox.question(self, "Confirma", "Excluir?") == QMessageBox.StandardButton.Yes:
            self.contrato_selecionado.lista_notas_empenho.remove(self.ne_selecionada);
            self.ne_selecionada = None;
            self.atualizar_painel_detalhes();
            self.salvar_dados()

    def menu_subcontrato(self, pos):
        item = self.tab_subcontratos.itemAt(pos)
        if item:
            row = item.row()
            menu = QMenu(self)
            menu.addAction("Editar", lambda: self.editar_servico(row))
            menu.addAction("Excluir", lambda: self.excluir_servico(row))
            menu.addAction("Exportar", lambda: self.exportar_servico(row))
            menu.exec(self.tab_subcontratos.mapToGlobal(pos))

    def exportar_servico(self, row):
        sub = self.contrato_selecionado.lista_servicos[row]
        ciclo_view_id = self.combo_ciclo_visualizacao.currentData() or 0
        fname, _ = QFileDialog.getSaveFileName(self, "Exportar Serviço", f"Serv_{sub.descricao[:10]}.csv", "CSV Files (*.csv)")
        if fname:
            try:
                with open(fname, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.writer(f, delimiter=';')
                    val_ciclo = sub.get_valor_ciclo(ciclo_view_id)
                    
                    writer.writerow(["=== DADOS DO SERVIÇO ==="])
                    writer.writerow(["Descrição", sub.descricao])
                    writer.writerow([f"Valor Orçamento (Ciclo {ciclo_view_id})", fmt_br(val_ciclo)])
                    writer.writerow([])
                    
                    writer.writerow(["=== DETALHAMENTO ==="])
                    writer.writerow(["NE", "Data", "Histórico", "Tipo", "Valor"])
                    total_gasto = 0.0
                    for ne in self.contrato_selecionado.lista_notas_empenho:
                        if ne.subcontrato_idx == row and ne.ciclo_id == ciclo_view_id:
                            total_gasto += ne.valor_inicial
                            for mov in ne.historico:
                                writer.writerow([ne.numero, ne.data_emissao, mov.competencia, mov.tipo, fmt_br(mov.valor)])
                    
                    writer.writerow([])
                    writer.writerow(["Total Empenhado (Neste Ciclo)", fmt_br(total_gasto)])
                    writer.writerow(["Saldo", fmt_br(val_ciclo - total_gasto)])
                QMessageBox.information(self, "Sucesso", "Serviço exportado!")
            except Exception as e: QMessageBox.critical(self, "Erro", str(e))

    # Na classe SistemaGestao:
    def editar_servico(self, row):
        sub = self.contrato_selecionado.lista_servicos[row]
        # Mudança aqui: Usar o combo global
        ciclo_id = self.combo_ciclo_visualizacao.currentData()
        if ciclo_id is None: ciclo_id = 0
        
        valor_atual = sub.get_valor_ciclo(ciclo_id)
        
        dial = DialogoSubContrato(parent=self)
        dial.inp_desc.setText(sub.descricao)
        dial.inp_valor.set_value(valor_atual)
        dial.setWindowTitle(f"Editar Serviço (Ciclo Selecionado)")

        if dial.exec():
            desc, novo_valor = dial.get_dados()
            sub.descricao = desc
            sub.set_valor_ciclo(ciclo_id, novo_valor)
            self.atualizar_painel_detalhes(); self.salvar_dados()

    def excluir_servico(self, row):
        # 1. Verifica se ESTE serviço tem empenhos (Bloqueia)
        if any(ne.subcontrato_idx == row for ne in self.contrato_selecionado.lista_notas_empenho):
            QMessageBox.warning(self, "Erro", "Este serviço possui Notas de Empenho vinculadas e não pode ser excluído.")
            return
        
        # 2. Verifica se ESTE serviço tem aditivos de valor vinculados (Bloqueia)
        if any(adt.servico_idx == row for adt in self.contrato_selecionado.lista_aditivos):
             QMessageBox.warning(self, "Erro", "Este serviço possui Aditivos de Valor vinculados.")
             return

        # 3. Confirmação
        if QMessageBox.question(self, "Excluir", "Tem certeza? Isso reordenará os índices dos serviços.") != QMessageBox.StandardButton.Yes:
            return

        # 4. CORREÇÃO CRÍTICA: Reajustar índices dos outros serviços
        # Se apagamos o serviço 2, quem era serviço 3 vira 2, o 4 vira 3...
        # Precisamos atualizar as NEs e Aditivos que apontam para esses índices maiores.
        
        # Atualiza NEs
        for ne in self.contrato_selecionado.lista_notas_empenho:
            if ne.subcontrato_idx > row:
                ne.subcontrato_idx -= 1
        
        # Atualiza Aditivos
        for adt in self.contrato_selecionado.lista_aditivos:
            if adt.servico_idx > row:
                adt.servico_idx -= 1

        # 5. Agora é seguro apagar
        del self.contrato_selecionado.lista_servicos[row]
        
        self.atualizar_painel_detalhes()
        self.salvar_dados()

    def menu_aditivo(self, pos):
        item = self.tab_aditivos.itemAt(pos)
        if item:
            row = item.row()
            menu = QMenu(self)
            menu.addAction("Editar", lambda: self.editar_aditivo(row))
            menu.addAction("Excluir", lambda: self.excluir_aditivo(row))
            menu.exec(self.tab_aditivos.mapToGlobal(pos))

    def editar_aditivo(self, row):
        adt = self.contrato_selecionado.lista_aditivos[row];
        dial = DialogoAditivo(self.contrato_selecionado, aditivo_editar=adt, parent=self)
        if dial.exec():
            # Atualiza todos os campos incluindo o serviço
            adt.tipo, adt.valor, adt.data_nova, adt.descricao, adt.renovacao_valor, adt.data_inicio_vigencia, adt.servico_idx = dial.get_dados()
            self.atualizar_painel_detalhes(); self.salvar_dados()

    def excluir_aditivo(self, row):
        del self.contrato_selecionado.lista_aditivos[row]; self.atualizar_painel_detalhes(); self.salvar_dados()

    def menu_movimentacao(self, pos):
        item = self.tab_mov.itemAt(pos)
        if item:
            row = item.row()
            if self.ne_selecionada.historico[row].tipo == "Pagamento":
                menu = QMenu(self)
                menu.addAction("Editar", lambda: self.editar_pagamento(row))
                menu.addAction("Excluir", lambda: self.excluir_pagamento(row))
                menu.exec(self.tab_mov.mapToGlobal(pos))

    def editar_pagamento(self, row):
        mov = self.ne_selecionada.historico[row];
        dial = DialogoPagamento(self.contrato_selecionado.comp_inicio, self.contrato_selecionado.comp_fim,
                                pg_editar=mov, parent=self)
        if dial.exec():
            c, v = dial.get_dados();
            ok, m = self.ne_selecionada.editar_movimentacao(row, v, c)
            if ok:
                self.atualizar_painel_detalhes(); self.atualizar_movimentos(); self.salvar_dados()
            else:
                QMessageBox.warning(self, "Erro", m)

    def excluir_pagamento(self, row):
        if self.ne_selecionada.excluir_movimentacao(
            row): self.atualizar_painel_detalhes(); self.atualizar_movimentos(); self.salvar_dados()

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

            # Valores com fmt_br
            self.tab_mov.setItem(row, 2, QTableWidgetItem(fmt_br(m.valor)))

            item_s = QTableWidgetItem(fmt_br(saldo_corrente))
            item_s.setForeground(QColor("#27ae60"))
            self.tab_mov.setItem(row, 3, item_s)

    def atualizar_painel_detalhes(self):
        if not self.contrato_selecionado: return
        c = self.contrato_selecionado
        
        # Cabeçalhos e Infos Gerais
        self.lbl_prestador.setText(c.prestador)
        self.lbl_titulo.setText(f"{c.numero} - {c.descricao}")
        self.lbl_d_licitacao.setText(c.licitacao); self.lbl_d_dispensa.setText(c.dispensa); self.lbl_d_vigencia.setText(f"{c.vigencia_inicio} a {c.get_vigencia_final_atual()}"); self.lbl_d_comp.setText(f"{c.comp_inicio} a {c.comp_fim}")
        
        txt_ciclos = ""
        for ciclo in c.ciclos:
            total = ciclo.get_teto_total(); saldo = c.get_saldo_ciclo_geral(ciclo.id_ciclo)
            txt_ciclos += f"{ciclo.nome}: Teto R$ {fmt_br(total)} | Saldo Livre Geral R$ {fmt_br(saldo)}\n"
        self.lbl_d_resumo_ciclos.setText(txt_ciclos)

        # --- GESTÃO DO COMBOBOX GLOBAL ---
        if self.combo_ciclo_visualizacao.count() != len(c.ciclos):
            idx_atual = self.combo_ciclo_visualizacao.currentIndex()
            self.combo_ciclo_visualizacao.blockSignals(True)
            self.combo_ciclo_visualizacao.clear()
            for ciclo in c.ciclos:
                self.combo_ciclo_visualizacao.addItem(ciclo.nome, ciclo.id_ciclo)
            if idx_atual >= 0 and idx_atual < self.combo_ciclo_visualizacao.count():
                self.combo_ciclo_visualizacao.setCurrentIndex(idx_atual)
            else:
                self.combo_ciclo_visualizacao.setCurrentIndex(self.combo_ciclo_visualizacao.count()-1)
            self.combo_ciclo_visualizacao.blockSignals(False)
        
        ciclo_view_id = self.combo_ciclo_visualizacao.currentData()
        if ciclo_view_id is None: ciclo_view_id = 0

        # Helpers
        def item_centro(txt):
            i = QTableWidgetItem(str(txt)); i.setTextAlignment(Qt.AlignmentFlag.AlignCenter); return i

        # --- PRÉ-CALCULO DAS MÉDIAS DOS SERVIÇOS (NOVO) ---
        # Calcula a média mensal global de cada serviço dentro do ciclo atual
        medias_por_servico = {} # {indice_servico: valor_media}
        for idx_serv, sub in enumerate(c.lista_servicos):
            # Pega todas as NEs deste serviço neste ciclo
            nes_do_servico = [n for n in c.lista_notas_empenho if n.subcontrato_idx == idx_serv and n.ciclo_id == ciclo_view_id]
            
            total_pago = 0.0
            competencias_pagas = set()
            
            for n in nes_do_servico:
                total_pago += n.valor_pago
                for mov in n.historico:
                    if mov.tipo == "Pagamento" and mov.competencia and mov.competencia != "-":
                        competencias_pagas.add(mov.competencia)
            
            if len(competencias_pagas) > 0:
                medias_por_servico[idx_serv] = total_pago / len(competencias_pagas)
            else:
                medias_por_servico[idx_serv] = 0.0

        # --- TABELA EMPENHOS ---
        self.tab_empenhos.setRowCount(0); self.tab_mov.setRowCount(0)
        self.lbl_ne_ciclo.setText("Ciclo: -"); self.lbl_ne_emissao.setText("Emissão: -"); self.lbl_ne_aditivo.setText("Aditivo: -"); self.lbl_ne_desc.setText("Selecione uma NE...")

        for row, ne in enumerate(c.lista_notas_empenho):
            if ne.ciclo_id != ciclo_view_id: continue

            new_row = self.tab_empenhos.rowCount()
            self.tab_empenhos.insertRow(new_row)
            
            n_serv = c.lista_servicos[ne.subcontrato_idx].descricao if 0 <= ne.subcontrato_idx < len(c.lista_servicos) else "?"
            
            self.tab_empenhos.setItem(new_row, 0, item_centro(ne.numero))
            self.tab_empenhos.setItem(new_row, 1, item_centro(ne.fonte_recurso))
            self.tab_empenhos.setItem(new_row, 2, item_centro(n_serv))
            self.tab_empenhos.setItem(new_row, 3, item_centro(fmt_br(ne.valor_inicial)))
            self.tab_empenhos.setItem(new_row, 4, item_centro(fmt_br(ne.valor_pago)))
            
            s = ne.valor_inicial - ne.valor_pago
            i_s = QTableWidgetItem(fmt_br(s)); i_s.setTextAlignment(Qt.AlignmentFlag.AlignCenter); i_s.setForeground(QColor("#27ae60"))
            self.tab_empenhos.setItem(new_row, 5, i_s)
            
            # MUDANÇA: Usa a média calculada do SERVIÇO, e não da NE
            media_servico = medias_por_servico.get(ne.subcontrato_idx, 0.0)
            self.tab_empenhos.setItem(new_row, 6, item_centro(fmt_br(media_servico)))
            
            self.tab_empenhos.item(new_row, 0).setData(Qt.ItemDataRole.UserRole, ne)

        # --- TABELA SERVIÇOS (Dentro de atualizar_painel_detalhes) ---
        self.tab_subcontratos.setRowCount(0)
        for idx, sub in enumerate(c.lista_servicos):
            # 1. Valor do Orçamento (Teto)
            valor_ciclo = sub.get_valor_ciclo(ciclo_view_id)
            
            # 2. Calcular totais de Empenho e Pagamento para este serviço neste ciclo
            gasto_empenhado = 0.0
            gasto_pago = 0.0
            
            for ne in c.lista_notas_empenho:
                if ne.subcontrato_idx == idx and ne.ciclo_id == ciclo_view_id:
                    gasto_empenhado += ne.valor_inicial
                    gasto_pago += ne.valor_pago
            
            # --- CÁLCULOS DOS 3 SALDOS ---
            
            # A. Saldo Não Empenhado (O que ainda posso empenhar)
            saldo_a_empenhar = valor_ciclo - gasto_empenhado
            
            # B. Saldo dos Empenhos (O que empenhei mas não paguei - Restos a Pagar)
            saldo_das_nes = gasto_empenhado - gasto_pago
            
            # C. Saldo do Serviço/Caixa (Orçamento - O que efetivamente saiu do banco)
            saldo_real_caixa = valor_ciclo - gasto_pago

            # --- PREENCHIMENTO DA TABELA ---
            self.tab_subcontratos.insertRow(idx)
            
            # Col 0: Descrição
            self.tab_subcontratos.setItem(idx, 0, item_centro(sub.descricao))
            
            # Col 1: Orçamento
            self.tab_subcontratos.setItem(idx, 1, item_centro(fmt_br(valor_ciclo)))
            
            # Col 2: Total Empenhado
            self.tab_subcontratos.setItem(idx, 2, item_centro(fmt_br(gasto_empenhado)))
            
            # Col 3: Saldo a Empenhar (Verde se positivo, Vermelho se estourou o teto)
            i_s1 = QTableWidgetItem(fmt_br(saldo_a_empenhar))
            i_s1.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            i_s1.setForeground(QColor("#27ae60" if saldo_a_empenhar >= 0 else "red"))
            self.tab_subcontratos.setItem(idx, 3, i_s1)
            
            # Col 4: A Pagar das NEs (Azul para indicar passivo/compromisso)
            i_s2 = QTableWidgetItem(fmt_br(saldo_das_nes))
            i_s2.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            i_s2.setForeground(QColor("#2980b9")) 
            self.tab_subcontratos.setItem(idx, 4, i_s2)
            
            # Col 5: Saldo Real/Caixa (Roxo para diferenciar)
            i_s3 = QTableWidgetItem(fmt_br(saldo_real_caixa))
            i_s3.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            i_s3.setForeground(QColor("#8e44ad")) 
            self.tab_subcontratos.setItem(idx, 5, i_s3)

        # --- TABELA ADITIVOS ---
        self.tab_aditivos.setRowCount(0)
        for row, adt in enumerate(c.lista_aditivos):
            self.tab_aditivos.insertRow(row)
            self.tab_aditivos.setItem(row, 0, item_centro(adt.tipo))
            self.tab_aditivos.setItem(row, 1, item_centro("Sim" if adt.renovacao_valor else "Não"))
            data_ini = adt.data_inicio_vigencia if adt.renovacao_valor else "-"
            self.tab_aditivos.setItem(row, 2, item_centro(data_ini))
            data_fim = adt.data_nova if adt.tipo == "Prazo" else "-"
            self.tab_aditivos.setItem(row, 3, item_centro(data_fim))
            val_txt = fmt_br(adt.valor) if (adt.tipo == "Valor" or adt.renovacao_valor) else "-"
            self.tab_aditivos.setItem(row, 4, item_centro(val_txt))
            self.tab_aditivos.setItem(row, 5, item_centro(adt.descricao))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = SistemaGestao()
    win.show()
    sys.exit(app.exec())