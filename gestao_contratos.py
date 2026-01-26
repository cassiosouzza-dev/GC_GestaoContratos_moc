import manual_texto
import sinc
import google.generativeai as genai
CHAVE_API_GEMINI = "AIzaSyDnCiICf2GXebAYzXxW044-8BSm7r2g3QI"
import sys
import csv
import json
import os
import ctypes
from ctypes import wintypes
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QTableWidget, QTableWidgetItem, QMessageBox,
                             QHeaderView, QListWidget, QSplitter,
                             QDialog, QComboBox, QFormLayout, QDialogButtonBox,
                             QAbstractItemView, QDateEdit, QTabWidget, QMenu,
                             QCheckBox, QStackedWidget, QFrame, QFileDialog, QInputDialog,
                             QSpinBox, QTextEdit, QListWidgetItem, QColorDialog, QSlider, QGroupBox) 
from PyQt6.QtCore import Qt, QDate, QEvent, QTimer
from PyQt6.QtGui import QAction, QColor, QFont, QPalette, QIcon, QPixmap



# --- FUNÇÃO GLOBAL PARA ESTILIZAR JANELAS (CORRIGE O BUG DOS DIÁLOGOS) ---
# Substitua a função antiga por esta versão COMPLETA:
def aplicar_estilo_janela(window_instance):
    """
    Tenta forçar a barra escura usando códigos do Win10 (19 e 20) e Win11.
    Executa imediatamente e reforça após 100ms.
    """
    def _aplicar():
        try:
            hwnd = int(window_instance.winId())
            if hwnd <= 0: return
            
            # Tenta o código padrão (Win 10 2004+ / Win 11)
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            val_dark = ctypes.c_int(1)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(val_dark), ctypes.sizeof(val_dark)
            )
            
            # Tenta o código antigo (Win 10 builds antigas - 1903/1909)
            # Se um falhar, o outro pega.
            DWMWA_USE_IMMERSIVE_DARK_MODE_OLD = 19
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE_OLD, ctypes.byref(val_dark), ctypes.sizeof(val_dark)
            )

            # Tenta Cor Personalizada (Apenas Win 11, ignorado no 10)
            DWMWA_CAPTION_COLOR = 35
            cor_hex = "1e3b4d" 
            r, g, b = int(cor_hex[0:2], 16), int(cor_hex[2:4], 16), int(cor_hex[4:6], 16)
            color_ref = (b << 16) | (g << 8) | r
            val_color = ctypes.c_int(color_ref)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, DWMWA_CAPTION_COLOR, ctypes.byref(val_color), ctypes.sizeof(val_color)
            )

            # Força o redesenho da barra (Gatilho visual)
            ctypes.windll.user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, 0x0027)
            
        except Exception:
            pass

    # ESTRATÉGIA DUPLA:
    # 1. Tenta executar AGORA (se a janela já tiver ID)
    _aplicar()
    # 2. Agenda uma repetição para garantir (caso o Windows esteja lento)
    QTimer.singleShot(100, _aplicar)


# --- CLASSES BASE ---
# Classe base para diálogos
# Corrige o bug da barra de título clara
class BaseDialog(QDialog): 
    """Classe base que força a barra escura assim que a janela aparece na tela (showEvent)"""
    def showEvent(self, event):
        aplicar_estilo_janela(self)
        super().showEvent(event)

class DarkMessageBox(QMessageBox):
    """Substitui o QMessageBox para garantir o tema escuro na barra de título"""
    def showEvent(self, event):
        aplicar_estilo_janela(self)
        super().showEvent(event)

    @staticmethod
    def info(parent, titulo, texto, buttons=QMessageBox.StandardButton.Ok):
        box = DarkMessageBox(parent)
        box.setWindowTitle(titulo)
        box.setText(texto)
        box.setIcon(QMessageBox.Icon.Information)
        box.setStandardButtons(buttons)
        return box.exec()

    @staticmethod
    def warning(parent, titulo, texto, buttons=QMessageBox.StandardButton.Ok):
        box = DarkMessageBox(parent)
        box.setWindowTitle(titulo)
        box.setText(texto)
        box.setIcon(QMessageBox.Icon.Warning)
        box.setStandardButtons(buttons)
        return box.exec()

    @staticmethod
    def critical(parent, titulo, texto, buttons=QMessageBox.StandardButton.Ok):
        box = DarkMessageBox(parent)
        box.setWindowTitle(titulo)
        box.setText(texto)
        box.setIcon(QMessageBox.Icon.Critical)
        box.setStandardButtons(buttons)
        return box.exec()
        
    @staticmethod
    def question(parent, titulo, texto, buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No):
        box = DarkMessageBox(parent)
        box.setWindowTitle(titulo)
        box.setText(texto)
        box.setIcon(QMessageBox.Icon.Question)
        box.setStandardButtons(buttons)
        return box.exec()


def fmt_br(valor):
    """Formata float para BRL: 1234.50 vira R$ 1.234,50"""
    if valor is None: return "R$ 0,00"
    texto = f"{valor:,.2f}"
    texto_formatado = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto_formatado}"

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
    def __init__(self, tipo, valor, competencia="", observacao=""):
        self.tipo = tipo
        self.valor = valor
        self.competencia = competencia
        self.observacao = observacao # Novo campo

    def to_dict(self): return self.__dict__

    @staticmethod
    def from_dict(d): 
        # Garante compatibilidade com versões anteriores (get 'observacao')
        return Movimentacao(d['tipo'], d['valor'], d['competencia'], d.get('observacao', ''))

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
        
        # Não vamos mais confiar na variável 'valor_pago' persistida, 
        # vamos calcular sempre baseados no histórico para evitar erros.
        self.valor_pago_cache = 0.0 
        
        self.historico = []
        self.historico.append(Movimentacao("Emissão Original", valor, "-"))

    @property
    def total_pago(self):
        """Soma apenas os Pagamentos reais"""
        return sum(m.valor for m in self.historico if m.tipo == "Pagamento")

    @property
    def total_anulado(self):
        """Soma apenas as Anulações (sempre positivo aqui para cálculo)"""
        # Nota: no histórico salvamos negativo, então usamos abs()
        return sum(abs(m.valor) for m in self.historico if m.tipo == "Anulação")

    @property
    def saldo_disponivel(self):
        """Saldo = Valor Inicial - Anulações - Pagamentos"""
        return self.valor_inicial - self.total_anulado - self.total_pago
    
    # Mantemos essa propriedade para compatibilidade com códigos antigos que chamam .valor_pago
    @property
    def valor_pago(self):
        return self.total_pago
    @valor_pago.setter
    def valor_pago(self, val):
        self.valor_pago_cache = val # Dummy setter

    def realizar_pagamento(self, valor, competencia, obs=""):
        if valor > self.saldo_disponivel + 0.01: 
            return False, f"Saldo insuficiente! Resta: {fmt_br(self.saldo_disponivel)}"
        
        self.historico.append(Movimentacao("Pagamento", valor, competencia, obs))
        return True, "Pagamento realizado."

    def realizar_anulacao(self, valor, justificativa=""):
        # Agora a anulação consome o SALDO, não o PAGO.
        if valor > self.saldo_disponivel + 0.01:
             return False, f"Impossível anular R$ {fmt_br(valor)}. Saldo disponível na nota é apenas R$ {fmt_br(self.saldo_disponivel)}."

        # Salvamos negativo para indicar redução no histórico visual
        self.historico.append(Movimentacao("Anulação", -valor, "-", justificativa))
        return True, "Anulação registrada (Saldo reduzido)."

    def excluir_movimentacao(self, index):
        if index < 0 or index >= len(self.historico): return False
        mov = self.historico[index]
        if mov.tipo == "Emissão Original": return False
        
        # Apenas removemos do histórico, as properties recalculam tudo sozinhas
        self.historico.pop(index)
        return True

    def editar_movimentacao(self, index, novo_valor, nova_comp, nova_obs=""):
        mov = self.historico[index]
        old_valor = mov.valor
        
        # Simula a remoção para testar saldo
        mov.valor = 0 
        
        if mov.tipo == "Pagamento":
            if novo_valor > self.saldo_disponivel + 0.01:
                mov.valor = old_valor # Restaura
                return False, "Novo valor excede o saldo disponível."
            mov.valor = novo_valor
            
        elif mov.tipo == "Anulação":
            novo_valor_neg = -abs(novo_valor)
            # Verifica se dá para anular esse valor
            # O saldo aumentou temporariamente porque zeramos o mov.valor acima
            if abs(novo_valor) > self.saldo_disponivel + 0.01:
                mov.valor = old_valor
                return False, "Novo valor de anulação excede o saldo disponível."
            mov.valor = novo_valor_neg

        mov.competencia = nova_comp
        mov.observacao = nova_obs
        return True, "Sucesso"

    def calcular_media_mensal(self):
        pagamentos = [m for m in self.historico if m.tipo == "Pagamento"]
        if not pagamentos: return 0.0
        soma_bruta = sum(m.valor for m in pagamentos)
        meses = set(m.competencia for m in pagamentos if m.competencia and m.competencia != "-")
        return soma_bruta / len(meses) if len(meses) > 0 else 0.0

    def to_dict(self):
        d = self.__dict__.copy()
        # Removemos cache do dict salvo
        if 'valor_pago_cache' in d: del d['valor_pago_cache']
        d['valor_pago'] = self.total_pago # Salva para compatibilidade
        d['historico'] = [h.to_dict() for h in self.historico]
        return d

    @staticmethod
    def from_dict(d):
        ne = NotaEmpenho(d['numero'], d['valor_inicial'], d['descricao'], d['subcontrato_idx'],
                         d['fonte_recurso'], d['data_emissao'], d.get('ciclo_id', 0), d.get('aditivo_vinculado_id'))
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
    def __init__(self, descricao, valor_mensal=0.0):
        self.descricao = descricao
        self.valor_mensal = valor_mensal
        self.valores_por_ciclo = {} # Começa vazio, sem vincular a nenhum ciclo

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
        v_mensal = d.get('valor_mensal', 0.0)
        sub = SubContrato(d['descricao'], v_mensal)
        if 'valores_por_ciclo' in d:
            sub.valores_por_ciclo = {int(k): v for k, v in d['valores_por_ciclo'].items()}
        # Compatibilidade com versões antigas que usavam valor_estimado solto
        elif 'valor_estimado' in d:
             sub.valores_por_ciclo[0] = d['valor_estimado']
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
                 licitacao, dispensa, ultima_modificacao=None):
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
        
        self.ultimo_ciclo_id = 0

        # Se não tiver data (novo), usa AGORA.
        self.ultima_modificacao = ultima_modificacao if ultima_modificacao else datetime.now().isoformat()

        self.ciclos = []
        self.ciclos.append(CicloFinanceiro(0, "Contrato Inicial", valor_inicial))
        self.lista_notas_empenho = []
        self.lista_aditivos = []
        self.lista_servicos = []
        self._contador_aditivos = 0

    # 2. Método para atualizar a data de edição
    def marcar_alteracao(self):
        self.ultima_modificacao = datetime.now().isoformat()

    def get_vigencia_final_atual(self):
        aditivos_prazo = [a for a in self.lista_aditivos if a.tipo == "Prazo"]
        if aditivos_prazo: return aditivos_prazo[-1].data_nova
        return self.vigencia_fim

        
    def adicionar_aditivo(self, adt, id_ciclo_alvo=None):
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
            # CORREÇÃO: Usa o ciclo alvo escolhido ou o último válido
            ciclo_atual = None

            if id_ciclo_alvo is not None:
                # Tenta achar o ciclo que o usuário estava vendo
                ciclo_atual = next((c for c in self.ciclos if c.id_ciclo == id_ciclo_alvo), None)

            # Se não achou ou não foi passado, pega o último não cancelado
            if not ciclo_atual:
                ciclo_atual = next((c for c in reversed(self.ciclos) if "(CANCELADO)" not in c.nome),
                                   self.ciclos[0])

            ciclo_atual.aditivos_valor.append(adt)
            adt.ciclo_pertencente_id = ciclo_atual.id_ciclo
            adt.descricao = f"{qtd_valores}º TA Valor - " + adt.descricao

            if adt.servico_idx >= 0 and adt.servico_idx < len(self.lista_servicos):
                serv = self.lista_servicos[adt.servico_idx]
                valor_atual = serv.get_valor_ciclo(ciclo_atual.id_ciclo)
                serv.set_valor_ciclo(ciclo_atual.id_ciclo, valor_atual + adt.valor)
                return f"Valor somado ao serviço '{serv.descricao}' no ciclo '{ciclo_atual.nome}'."

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
        # 3. Lê a data do JSON
        c = Contrato(
            d['numero'], d['prestador'], d['descricao'], d['valor_inicial'], d['vigencia_inicio'],
            d['vigencia_fim'], d['comp_inicio'], d['comp_fim'], d.get('licitacao', ''), d.get('dispensa', ''),
            d.get('ultima_modificacao') # <--- Carrega data
        )
        c.ultimo_ciclo_id = d.get('ultimo_ciclo_id', 0)
        c.ciclos = [CicloFinanceiro.from_dict(cd) for cd in d['ciclos']]
        c.lista_servicos = [SubContrato.from_dict(sd) for sd in d['lista_servicos']]
        c.lista_aditivos = [Aditivo.from_dict(ad) for ad in d['lista_aditivos']]
        c.lista_notas_empenho = [NotaEmpenho.from_dict(nd) for nd in d['lista_notas_empenho']]
        c._contador_aditivos = d.get('_contador_aditivos', 0)
        
        for adt in c.lista_aditivos:
            if adt.tipo == "Valor" and adt.ciclo_pertencente_id != -1:
                for ciclo in c.ciclos:
                    if ciclo.id_ciclo == adt.ciclo_pertencente_id:
                        ciclo.aditivos_valor.append(adt); break
        return c

class Prestador:
    def __init__(self, razao_social, nome_fantasia, cnpj, cnes, cod_cp):
        self.razao_social = razao_social
        self.nome_fantasia = nome_fantasia
        self.cnpj = cnpj
        self.cnes = cnes
        self.cod_cp = cod_cp

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(d):
        return Prestador(d['razao_social'], d['nome_fantasia'], d['cnpj'], d.get('cnes', ''), d.get('cod_cp', ''))

# --- 2. DIÁLOGOS ---

class DialogoAjuda(BaseDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manual do Sistema - GC Gestor")
        self.resize(850, 650) # Aumentei um pouco para caber o texto novo

        layout = QVBoxLayout(self)

        texto_ajuda = QTextEdit()
        texto_ajuda.setReadOnly(True)

        # --- MUDANÇA AQUI ---
        # Agora pegamos o texto do arquivo separado
        texto_ajuda.setHtml(manual_texto.HTML_MANUAL) 
        # --------------------

        layout.addWidget(texto_ajuda)

        btn_fechar = QPushButton("Fechar")
        btn_fechar.clicked.connect(self.accept)
        layout.addWidget(btn_fechar)

class DialogoCriarContrato(BaseDialog):
    # ATENÇÃO: Adicionado 'lista_prestadores' nos argumentos
    def __init__(self, lista_prestadores, contrato_editar=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cadastro de Contrato")
        self.resize(700, 600)
        layout = QFormLayout(self)
        
        self.inp_numero = QLineEdit();
        
        # --- MUDANÇA: AGORA É UM COMBOBOX ---
        self.combo_prestador = QComboBox()
        self.combo_prestador.setEditable(False) # Obriga a escolher da lista
        
        # Popula o Combobox
        for p in lista_prestadores:
            # Exibe: Nome Fantasia (Razão Social) - CNPJ
            texto = f"{p.nome_fantasia} ({p.razao_social})"
            # Salva o Nome Fantasia como dado principal (para compatibilidade com sistema antigo)
            self.combo_prestador.addItem(texto, p.nome_fantasia)
            
        if self.combo_prestador.count() == 0:
            self.combo_prestador.addItem("Nenhum prestador cadastrado (Cadastre no menu Prestadores)", "")
        # ------------------------------------

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
        layout.addRow("Prestador (Vinculado):", self.combo_prestador) # Mudou aqui
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
            
            # Tenta selecionar o prestador antigo na lista
            index = self.combo_prestador.findData(contrato_editar.prestador)
            if index >= 0:
                self.combo_prestador.setCurrentIndex(index)
            else:
                # Se for um contrato antigo com prestador que não tá na lista, adiciona temporariamente
                self.combo_prestador.addItem(f"{contrato_editar.prestador} (Não cadastrado)", contrato_editar.prestador)
                self.combo_prestador.setCurrentIndex(self.combo_prestador.count()-1)

            self.inp_desc.setText(contrato_editar.descricao);
            self.inp_valor.set_value(contrato_editar.valor_inicial);
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

    def get_dados(self): 
        # Retorna o .currentData() que é o Nome Fantasia limpo
        prestador_escolhido = self.combo_prestador.currentData()
        if not prestador_escolhido: prestador_escolhido = "Desconhecido"
        
        return (self.inp_numero.text(), prestador_escolhido, self.inp_desc.text(),
                self.inp_valor.get_value(), self.date_vig_ini.text(), self.date_vig_fim.text(),
                self.inp_comp_ini.text(), self.inp_comp_fim.text(), self.inp_licitacao.text(),
                self.inp_dispensa.text())

class DialogoNovoEmpenho(BaseDialog):
    def __init__(self, contrato, ne_editar=None, parent=None):
        super().__init__(parent);
        self.contrato = contrato;
        self.setWindowTitle("Nota de Empenho");
        self.resize(600, 450)
        layout = QFormLayout(self)
        self.inp_num = QLineEdit();
        self.inp_desc = QLineEdit();
        self.inp_fonte = QLineEdit();
        self.date_emissao = QDateEdit(QDate.currentDate());
        self.date_emissao.setCalendarPopup(True);
        self.inp_val = CurrencyInput()

        self.combo_ciclo = QComboBox()
        # VITAL: Conecta a mudança de ciclo à atualização dos valores dos serviços
        self.combo_ciclo.currentIndexChanged.connect(self.ao_mudar_ciclo)

        self.combo_aditivo = QComboBox()
        self.combo_sub = QComboBox()

        for c in contrato.ciclos:
            saldo = contrato.get_saldo_ciclo_geral(c.id_ciclo)
            if ne_editar and ne_editar.ciclo_id == c.id_ciclo: saldo += ne_editar.valor_inicial
            self.combo_ciclo.addItem(f"{c.nome} (Livre: R$ {fmt_br(saldo)})", c.id_ciclo)

        layout.addRow("1. Ciclo Financeiro:", self.combo_ciclo);
        layout.addRow("2. Vincular a Aditivo de Valor (Opcional):", self.combo_aditivo)
        layout.addRow("Número da Nota:", self.inp_num);
        layout.addRow("Data de Emissão:", self.date_emissao);
        layout.addRow("Fonte de Recurso:", self.inp_fonte)
        layout.addRow("Descrição:", self.inp_desc);
        layout.addRow("Vincular a Serviço:", self.combo_sub);
        layout.addRow("Valor:", self.inp_val)

        if ne_editar:
            self.inp_num.setText(ne_editar.numero);
            self.inp_desc.setText(ne_editar.descricao);
            self.inp_fonte.setText(ne_editar.fonte_recurso)
            self.date_emissao.setDate(str_to_date(ne_editar.data_emissao));
            self.inp_val.set_value(ne_editar.valor_inicial)

            idx_c = self.combo_ciclo.findData(ne_editar.ciclo_id);
            if idx_c >= 0: self.combo_ciclo.setCurrentIndex(idx_c)

            # Força atualização para carregar valores corretos do serviço na edição
            self.ao_mudar_ciclo()

            if ne_editar.aditivo_vinculado_id:
                idx_a = self.combo_aditivo.findData(ne_editar.aditivo_vinculado_id)
                if idx_a >= 0: self.combo_aditivo.setCurrentIndex(idx_a)
            if ne_editar.subcontrato_idx < self.combo_sub.count(): self.combo_sub.setCurrentIndex(
                ne_editar.subcontrato_idx)
            if len(ne_editar.historico) > 1: self.inp_val.setEnabled(False)
        else:
            self.combo_ciclo.setCurrentIndex(self.combo_ciclo.count() - 1)
            self.ao_mudar_ciclo()  # Atualiza ao abrir

        botoes = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        botoes.accepted.connect(self.accept)
        botoes.rejected.connect(self.reject)
        layout.addWidget(botoes)
        
    def ao_mudar_ciclo(self):
        self.atualizar_combo_aditivos()
        self.atualizar_combo_servicos()

    def atualizar_combo_servicos(self):
        id_ciclo_atual = self.combo_ciclo.currentData()
        if id_ciclo_atual is None: return

        idx_atual = self.combo_sub.currentIndex()
        self.combo_sub.clear()

        # Pega o valor do serviço NO CICLO SELECIONADO na combobox
        for i, sub in enumerate(self.contrato.lista_servicos):
            val_atual = sub.get_valor_ciclo(id_ciclo_atual)
            self.combo_sub.addItem(f"{sub.descricao} (Orç. Ciclo: {fmt_br(val_atual)})", i)

        if idx_atual >= 0 and idx_atual < self.combo_sub.count():
            self.combo_sub.setCurrentIndex(idx_atual)

    def atualizar_combo_aditivos(self):
        self.combo_aditivo.clear();
        self.combo_aditivo.addItem("--- Usar Saldo Geral do Ciclo ---", None)
        id_ciclo_atual = self.combo_ciclo.currentData();
        if id_ciclo_atual is None: return
        ciclo_obj = next((c for c in self.contrato.ciclos if c.id_ciclo == id_ciclo_atual), None)
        if ciclo_obj:
            for adt in ciclo_obj.aditivos_valor:
                saldo = self.contrato.get_saldo_aditivo_especifico(adt.id_aditivo)
                self.combo_aditivo.addItem(f"{adt.descricao} (Resta: R$ {fmt_br(saldo)})", adt.id_aditivo)

    def get_dados(self):
        return (self.inp_num.text(), self.inp_desc.text(), self.combo_sub.currentIndex(), self.inp_val.get_value(),
                self.inp_fonte.text(), self.date_emissao.text(), self.combo_ciclo.currentData(),
                self.combo_aditivo.currentData())


class DialogoAditivo(BaseDialog):
    def __init__(self, contrato, aditivo_editar=None, parent=None):
        super().__init__(parent); self.contrato = contrato 
        self.setWindowTitle("Aditivo Contratual"); 
        self.resize(550, 500)
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

class DialogoPagamento(BaseDialog):
    # Adicionado parametro 'titulo' e 'label_valor'
    def __init__(self, comp_inicio, comp_fim, pg_editar=None, titulo="Realizar Pagamento", label_valor="Valor:", parent=None):
        super().__init__(parent);
        self.setWindowTitle(titulo); # Usa o título dinâmico
        self.resize(400, 500)
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("Competência(s) Referente(s):"))
        self.lista_comp = QListWidget()
        meses = gerar_competencias(comp_inicio, comp_fim)
        if not meses: meses = ["Erro datas contrato"]
        
        competencias_selecionadas = []
        if pg_editar:
            competencias_selecionadas = [c.strip() for c in pg_editar.competencia.split(',')]

        for m in meses:
            item = QListWidgetItem(m)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            if pg_editar and m in competencias_selecionadas:
                item.setCheckState(Qt.CheckState.Checked)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)
            self.lista_comp.addItem(item)
            
        layout.addWidget(self.lista_comp)
        
        # Usa o label dinâmico
        layout.addWidget(QLabel(label_valor))
        self.inp_valor = CurrencyInput()
        layout.addWidget(self.inp_valor)
        
        layout.addWidget(QLabel("Justificativa / Observação:")) # Texto genérico
        self.inp_obs = QLineEdit()
        self.inp_obs.setPlaceholderText("Descreva o motivo...")
        layout.addWidget(self.inp_obs)

        if pg_editar:
            # Se for edição, usamos o valor absoluto (sem sinal negativo) para editar
            val_abs = abs(pg_editar.valor)
            self.inp_valor.set_value(val_abs)
            self.inp_obs.setText(pg_editar.observacao)
        else:
            if self.lista_comp.count() > 0:
                 self.lista_comp.item(0).setCheckState(Qt.CheckState.Checked)

        botoes = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel);
        botoes.accepted.connect(self.accept)
        botoes.rejected.connect(self.reject)
        layout.addWidget(botoes)

    def get_dados(self):
        selecionados = []
        for i in range(self.lista_comp.count()):
            item = self.lista_comp.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selecionados.append(item.text())
        
        comp_str = ", ".join(selecionados) if selecionados else "Nenhuma"
        return comp_str, self.inp_valor.get_value(), self.inp_obs.text()

class DialogoAnulacao(BaseDialog):
    """Diálogo simplificado para anulação: Apenas Valor e Justificativa"""
    def __init__(self, editar_valor=None, editar_obs=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Anular / Estornar Empenho")
        self.resize(350, 200)
        
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("Valor a Anular/Estornar:"))
        self.inp_valor = CurrencyInput()
        layout.addWidget(self.inp_valor)
        
        layout.addWidget(QLabel("Justificativa:"))
        self.inp_obs = QLineEdit()
        self.inp_obs.setPlaceholderText("Motivo da anulação...")
        layout.addWidget(self.inp_obs)

        # Se for edição, preenche os dados
        if editar_valor is not None:
            self.inp_valor.set_value(abs(editar_valor)) # Usa valor positivo visualmente
        if editar_obs is not None:
            self.inp_obs.setText(editar_obs)
        
        layout.addSpacing(10)
        
        lbl_info = QLabel("ℹ A anulação abate o 'Valor Pago' e devolve o saldo para a Nota de Empenho.\nNão altera a média mensal do serviço.")
        lbl_info.setWordWrap(True)
        lbl_info.setStyleSheet("color: #555; font-size: 11px; font-style: italic;")
        layout.addWidget(lbl_info)

        botoes = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        botoes.accepted.connect(self.accept)
        botoes.rejected.connect(self.reject)
        layout.addWidget(botoes)

    def get_dados(self):
        return self.inp_valor.get_value(), self.inp_obs.text()

class DialogoSubContrato(BaseDialog):
    def __init__(self, lista_ciclos, ciclo_atual_id=0, sub_editar=None, valor_editar=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Serviço / Subcontrato")
        self.resize(500, 400)
        layout = QFormLayout(self)

        self.inp_desc = QLineEdit()
        self.inp_mensal = CurrencyInput()
        self.inp_valor = CurrencyInput()

        # Seletor de Ciclo
        self.combo_ciclo_alvo = QComboBox()
        for id_c, nome_c in lista_ciclos:
            self.combo_ciclo_alvo.addItem(nome_c, id_c)

        # Seleciona o ciclo atual por padrão
        idx = self.combo_ciclo_alvo.findData(ciclo_atual_id)
        if idx >= 0: self.combo_ciclo_alvo.setCurrentIndex(idx)

        # Checkbox
        self.chk_todos = QCheckBox("Ignorar escolha acima e replicar para TODOS?")
        self.chk_todos.setChecked(False)

        layout.addRow("Descrição:", self.inp_desc)
        layout.addRow("Vincular ao Ciclo:", self.combo_ciclo_alvo)
        layout.addRow("Valor Mensal:", self.inp_mensal)
        layout.addRow("Valor Total:", self.inp_valor)
        layout.addRow("", self.chk_todos)

        if sub_editar:
            self.inp_desc.setText(sub_editar.descricao)
            self.inp_mensal.set_value(sub_editar.valor_mensal)
            if valor_editar is not None:
                self.inp_valor.set_value(valor_editar)
            else:
                self.inp_valor.set_value(sub_editar.get_valor_ciclo(0))

            # Na edição, travamos o ciclo para evitar confusão
            self.combo_ciclo_alvo.setEnabled(False)
            self.chk_todos.setText("Aplicar este novo valor a TODOS os ciclos?")

        botoes = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        botoes.accepted.connect(self.accept)
        botoes.rejected.connect(self.reject)
        layout.addWidget(botoes)
        
    def get_dados(self):
        return (self.inp_desc.text(),
                self.inp_valor.get_value(),
                self.inp_mensal.get_value(),
                self.chk_todos.isChecked(),
                self.combo_ciclo_alvo.currentData())



class DialogoDetalheServico(BaseDialog):
    def __init__(self, servico, lista_nes_do_servico, data_inicio, data_fim, ciclo_id=0, parent=None):
        super().__init__(parent)
    
        # --- GUARDA AS REFERÊNCIAS PARA A IA USAR DEPOIS ---
        self.servico_ref = servico
        self.lista_nes_ref = lista_nes_do_servico
        self.ciclo_ref = ciclo_id 
        # ---------------------------------------------------

        self.setWindowTitle(f"Detalhamento: {servico.descricao}")
        self.resize(1200, 700)
        self.showMaximized() 
        
        layout = QVBoxLayout(self)
        self.abas = QTabWidget()
        layout.addWidget(self.abas)

        # ABA 1: EVOLUÇÃO MENSAL
        tab_mensal = QWidget()
        l_mensal = QVBoxLayout(tab_mensal)
        
        mapa_pagamentos = {}
        meses = gerar_competencias(data_inicio, data_fim)
        total_meses_count = len(meses)
        valor_total_orcamento = servico.valor_mensal * total_meses_count
        
        for m in meses:
             mapa_pagamentos[m] = {'pago': 0.0, 'detalhes_texto': [], 'tem_obs': False}

        for ne in lista_nes_do_servico:
            for mov in ne.historico:
                if mov.tipo == "Pagamento":
                    comps = [c.strip() for c in mov.competencia.split(',') if c.strip()]
                    qtd = len(comps)
                    if qtd == 0: continue
                    valor_parcela = mov.valor / qtd 
                    obs_str = f" | Obs: {mov.observacao}" if mov.observacao else ""
                    texto_info = f"• NE {ne.numero}: {fmt_br(mov.valor)} (Ref. {qtd} meses){obs_str}"

                    for c in comps:
                        if c in mapa_pagamentos:
                            mapa_pagamentos[c]['pago'] += valor_parcela
                            mapa_pagamentos[c]['detalhes_texto'].append(texto_info)
                            if qtd > 1 or mov.observacao:
                                mapa_pagamentos[c]['tem_obs'] = True

        self.tabela_mensal = TabelaExcel()
        colunas = ["Competência", "Det.", "Valor Mensal", "Valor Pago", "Saldo Mês", "% Mês", "Saldo Global", "% Acum."]
        self.tabela_mensal.setColumnCount(len(colunas))
        self.tabela_mensal.setHorizontalHeaderLabels(colunas)
        
        header = self.tabela_mensal.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed); self.tabela_mensal.setColumnWidth(1, 50)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)
        
        self.tabela_mensal.cellClicked.connect(self.mostrar_detalhes_clique)

        self.tabela_mensal.setRowCount(0)
        
        # Variáveis acumuladoras
        total_previsto = 0
        total_pago = 0
        acumulado_pago_ate_agora = 0
        total_saldo_mensal_acumulado = 0 # <--- ACUMULADOR NOVO

        def item_centro(texto, cor=None, bg=None):
            it = QTableWidgetItem(str(texto))
            it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if cor: it.setForeground(QColor(cor))
            if bg: it.setBackground(QColor(bg))
            return it

        for mes in meses:
            dados = mapa_pagamentos[mes]
            valor_mensal = servico.valor_mensal
            valor_pago = dados['pago']
            
            # Cálculo do Mês
            saldo_mes = valor_mensal - valor_pago
            percentual_mes = (valor_pago / valor_mensal * 100) if valor_mensal > 0 else 0
            
            # Acumulando Totais
            total_previsto += valor_mensal
            total_pago += valor_pago
            acumulado_pago_ate_agora += valor_pago
            total_saldo_mensal_acumulado += saldo_mes # <--- SOMA LINHA A LINHA
            
            # Cálculo Global
            saldo_global = valor_total_orcamento - acumulado_pago_ate_agora
            perc_acumulada = (acumulado_pago_ate_agora / valor_total_orcamento * 100) if valor_total_orcamento > 0 else 0

            row = self.tabela_mensal.rowCount()
            self.tabela_mensal.insertRow(row)
            
            self.tabela_mensal.setItem(row, 0, item_centro(mes, bg=None))
            
            # Ícone de detalhes
            item_link = item_centro("")
            if dados['tem_obs']:
                item_link.setText("🔗") 
                item_link.setForeground(QColor("blue"))
                texto_completo = "Detalhes do Pagamento:\n\n" + "\n".join(dados['detalhes_texto'])
                item_link.setToolTip(texto_completo)
                item_link.setData(Qt.ItemDataRole.UserRole, texto_completo)
            self.tabela_mensal.setItem(row, 1, item_link)

            # --- EXIBIÇÃO ---
            if valor_pago > 0:
                self.tabela_mensal.setItem(row, 2, item_centro(fmt_br(valor_mensal)))
                self.tabela_mensal.setItem(row, 3, item_centro(fmt_br(valor_pago), cor="#27ae60"))
                
                cor_saldo = "red" if saldo_mes < -0.01 else None
                self.tabela_mensal.setItem(row, 4, item_centro(fmt_br(saldo_mes), cor=cor_saldo))
                
                bg_perc = "#16A856" if percentual_mes >= 100 else None
                self.tabela_mensal.setItem(row, 5, item_centro(f"{percentual_mes:.1f}%", bg=bg_perc))
            else:
                self.tabela_mensal.setItem(row, 2, item_centro("-"))
                self.tabela_mensal.setItem(row, 3, item_centro("-"))
                self.tabela_mensal.setItem(row, 4, item_centro("-"))
                self.tabela_mensal.setItem(row, 5, item_centro("-"))

            self.tabela_mensal.setItem(row, 6, item_centro(fmt_br(saldo_global)))
            self.tabela_mensal.setItem(row, 7, item_centro(f"{perc_acumulada:.1f}%"))

        # --- LINHA DE TOTAL ---
        row = self.tabela_mensal.rowCount()
        self.tabela_mensal.insertRow(row)
        font_bold = QFont(); font_bold.setBold(True)
        
        i_tot = item_centro("TOTAL"); i_tot.setFont(font_bold)
        self.tabela_mensal.setItem(row, 0, i_tot)
        
        i_v_tot = item_centro(fmt_br(total_previsto)); i_v_tot.setFont(font_bold)
        self.tabela_mensal.setItem(row, 2, i_v_tot)
        
        i_p_tot = item_centro(fmt_br(total_pago)); i_p_tot.setFont(font_bold)
        self.tabela_mensal.setItem(row, 3, i_p_tot)

        # --- TOTAL DO SALDO MENSAL (SOMATÓRIO EXATO) ---
        i_s_tot = item_centro(fmt_br(total_saldo_mensal_acumulado)); i_s_tot.setFont(font_bold)
        if total_saldo_mensal_acumulado < 0: i_s_tot.setForeground(QColor("red"))
        self.tabela_mensal.setItem(row, 4, i_s_tot)
        # -----------------------------------------------
        
        l_mensal.addWidget(self.tabela_mensal)
        self.abas.addTab(tab_mensal, "Evolução Mensal")

        # ABA 2: LISTA DE NEs
        tab_nes = QWidget()
        l_nes = QVBoxLayout(tab_nes)
        self.tabela_nes = TabelaExcel()
        self.tabela_nes.setColumnCount(6)
        self.tabela_nes.setHorizontalHeaderLabels(["Número NE", "Emissão", "Descrição", "Valor Original", "Total Pago", "Saldo Atual"])
        self.tabela_nes.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabela_nes.setRowCount(0)
        for ne in lista_nes_do_servico:
            r = self.tabela_nes.rowCount()
            self.tabela_nes.insertRow(r)
            pago = sum(m.valor for m in ne.historico if m.tipo == "Pagamento")
            anulado = sum(abs(m.valor) for m in ne.historico if m.tipo == "Anulação")
            saldo = ne.valor_inicial - anulado - pago
            self.tabela_nes.setItem(r, 0, item_centro(ne.numero))
            self.tabela_nes.setItem(r, 1, item_centro(ne.data_emissao))
            self.tabela_nes.setItem(r, 2, item_centro(ne.descricao))
            self.tabela_nes.setItem(r, 3, item_centro(fmt_br(ne.valor_inicial)))
            self.tabela_nes.setItem(r, 4, item_centro(fmt_br(pago), cor="#27ae60"))
            self.tabela_nes.setItem(r, 5, item_centro(fmt_br(saldo)))
        l_nes.addWidget(self.tabela_nes)
        self.abas.addTab(tab_nes, "Por Nota de Empenho (NE)")

        # BOTÕES
        btns = QHBoxLayout()

        btn_ia = QPushButton("🤖 Analisar Este Serviço")
        btn_ia.setStyleSheet("background-color: #8e44ad; color: white; font-weight: bold; padding: 8px 15px;")
        btn_ia.clicked.connect(self.chamar_analise_ia)
        btns.addWidget(btn_ia)

        btn_copiar = QPushButton("Copiar Tabela Atual")
        btn_copiar.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 8px 15px;")
        btn_copiar.clicked.connect(self.copiar_tabela_ativa)
        btn_fechar = QPushButton("Fechar")
        btn_fechar.setStyleSheet("padding: 8px 15px;")
        btn_fechar.clicked.connect(self.accept)
        btns.addWidget(btn_copiar)
        btns.addStretch()
        btns.addWidget(btn_fechar)
        layout.addLayout(btns)
        aplicar_estilo_janela(self)

    def chamar_analise_ia(self):
        try:
            main_window = self.parent()
            if not hasattr(main_window, 'ia'): return

            DarkMessageBox.info(self, "IA Trabalhando", "Analisando o ritmo de execução deste serviço...")
            
            parecer = main_window.ia.analisar_servico_especifico(
                self.servico_ref,
                self.lista_nes_ref,
                self.ciclo_ref 
            )
            
            dial = BaseDialog(self)
            dial.setWindowTitle("Análise do Serviço")
            dial.resize(600, 400)
            l = QVBoxLayout(dial)
            t = QTextEdit(); t.setMarkdown(parecer); t.setReadOnly(True)
            l.addWidget(t)
            dial.exec()
            
        except Exception as e:
            DarkMessageBox.critical(self, "Erro", str(e))

    def mostrar_detalhes_clique(self, row, col):
        item = self.tabela_mensal.item(row, col)
        if item and item.text() == "🔗":
            texto = item.data(Qt.ItemDataRole.UserRole)
            if texto: DarkMessageBox.info(self, "Detalhes", texto)

    def copiar_tabela_ativa(self):
        idx = self.abas.currentIndex()
        if idx == 0:
            self.tabela_mensal.selectAll()
            self.tabela_mensal.copiar_selecao()
            self.tabela_mensal.clearSelection()
        else:
            self.tabela_nes.selectAll()
            self.tabela_nes.copiar_selecao()
            self.tabela_nes.clearSelection()
        DarkMessageBox.info(self, "Sucesso", "Tabela da aba atual copiada!")

class DialogoCadastroPrestador(BaseDialog):
    def __init__(self, prestador_editar=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cadastro de Prestador")
        self.resize(500, 300)
        layout = QFormLayout(self)

        self.inp_razao = QLineEdit()
        self.inp_fantasia = QLineEdit()
        self.inp_cnpj = QLineEdit()
        self.inp_cnpj.setInputMask("99.999.999/9999-99")
        self.inp_cnes = QLineEdit()
        self.inp_cod = QLineEdit()

        layout.addRow("Razão Social:", self.inp_razao)
        layout.addRow("Nome Fantasia:", self.inp_fantasia)
        layout.addRow("C.N.P.J.:", self.inp_cnpj)
        layout.addRow("CNES:", self.inp_cnes)
        layout.addRow("Cód. CP:", self.inp_cod)

        if prestador_editar:
            self.inp_razao.setText(prestador_editar.razao_social)
            self.inp_fantasia.setText(prestador_editar.nome_fantasia)
            self.inp_cnpj.setText(prestador_editar.cnpj)
            self.inp_cnes.setText(prestador_editar.cnes)
            self.inp_cod.setText(prestador_editar.cod_cp)

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def get_dados(self):
        return (self.inp_razao.text(), self.inp_fantasia.text(), self.inp_cnpj.text(), 
                self.inp_cnes.text(), self.inp_cod.text())


class DialogoGerenciarPrestadores(BaseDialog):
    def __init__(self, lista_prestadores, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Registro de Prestadores")
        self.resize(900, 600)
        
        # --- NOVO: HABILITA OS BOTÕES DE MAXIMIZAR E MINIMIZAR ---
        self.setWindowFlags(self.windowFlags() | 
                            Qt.WindowType.WindowMaximizeButtonHint | 
                            Qt.WindowType.WindowMinimizeButtonHint |
                            Qt.WindowType.WindowCloseButtonHint)
        # ---------------------------------------------------------

        self.lista_prestadores = lista_prestadores
        self.parent_window = parent 

        layout = QVBoxLayout(self)

        # Botões de Ação
        h_btns = QHBoxLayout()
        btn_novo = QPushButton("+ Novo Prestador")
        btn_novo.clicked.connect(self.novo_prestador)
        btn_novo.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 6px;")
        
        btn_editar = QPushButton("Editar Selecionado")
        btn_editar.clicked.connect(self.editar_prestador)
        
        btn_excluir = QPushButton("Excluir Selecionado")
        btn_excluir.clicked.connect(self.excluir_prestador)
        btn_excluir.setStyleSheet("color: #c0392b;")

        h_btns.addWidget(btn_novo)
        h_btns.addWidget(btn_editar)
        h_btns.addWidget(btn_excluir)
        h_btns.addStretch()
        layout.addLayout(h_btns)

        # Tabela
        self.tabela = TabelaExcel()
        colunas = ["Razão Social", "Nome Fantasia", "CNPJ", "CNES", "Cód. CP"]
        self.tabela.setColumnCount(len(colunas))
        self.tabela.setHorizontalHeaderLabels(colunas)
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tabela.cellDoubleClicked.connect(self.editar_prestador)
        
        # --- ATIVAR MENU DE CONTEXTO (Botão Direito) ---
        self.tabela.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tabela.customContextMenuRequested.connect(self.abrir_menu_contexto)
        # -----------------------------------------------

        # Ativa a ordenação (recurso que adicionamos antes)
        self.tabela.setSortingEnabled(True)
        
        layout.addWidget(self.tabela)
        self.atualizar_tabela()

        btn_fechar = QPushButton("Fechar")
        btn_fechar.clicked.connect(self.accept)
        layout.addWidget(btn_fechar)

        # Aplica o estilo escuro na janela (importante ao alterar flags)
        aplicar_estilo_janela(self)

    def atualizar_tabela(self):
        # Desliga ordenação para não embaralhar inserção
        self.tabela.setSortingEnabled(False)
        self.tabela.setRowCount(0)
        
        for p in self.lista_prestadores:
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            
            # Converte para string para ordenação funcionar bem
            self.tabela.setItem(row, 0, QTableWidgetItem(str(p.razao_social)))
            self.tabela.setItem(row, 1, QTableWidgetItem(str(p.nome_fantasia)))
            self.tabela.setItem(row, 2, QTableWidgetItem(str(p.cnpj)))
            self.tabela.setItem(row, 3, QTableWidgetItem(str(p.cnes)))
            self.tabela.setItem(row, 4, QTableWidgetItem(str(p.cod_cp)))
            
            self.tabela.item(row, 0).setData(Qt.ItemDataRole.UserRole, p)
            
        # Religa ordenação
        self.tabela.setSortingEnabled(True)

    def novo_prestador(self):
        dial = DialogoCadastroPrestador(parent=self)
        if dial.exec():
            dados = dial.get_dados()
            novo_p = Prestador(*dados)
            self.lista_prestadores.append(novo_p)
            self.atualizar_tabela()
            if self.parent_window: self.parent_window.salvar_dados()

    def abrir_menu_contexto(self, pos):
        # Descobre em qual linha foi o clique
        item = self.tabela.itemAt(pos)
        
        if item:
            # Garante que a linha clicada fique selecionada visualmente
            self.tabela.selectRow(item.row())
            
            menu = QMenu(self)
            
            acao_editar = menu.addAction("Editar Prestador")
            acao_editar.triggered.connect(self.editar_prestador)
            
            menu.addSeparator()
            
            acao_excluir = menu.addAction("Excluir Prestador")
            acao_excluir.triggered.connect(self.excluir_prestador)
            
            # Exibe o menu na posição do mouse
            menu.exec(self.tabela.mapToGlobal(pos))

    def editar_prestador(self):
        row = self.tabela.currentRow()
        if row < 0: return
        p = self.tabela.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        dial = DialogoCadastroPrestador(prestador_editar=p, parent=self)
        if dial.exec():
            # Atualiza objeto
            rs, nf, cj, cn, cd = dial.get_dados()
            p.razao_social = rs; p.nome_fantasia = nf; p.cnpj = cj; p.cnes = cn; p.cod_cp = cd
            self.atualizar_tabela()
            if self.parent_window: self.parent_window.salvar_dados()

    def excluir_prestador(self):
        row = self.tabela.currentRow()
        if row < 0: return
        p = self.tabela.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        if DarkMessageBox.question(self, "Excluir", f"Tem certeza que deseja excluir '{p.nome_fantasia}'?") == QMessageBox.StandardButton.Yes:
            self.lista_prestadores.remove(p)
            self.atualizar_tabela()
            if self.parent_window: self.parent_window.salvar_dados()

class PainelDetalheGlobal(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.lbl_titulo = QLabel("Visão Detalhada do Ciclo (Todos os Serviços)")
        self.lbl_titulo.setStyleSheet("font-size: 14px; font-weight: bold; color: #555;")
        layout.addWidget(self.lbl_titulo)
        
        self.tabela = TabelaExcel()
        colunas = ["Competência", "Det.", "Meta Mensal", "Executado", "Saldo Mês", "% Mês", "Saldo Global", "% Acum."]
        self.tabela.setColumnCount(len(colunas))
        self.tabela.setHorizontalHeaderLabels(colunas)
        
        header = self.tabela.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed); self.tabela.setColumnWidth(1, 50)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)
        
        self.tabela.cellClicked.connect(self.mostrar_detalhes_clique)
        layout.addWidget(self.tabela)
        
        btns = QHBoxLayout()
        btn_copiar = QPushButton("Copiar Tabela")
        btn_copiar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_copiar.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 8px 15px;")
        btn_copiar.clicked.connect(self.copiar_tabela)
        btns.addWidget(btn_copiar)
        btns.addStretch()
        layout.addLayout(btns)

    def carregar_dados(self, contrato, ciclo_ativo_id):
        self.tabela.setRowCount(0)
        if not contrato: return

        ciclo = next((c for c in contrato.ciclos if c.id_ciclo == ciclo_ativo_id), None)
        if not ciclo: return 
        
        c_ini = getattr(ciclo, 'inicio', None)
        c_fim = getattr(ciclo, 'fim', None)
        dt_ini = c_ini if c_ini else contrato.comp_inicio
        dt_fim = c_fim if c_fim else contrato.comp_fim
        
        meses = gerar_competencias(dt_ini, dt_fim)
        meta_mensal_global = sum([s.valor_mensal for s in contrato.lista_servicos])
        valor_total_contrato = meta_mensal_global * len(meses)
        mapa_pagos = {m: {'valor': 0.0, 'detalhes_texto': [], 'tem_obs': False} for m in meses}
        
        for ne in contrato.lista_notas_empenho:
            if ne.ciclo_id != ciclo.id_ciclo: continue
            for mov in ne.historico:
                if mov.tipo == "Pagamento":
                    comps = [c.strip() for c in mov.competencia.split(',') if c.strip()]
                    qtd = len(comps)
                    if qtd == 0: continue
                    valor_parcela = mov.valor / qtd
                    obs_str = f" | Obs: {mov.observacao}" if mov.observacao else ""
                    texto_info = f"• NE {ne.numero}: {fmt_br(mov.valor)} (Ref. {qtd} meses){obs_str}"
                    for c in comps:
                        if c in mapa_pagos: 
                            mapa_pagos[c]['valor'] += valor_parcela
                            mapa_pagos[c]['detalhes_texto'].append(texto_info)
                            if qtd > 1 or mov.observacao: mapa_pagos[c]['tem_obs'] = True

        def item_centro(texto, cor=None, bg=None):
            it = QTableWidgetItem(str(texto))
            it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if cor: it.setForeground(QColor(cor))
            if bg: it.setBackground(QColor(bg))
            return it

        tot_meta = 0; tot_exec = 0; acumulado_exec_ate_agora = 0
        
        for mes in meses:
            dados = mapa_pagos[mes]
            executado = dados['valor']
            saldo_mes = meta_mensal_global - executado
            perc_mes = (executado / meta_mensal_global * 100) if meta_mensal_global > 0 else 0
            
            tot_meta += meta_mensal_global
            tot_exec += executado
            acumulado_exec_ate_agora += executado
            
            saldo_global = valor_total_contrato - acumulado_exec_ate_agora
            perc_acumulada = (acumulado_exec_ate_agora / valor_total_contrato * 100) if valor_total_contrato > 0 else 0

            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            self.tabela.setItem(row, 0, item_centro(mes))
            
            item_link = item_centro("")
            if dados['tem_obs']:
                item_link.setText("🔗") 
                item_link.setForeground(QColor("blue"))
                texto_completo = "Detalhes dos Pagamentos:\n\n" + "\n".join(dados['detalhes_texto'])
                item_link.setToolTip(texto_completo)
                item_link.setData(Qt.ItemDataRole.UserRole, texto_completo)
            self.tabela.setItem(row, 1, item_link)
            
            # --- LÓGICA DE EXIBIÇÃO ---
            if executado > 0:
                self.tabela.setItem(row, 2, item_centro(fmt_br(meta_mensal_global)))
                self.tabela.setItem(row, 3, item_centro(fmt_br(executado), cor="#27ae60"))
                self.tabela.setItem(row, 4, item_centro(fmt_br(saldo_mes), cor="red" if saldo_mes < -0.01 else None))
                bg_perc = "#d5f5e3" if perc_mes >= 100 else None
                self.tabela.setItem(row, 5, item_centro(f"{perc_mes:.1f}%", bg=bg_perc))
            else:
                self.tabela.setItem(row, 2, item_centro("-"))
                self.tabela.setItem(row, 3, item_centro("-"))
                self.tabela.setItem(row, 4, item_centro("-"))
                self.tabela.setItem(row, 5, item_centro("-"))

            self.tabela.setItem(row, 6, item_centro(fmt_br(saldo_global)))
            self.tabela.setItem(row, 7, item_centro(f"{perc_acumulada:.1f}%"))

        # --- TOTAIS ---
        row = self.tabela.rowCount()
        self.tabela.insertRow(row)
        font_b = QFont(); font_b.setBold(True)
        it_tot = item_centro("TOTAL"); it_tot.setFont(font_b)
        self.tabela.setItem(row, 0, it_tot)
        it_m = item_centro(fmt_br(tot_meta)); it_m.setFont(font_b)
        self.tabela.setItem(row, 2, it_m)
        it_e = item_centro(fmt_br(tot_exec)); it_e.setFont(font_b)
        self.tabela.setItem(row, 3, it_e)
        
        # --- NOVO: TOTAL SALDO MENSAL ---
        saldo_mes_total = tot_meta - tot_exec
        it_s = item_centro(fmt_br(saldo_mes_total)); it_s.setFont(font_b)
        if saldo_mes_total < 0: it_s.setForeground(QColor("red"))
        self.tabela.setItem(row, 4, it_s)
        # --------------------------------

    def mostrar_detalhes_clique(self, row, col):
        item = self.tabela.item(row, col)
        if item and item.text() == "🔗":
            texto = item.data(Qt.ItemDataRole.UserRole)
            if texto: DarkMessageBox.info(self, "Detalhes", texto)

    def copiar_tabela(self):
        self.tabela.selectAll()
        self.tabela.copiar_selecao()
        self.tabela.clearSelection()
        DarkMessageBox.info(self, "Sucesso", "Tabela copiada para a área de transferência!")

#-- Diálogo de Histórico Maximizado ---
class DialogoHistoricoMaximizado(BaseDialog):
    def __init__(self, ne, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Histórico Completo: NE {ne.numero}")
        self.resize(800, 600) # Janela grande
        
        layout = QVBoxLayout(self)
        
        # Cabeçalho
        lbl_titulo = QLabel(f"Histórico Financeiro da NE {ne.numero}")
        lbl_titulo.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_desc = QLabel(ne.descricao)
        lbl_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_desc.setStyleSheet("color: #aaa; margin-bottom: 10px;")
        
        layout.addWidget(lbl_titulo)
        layout.addWidget(lbl_desc)
        
        # Tabela
        self.tabela = TabelaExcel()
        self.tabela.setColumnCount(4)
        self.tabela.setHorizontalHeaderLabels(["Competência", "Tipo de Movimento", "Valor", "Saldo Restante"])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.tabela)
        
        # Preenchimento dos Dados
        self.preencher_dados(ne)
        
        # Botões de Ação
        btns = QHBoxLayout()
        btn_copiar = QPushButton("Copiar Tabela")
        btn_copiar.clicked.connect(self.copiar_tudo)
        btn_copiar.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 8px;") # Verde
        
        btn_fechar = QPushButton("Fechar")
        btn_fechar.clicked.connect(self.close)
        
        btns.addWidget(btn_copiar)
        btns.addStretch()
        btns.addWidget(btn_fechar)
        
        layout.addLayout(btns)
        
    def preencher_dados(self, ne):
        self.tabela.setRowCount(0)
        saldo_corrente = ne.valor_inicial
        fonte_negrito = QFont(); fonte_negrito.setBold(True)
        
        for row, m in enumerate(ne.historico):
            self.tabela.insertRow(row)
            
            if m.tipo == "Pagamento":
                saldo_corrente -= m.valor
            
            # Formatação
            item_comp = QTableWidgetItem(m.competencia)
            item_tipo = QTableWidgetItem(m.tipo)
            item_valor = QTableWidgetItem(fmt_br(m.valor))
            item_saldo = QTableWidgetItem(fmt_br(saldo_corrente))
            item_saldo.setForeground(QColor("#27ae60")) # Verde
            
            # Alinhamento Centro
            for i in [item_comp, item_tipo, item_valor, item_saldo]:
                i.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Destaque para Emissão Original
            if m.tipo == "Emissão Original":
                for i in [item_comp, item_tipo, item_valor, item_saldo]:
                    i.setFont(fonte_negrito)
            
            self.tabela.setItem(row, 0, item_comp)
            self.tabela.setItem(row, 1, item_tipo)
            self.tabela.setItem(row, 2, item_valor)
            self.tabela.setItem(row, 3, item_saldo)

    def copiar_tudo(self):
        self.tabela.selectAll()
        self.tabela.copiar_selecao()
        self.tabela.clearSelection()
        DarkMessageBox.info(self, "Copiado", "Tabela copiada para a área de transferência!\nBasta colar no Excel (Ctrl+V).")

# --- NOVAS CLASSES DE AUDITORIA E LOGIN ---

class RegistroLog:
    def __init__(self, data, nome, cpf, acao, detalhe):
        self.data = data
        self.nome = nome
        self.cpf = cpf
        self.acao = acao
        self.detalhe = detalhe

    def to_dict(self): return self.__dict__
    
    @staticmethod
    def from_dict(d):
        return RegistroLog(d['data'], d['nome'], d['cpf'], d['acao'], d.get('detalhe', ''))


class DialogoLogin(BaseDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Acesso ao Sistema GC")
        self.setModal(True)
        self.resize(450, 220)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint)
        
        main_layout = QVBoxLayout(self)

        # --- Cabeçalho com Ícone ---
        header = QHBoxLayout()
        
        lbl_icon = QLabel()
        # Caminho absoluto para o ícone
        base_path = os.path.dirname(os.path.abspath(__file__))
        path_icon = os.path.join(base_path, "icon_gc.png")
        
        if os.path.exists(path_icon):
            pix = QPixmap(path_icon).scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            lbl_icon.setPixmap(pix)
        
        lbl_titulo = QLabel("GESTÃO DE CONTRATOS")
        lbl_titulo.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        lbl_titulo.setStyleSheet("color: #2c3e50; margin-left: 10px;")
        
        header.addWidget(lbl_icon)
        header.addWidget(lbl_titulo)
        header.addStretch()
        main_layout.addLayout(header)

        # --- Formulário ---
        form_layout = QFormLayout()
        
        self.inp_nome = QLineEdit()
        self.inp_nome.setPlaceholderText("Seu Nome")
        
        self.inp_cpf = QLineEdit()
        self.inp_cpf.setInputMask("999.999.999-99")
        
        # Tenta carregar último login ao abrir a janela
        self.carregar_ultimo_login()
        
        form_layout.addRow("Nome:", self.inp_nome)
        form_layout.addRow("CPF:", self.inp_cpf)
        
        main_layout.addLayout(form_layout)
        main_layout.addSpacing(10)
        
        # --- Botões Lado a Lado ---
        btn_layout = QHBoxLayout()
        
        btn_entrar = QPushButton("Entrar")
        btn_entrar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_entrar.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 8px 20px;")
        btn_entrar.clicked.connect(self.validar)
        
        btn_sair = QPushButton("Sair")
        btn_sair.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_sair.setStyleSheet("padding: 8px 20px;")
        btn_sair.clicked.connect(sys.exit)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_sair)
        btn_layout.addWidget(btn_entrar)
        
        main_layout.addLayout(btn_layout)
        
        aplicar_estilo_janela(self)

    def get_config_path(self):
        """Retorna o caminho exato do config.json na mesma pasta do script"""
        pasta_app = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(pasta_app, "config.json")

    def carregar_ultimo_login(self):
        caminho = self.get_config_path()
        try:
            if os.path.exists(caminho):
                with open(caminho, "r", encoding='utf-8') as f:
                    cfg = json.load(f)
                    last = cfg.get("ultimo_usuario", {})
                    if last:
                        self.inp_nome.setText(last.get("nome", ""))
                        self.inp_cpf.setText(last.get("cpf", ""))
        except Exception as e:
            print(f"Erro ao ler config: {e}")

    def validar(self):
        nome = self.inp_nome.text().strip()
        cpf = self.inp_cpf.text()
        
        if len(nome) < 3 or not self.inp_cpf.hasAcceptableInput():
            DarkMessageBox.warning(self, "Dados Inválidos", "Preencha seu Nome e CPF corretamente.")
            return
            
        # Salva ANTES de fechar a janela
        self.salvar_login_local(nome, cpf)
        self.accept()

    def salvar_login_local(self, nome, cpf):
        caminho = self.get_config_path()
        try:
            cfg = {}
            # Se já existir arquivo, lê o conteúdo atual para não perder outras configs (tema, etc)
            if os.path.exists(caminho):
                with open(caminho, "r", encoding='utf-8') as f:
                    try:
                        cfg = json.load(f)
                    except:
                        cfg = {}
            
            # Atualiza apenas os dados de login
            cfg["ultimo_usuario"] = {"nome": nome, "cpf": cpf}
            
            # Grava no disco
            with open(caminho, "w", encoding='utf-8') as f:
                json.dump(cfg, f, indent=4)
                
        except Exception as e:
            print(f"Erro ao salvar config: {e}")

    def get_dados(self):
        return self.inp_nome.text().strip(), self.inp_cpf.text()


class DialogoAuditoria(BaseDialog):
    def __init__(self, lista_logs, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Histórico de Alterações (Auditoria)")
        self.resize(1100, 700) # Tamanho padrão caso o usuário restaure a janela
        
        # Garante que os botões de maximizar/minimizar apareçam
        self.setWindowFlags(self.windowFlags() | 
                            Qt.WindowType.WindowMaximizeButtonHint | 
                            Qt.WindowType.WindowMinimizeButtonHint |
                            Qt.WindowType.WindowCloseButtonHint)
        
        layout = QVBoxLayout(self)
        
        lbl_info = QLabel(f"Total de registros encontrados: {len(lista_logs)}")
        lbl_info.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 5px")
        layout.addWidget(lbl_info)
        
        self.tabela = TabelaExcel()
        self.tabela.setColumnCount(5)
        self.tabela.setHorizontalHeaderLabels(["Data/Hora", "Usuário", "CPF", "Ação", "Detalhes"])
        
        # --- CONFIGURAÇÃO VISUAL ---
        header = self.tabela.horizontalHeader()
        self.tabela.setColumnWidth(0, 140) 
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.tabela.setColumnWidth(2, 110)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        
        self.tabela.setWordWrap(True)
        self.tabela.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        self.tabela.setRowCount(0)
        for log in reversed(lista_logs):
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            
            def item_formatado(texto):
                i = QTableWidgetItem(str(texto))
                i.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
                return i

            self.tabela.setItem(row, 0, item_formatado(log.data))
            self.tabela.setItem(row, 1, item_formatado(log.nome))
            self.tabela.setItem(row, 2, item_formatado(log.cpf))
            self.tabela.setItem(row, 3, item_formatado(log.acao))
            self.tabela.setItem(row, 4, item_formatado(log.detalhe))
            
        layout.addWidget(self.tabela)
        
        btn_fechar = QPushButton("Fechar")
        btn_fechar.clicked.connect(self.accept)
        layout.addWidget(btn_fechar)
        
        # --- APLICA O ESTILO ESCURO E MAXIMIZA ---
        aplicar_estilo_janela(self)
        self.showMaximized() # <--- ADICIONADO AQUI

class DialogoAparencia(BaseDialog):
    def __init__(self, cor_fundo_atual, cor_sel_atual, tam_fonte_atual, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Personalizar Aparência")
        self.resize(400, 350)
        
        layout = QVBoxLayout(self)
        
        # --- Grupo 1: Cores ---
        layout.addWidget(QLabel("Personalização de Cores:"))
        
        # Cor de Fundo
        h_bg = QHBoxLayout()
        self.btn_cor_bg = QPushButton()
        self.btn_cor_bg.setFixedSize(40, 25)
        self.cor_bg_escolhida = cor_fundo_atual
        self.atualizar_btn_cor(self.btn_cor_bg, self.cor_bg_escolhida)
        self.btn_cor_bg.clicked.connect(self.escolher_cor_bg)
        
        h_bg.addWidget(QLabel("Cor de Fundo Principal:"))
        h_bg.addWidget(self.btn_cor_bg)
        layout.addLayout(h_bg)
        
        # Cor de Seleção
        h_sel = QHBoxLayout()
        self.btn_cor_sel = QPushButton()
        self.btn_cor_sel.setFixedSize(40, 25)
        self.cor_sel_escolhida = cor_sel_atual
        self.atualizar_btn_cor(self.btn_cor_sel, self.cor_sel_escolhida)
        self.btn_cor_sel.clicked.connect(self.escolher_cor_sel)
        
        h_sel.addWidget(QLabel("Cor de Realce/Seleção:"))
        h_sel.addWidget(self.btn_cor_sel)
        layout.addLayout(h_sel)
        
        layout.addSpacing(20)
        
        # --- Grupo 2: Fonte ---
        layout.addWidget(QLabel("Tamanho da Fonte (12px - 16px):"))
        
        h_font = QHBoxLayout()
        self.lbl_tamanho = QLabel(f"{tam_fonte_atual}px")
        self.lbl_tamanho.setFixedWidth(40)
        self.lbl_tamanho.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_tamanho.setStyleSheet("font-weight: bold; border: 1px solid #555; border-radius: 4px;")
        
        self.slider_fonte = QSlider(Qt.Orientation.Horizontal)
        self.slider_fonte.setMinimum(12)
        self.slider_fonte.setMaximum(16)
        self.slider_fonte.setValue(tam_fonte_atual)
        self.slider_fonte.valueChanged.connect(lambda v: self.lbl_tamanho.setText(f"{v}px"))
        
        h_font.addWidget(self.slider_fonte)
        h_font.addWidget(self.lbl_tamanho)
        layout.addLayout(h_font)
        
        layout.addWidget(QLabel("Nota: Tamanhos muito grandes podem ocultar textos em tabelas.", self))
        
        layout.addStretch()
        
        # --- Botões ---
        btns = QHBoxLayout()
        btn_padrao = QPushButton("Restaurar Padrão")
        btn_padrao.clicked.connect(self.restaurar_padrao)
        
        btn_salvar = QPushButton("Aplicar e Salvar")
        btn_salvar.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
        btn_salvar.clicked.connect(self.accept)
        
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.reject)
        
        btns.addWidget(btn_padrao)
        btns.addStretch()
        btns.addWidget(btn_cancelar)
        btns.addWidget(btn_salvar)
        layout.addLayout(btns)

    def atualizar_btn_cor(self, btn, cor_hex):
        btn.setStyleSheet(f"background-color: {cor_hex}; border: 1px solid #888; border-radius: 4px;")

    def escolher_cor_bg(self):
        c = QColorDialog.getColor(QColor(self.cor_bg_escolhida), self, "Escolher Fundo")
        if c.isValid():
            self.cor_bg_escolhida = c.name()
            self.atualizar_btn_cor(self.btn_cor_bg, self.cor_bg_escolhida)

    def escolher_cor_sel(self):
        c = QColorDialog.getColor(QColor(self.cor_sel_escolhida), self, "Escolher Seleção")
        if c.isValid():
            self.cor_sel_escolhida = c.name()
            self.atualizar_btn_cor(self.btn_cor_sel, self.cor_sel_escolhida)

    def restaurar_padrao(self):
        # Restaura para o padrão Dark
        self.cor_bg_escolhida = "#2b2b2b"
        self.cor_sel_escolhida = "#4da6ff"
        self.slider_fonte.setValue(14)
        self.atualizar_btn_cor(self.btn_cor_bg, self.cor_bg_escolhida)
        self.atualizar_btn_cor(self.btn_cor_sel, self.cor_sel_escolhida)

    def get_dados(self):
        return self.cor_bg_escolhida, self.cor_sel_escolhida, self.slider_fonte.value()

class ConsultorIA:
    def __init__(self, dados_contratos):
        self.ativo = False
        self.dados = dados_contratos 
        try:
            if "COLE_SUA" in CHAVE_API_GEMINI:
                return 
            
            genai.configure(api_key=CHAVE_API_GEMINI)
            
            # --- SOLUÇÃO DEFINITIVA: AUTO-DETECÇÃO DE MODELO ---
            # Em vez de fixar um nome, listamos o que sua conta tem acesso.
            modelo_escolhido = 'gemini-1.5-flash' # Um fallback caso tudo falhe
            
            try:
                print("Buscando modelos de IA disponíveis...")
                for m in genai.list_models():
                    # Procura um modelo que gere texto (generateContent) e seja da família Gemini
                    if 'generateContent' in m.supported_generation_methods:
                        if 'gemini' in m.name.lower():
                            # Limpa o prefixo 'models/' se vier
                            nome_limpo = m.name.replace('models/', '')
                            modelo_escolhido = nome_limpo
                            # Se achar um modelo "1.5", dá preferência e para de procurar
                            if '1.5' in nome_limpo: 
                                break
            except Exception as e:
                print(f"Erro ao listar modelos: {e}")

            print(f"--> Modelo de IA Conectado: {modelo_escolhido}")
            self.model = genai.GenerativeModel(modelo_escolhido)
            self.ativo = True
        except Exception as e:
            print(f"Erro fatal na IA: {e}")
            self.ativo = False

    def verificar_status(self):
        if not self.ativo:
            return False, "Erro: IA não conectada. Verifique o terminal para ver o erro detalhado."
        return True, "OK"

    def gerar_contexto_global(self):
        txt = "DADOS DO SISTEMA DE CONTRATOS:\n"
        hoje = datetime.now().strftime("%d/%m/%Y")
        txt += f"Data de Hoje: {hoje}\n\n"
        
        for c in self.dados:
            # Proteção para datas inválidas
            try:
                dt_fim = str_to_date(c.get_vigencia_final_atual())
                status = "Vigente" if dt_fim >= datetime.now() else "Vencido"
            except:
                status = "Data Inválida"

            total_pago = 0.0
            total_empenhado = 0.0
            
            for ne in c.lista_notas_empenho:
                total_empenhado += ne.valor_inicial
                total_pago += ne.total_pago
            
            txt += f"- Contrato {c.numero} | Prestador: {c.prestador} | Objeto: {c.descricao}\n"
            txt += f"  Vigência: {c.vigencia_inicio} a {c.get_vigencia_final_atual()} ({status})\n"
            txt += f"  Total Empenhado: R$ {total_empenhado:.2f} | Total Pago: R$ {total_pago:.2f}\n"
            txt += "  Serviços:\n"
            for sub in c.lista_servicos:
                txt += f"    * {sub.descricao} (Mensal: R$ {sub.valor_mensal:.2f})\n"
            txt += "---\n"
        return txt

    def analisar_risco_contrato(self, contrato, ciclo_id):
        if not self.ativo: return "IA Não disponível."
        
        ciclo = next((c for c in contrato.ciclos if c.id_ciclo == ciclo_id), None)
        nome_ciclo = ciclo.nome if ciclo else "Geral"
        
        prompt = f"""
        Aja como um Auditor Fiscal. Analise este contrato e aponte RISCOS.
        Seja breve.
        
        CONTRATO: {contrato.numero} - {contrato.prestador}
        OBJETO: {contrato.descricao}
        CICLO: {nome_ciclo}
        VIGÊNCIA FINAL: {contrato.get_vigencia_final_atual()}
        
        DETALHES FINANCEIROS:
        """
        for sub in contrato.lista_servicos:
            val_ciclo = sub.get_valor_ciclo(ciclo_id)
            gasto_emp = sum(n.valor_inicial for n in contrato.lista_notas_empenho if n.subcontrato_idx == contrato.lista_servicos.index(sub) and n.ciclo_id == ciclo_id)
            gasto_pag = 0.0
            for n in contrato.lista_notas_empenho:
                 if n.subcontrato_idx == contrato.lista_servicos.index(sub) and n.ciclo_id == ciclo_id:
                     gasto_pag += n.total_pago
            
            saldo = val_ciclo - gasto_pag
            prompt += f"\n- Serviço '{sub.descricao}': Orçamento R$ {val_ciclo:.2f} | Empenhado R$ {gasto_emp:.2f} | Pago R$ {gasto_pag:.2f} | Saldo R$ {saldo:.2f}"
            
        prompt += "\n\nResponda em Tópicos: 1. Execução, 2. Prazos, 3. Risco (Alto/Médio/Baixo)."
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e: return f"Erro IA: {e}"



    def perguntar_aos_dados(self, pergunta_usuario):
        if not self.ativo: return "IA Não disponível."
        
        contexto = self.gerar_contexto_global()
        
        prompt = f"""
        {contexto}
        
        Com base APENAS nos dados acima, responda:
        PERGUNTA: {pergunta_usuario}
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e: return f"Erro IA: {e}"


    def analisar_servico_especifico(self, servico, lista_nes, ciclo_id):
        """Analisa apenas UM serviço isoladamente"""
        if not self.ativo: return "IA Não disponível."

        valor_ciclo = servico.get_valor_ciclo(ciclo_id)
        
        # Calcula totais
        total_pago = 0.0
        historico_txt = ""
        
        for ne in lista_nes:
            for mov in ne.historico:
                if mov.tipo == "Pagamento":
                    total_pago += mov.valor
                    historico_txt += f"- {mov.competencia}: R$ {mov.valor:.2f}\n"

        saldo = valor_ciclo - total_pago
        perc_exec = (total_pago / valor_ciclo * 100) if valor_ciclo > 0 else 0

        prompt = f"""
        Aja como um Controlador Financeiro. Analise a execução deste SERVIÇO ESPECÍFICO de um contrato.
        
        SERVIÇO: {servico.descricao}
        ORÇAMENTO TOTAL: R$ {valor_ciclo:.2f}
        EXECUTADO ATÉ AGORA: R$ {total_pago:.2f} ({perc_exec:.1f}%)
        SALDO RESTANTE: R$ {saldo:.2f}
        
        HISTÓRICO DE PAGAMENTOS:
        {historico_txt}
        
        PERGUNTA: Com base no ritmo desses pagamentos, o saldo é suficiente? Existe algum padrão anormal (picos ou quedas bruscas)?
        Seja direto e curto.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e: return f"Erro IA: {e}"


class DialogoChatIA(BaseDialog):
    def __init__(self, consultor_ia, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Assistente Inteligente (Chat com Dados)")
        self.resize(600, 500)
        self.consultor = consultor_ia
        
        layout = QVBoxLayout(self)
        
        # Histórico do Chat
        self.txt_historico = QTextEdit()
        self.txt_historico.setReadOnly(True)
        self.txt_historico.setStyleSheet("background-color: #f0f0f0; color: #333; font-size: 13px; border-radius: 5px; padding: 10px;")
        layout.addWidget(self.txt_historico)
        
        self.txt_historico.append("<b>🤖 Assistente:</b> Olá! Analisei todos os seus contratos. Pode me perguntar coisas como:\n"
                                  "<i>- Qual contrato vence este mês?</i>\n"
                                  "<i>- Quanto gastamos no total com a empresa X?</i>\n"
                                  "<i>- Resuma o contrato 123.</i>\n")
        
        # Área de Input
        h_input = QHBoxLayout()
        self.inp_msg = QLineEdit()
        self.inp_msg.setPlaceholderText("Digite sua pergunta aqui...")
        self.inp_msg.returnPressed.connect(self.enviar_pergunta)
        
        btn_env = QPushButton("Enviar")
        btn_env.setStyleSheet("background-color: #2980b9; color: white; font-weight: bold;")
        btn_env.clicked.connect(self.enviar_pergunta)
        
        h_input.addWidget(self.inp_msg)
        h_input.addWidget(btn_env)
        layout.addLayout(h_input)
        
    def enviar_pergunta(self):
        pgt = self.inp_msg.text().strip()
        if not pgt: return
        
        self.txt_historico.append(f"<b>👤 Você:</b> {pgt}")
        self.inp_msg.clear()
        self.inp_msg.setDisabled(True)
        self.txt_historico.append("<i>🤖 Pensando...</i>")
        QApplication.processEvents() # Atualiza tela
        
        resp = self.consultor.perguntar_aos_dados(pgt)
        
        # Remove o "Pensando..." (gambiarra visual simples: apenas adiciona a resposta)
        self.txt_historico.append(f"<b>🤖 Assistente:</b>\n{resp}")
        self.txt_historico.append("-" * 30)
        self.inp_msg.setDisabled(False)
        self.inp_msg.setFocus()

class DialogoNotificacoes(BaseDialog):
    def __init__(self, lista_alertas, consultor_ia, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Central de Notificações e Alertas")
        self.resize(700, 500)
        self.lista_alertas = lista_alertas
        self.consultor = consultor_ia
        
        layout = QVBoxLayout(self)
        
        # Cabeçalho
        h_top = QHBoxLayout()
        lbl_icon = QLabel("🔔")
        lbl_icon.setFont(QFont("Arial", 24))
        lbl_tit = QLabel(f"Foram encontrados {len(lista_alertas)} pontos de atenção")
        lbl_tit.setStyleSheet("font-size: 16px; font-weight: bold; color: #c0392b;")
        h_top.addWidget(lbl_icon)
        h_top.addWidget(lbl_tit)
        h_top.addStretch()
        layout.addLayout(h_top)
        
        # Lista de Alertas
        self.list_widget = QListWidget()
        for alerta in lista_alertas:
            item = QListWidgetItem()
            # Formatação visual dependendo da gravidade
            texto = f"[{alerta['tipo']}] {alerta['mensagem']}"
            item.setText(texto)
            
            if "CRÍTICO" in alerta['gravidade']:
                item.setForeground(QColor("#e74c3c")) # Vermelho
                item.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            elif "ALTA" in alerta['gravidade']:
                item.setForeground(QColor("#d35400")) # Laranja
            else:
                item.setForeground(QColor("#f39c12")) # Amarelo escuro
                
            self.list_widget.addItem(item)
            
        layout.addWidget(self.list_widget)
        
        # Área da IA
        self.grp_ia = QGroupBox("Análise Inteligente de Riscos")
        l_ia = QVBoxLayout(self.grp_ia)
        
        self.txt_ia = QTextEdit()
        self.txt_ia.setReadOnly(True)
        self.txt_ia.setPlaceholderText("Clique no botão abaixo para pedir à IA um plano de ação sobre esses alertas...")
        self.txt_ia.setMaximumHeight(150)
        
        self.btn_ia = QPushButton("🤖 Gerar Plano de Ação (IA)")
        self.btn_ia.setStyleSheet("background-color: #8e44ad; color: white; font-weight: bold; padding: 10px;")
        self.btn_ia.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_ia.clicked.connect(self.gerar_analise_ia)
        
        l_ia.addWidget(self.txt_ia)
        l_ia.addWidget(self.btn_ia)
        
        layout.addWidget(self.grp_ia)
        
        btn_fechar = QPushButton("Fechar")
        btn_fechar.clicked.connect(self.accept)
        layout.addWidget(btn_fechar)
        
    def gerar_analise_ia(self):
        if not self.lista_alertas:
            self.txt_ia.setText("Sem alertas para analisar. Tudo tranquilo!")
            return
            
        self.txt_ia.setText("⏳ A IA está analisando os prazos e saldos... Aguarde...")
        QApplication.processEvents()
        
        # Monta um resumo para a IA
        texto_alertas = "\n".join([f"- {a['tipo']}: {a['mensagem']}" for a in self.lista_alertas])
        
        prompt = f"""
        Aja como um Gestor de Contratos Sênior. O sistema detectou os seguintes problemas críticos:
        
        {texto_alertas}
        
        Gere um RESUMO EXECUTIVO curto (máx 5 linhas) sugerindo prioridades.
        O que deve ser feito primeiro? Algum aditivo urgente?
        """
        
        try:
            resp = self.consultor.model.generate_content(prompt)
            self.txt_ia.setMarkdown(resp.text)
        except Exception as e:
            self.txt_ia.setText(f"Erro na IA: {str(e)}")

# --- 3. SISTEMA PRINCIPAL ---

class SistemaGestao(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db_contratos = []
        self.db_prestadores = []
        self.db_logs = [] 
        self.lista_alertas = []
        self.contrato_selecionado = None
        self.ne_selecionada = None
        self.arquivo_db = "dados_sistema.json"
        
        # Variáveis do Usuário Atual
        self.usuario_nome = "Desconhecido"
        self.usuario_cpf = "000.000.000-00"

        # --- CORREÇÃO DE INICIALIZAÇÃO ---
        self.tema_escuro = False # Valor padrão

        self.custom_bg = None
        self.custom_sel = None
        self.tamanho_fonte = 14

        self.carregar_config()   # 1. Lê a config (incluindo tema e login)
        
        # 2. Aplica o visual sem inverter/salvar
        self.aplicar_tema_visual()
        
        # 3. Pede Login (agora o DialogoLogin vai ler o mesmo arquivo config.json)
        self.fazer_login() 
        
        self.init_ui()
        self.carregar_dados()

        # INICIA O CONSULTOR COM OS DADOS CARREGADOS
        self.ia = ConsultorIA(self.db_contratos)
        
        # Garante o estilo da janela
        aplicar_estilo_janela(self)
        
        self.em_tutorial = False

    def iniciar_tutorial_interativo(self):
        """Orquestra uma sequência de passos para ensinar o usuário"""
        
        # 1. Boas Vindas
        res = DarkMessageBox.info(self, "Tutorial Interativo", 
            "Bem-vindo ao Modo de Aprendizado!\n\n"
            "Vou guiar você criando um contrato completo do zero:\n"
            "1. Criar o Contrato\n"
            "2. Cadastrar um Serviço\n"
            "3. Emitir Nota de Empenho\n"
            "4. Realizar um Pagamento\n\n"
            "Clique em OK para começar.", QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        
        if res == QMessageBox.StandardButton.Cancel: return

        self.em_tutorial = True # Ativa o modo mágico

        try:
            # --- PASSO 1: CRIAR CONTRATO ---
            DarkMessageBox.info(self, "Passo 1/4", 
                "Primeiro, vamos cadastrar o CONTRATO.\n\n"
                "Vou abrir a janela e preencher os dados de exemplo para você.\n"
                "Apenas confira e clique em 'OK' na janela que abrir.")
            
            # Chama a função existente (que vamos modificar no Passo 3 para reagir ao tutorial)
            self.abrir_novo_contrato()
            
            # Verifica se o usuário criou mesmo (pegamos o último da lista)
            if not self.db_contratos or self.db_contratos[-1].prestador != "Empresa Tutorial Ltda":
                self.em_tutorial = False; return # Usuário cancelou
            
            # Força a abertura desse contrato na tela de detalhes
            self.contrato_selecionado = self.db_contratos[-1]
            self.atualizar_painel_detalhes()
            self.stack.setCurrentIndex(1) # Muda para a página de detalhes

            # --- PASSO 2: CRIAR SERVIÇO ---
            DarkMessageBox.info(self, "Passo 2/4", 
                "Ótimo! Contrato criado.\n\n"
                "Agora precisamos definir O QUE foi contratado (Serviços/Itens).\n"
                "Vou preencher um serviço de 'Manutenção' para você.")
            
            self.abrir_novo_servico()

            # --- PASSO 3: NOTA DE EMPENHO ---
            DarkMessageBox.info(self, "Passo 3/4", 
                "Agora que temos o contrato e o serviço, vamos reservar o dinheiro (Empenho).\n\n"
                "Vou criar uma Nota de Empenho vinculada ao serviço anterior.")
            
            self.abas.setCurrentIndex(1) # Muda para aba Financeiro visualmente
            self.dialogo_nova_ne()

            # Seleciona a NE criada para permitir o pagamento
            if self.contrato_selecionado.lista_notas_empenho:
                self.ne_selecionada = self.contrato_selecionado.lista_notas_empenho[-1]
                # Simula seleção na tabela
                self.tab_empenhos.selectRow(0)
                self.atualizar_painel_detalhes()

            # --- PASSO 4: PAGAMENTO ---
            DarkMessageBox.info(self, "Passo 4/4", 
                "Dinheiro reservado! Agora a empresa trabalhou e vamos PAGAR.\n\n"
                "Vou lançar um pagamento parcial na NE que acabamos de criar.")
            
            self.abrir_pagamento()

            # --- FIM ---
            DarkMessageBox.info(self, "Parabéns!", 
                "Tutorial Concluído com Sucesso!\n\n"
                "Você aprendeu o fluxo principal do sistema.\n"
                "Os dados criados aqui são reais, você pode excluí-los depois se quiser.")

        except Exception as e:
            DarkMessageBox.critical(self, "Erro no Tutorial", str(e))
        
        finally:
            self.em_tutorial = False # Desliga o modo mágico
        
    def fazer_login(self):
        """Abre a tela de login bloqueante no início"""
        dial = DialogoLogin()
        if dial.exec():
            self.usuario_nome, self.usuario_cpf = dial.get_dados()
        else:
            sys.exit() # Se fechar o login na força, fecha o app

    def registrar_log(self, acao, detalhe):
        """Cria um registro de auditoria e salva na memória"""
        novo_log = RegistroLog(
            datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            self.usuario_nome,
            self.usuario_cpf,
            acao,
            detalhe
        )
        self.db_logs.append(novo_log)
        # Nota: O salvamento no disco acontece no salvar_dados() geral

    def carregar_config(self):
        caminho = self.get_config_path()
        try:
            if os.path.exists(caminho):
                with open(caminho, "r", encoding='utf-8') as f:
                    cfg = json.load(f)
                    self.tema_escuro = cfg.get("tema_escuro", False)
                    # Lê personalizações
                    self.custom_bg = cfg.get("custom_bg", None)
                    self.custom_sel = cfg.get("custom_sel", None)
                    self.tamanho_fonte = cfg.get("tamanho_fonte", 14)
            else:
                self.tema_escuro = False
        except:
            self.tema_escuro = False

    def get_config_path(self):
        """Retorna o caminho exato do config.json na mesma pasta do script"""
        pasta_app = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(pasta_app, "config.json")

    def salvar_config(self):
        caminho = self.get_config_path()
        try:
            cfg = {}
            if os.path.exists(caminho):
                with open(caminho, "r", encoding='utf-8') as f:
                    try:
                        cfg = json.load(f)
                    except:
                        cfg = {}
            
            cfg["tema_escuro"] = self.tema_escuro
            # Salva personalizações
            cfg["custom_bg"] = self.custom_bg
            cfg["custom_sel"] = self.custom_sel
            cfg["tamanho_fonte"] = self.tamanho_fonte
            
            with open(caminho, "w", encoding='utf-8') as f:
                json.dump(cfg, f, indent=4)
        except Exception as e: 
            print(f"Erro ao salvar config: {e}")

    def showEvent(self, event):
        # Garante que a barra fique escura assim que o programa abre
        aplicar_estilo_janela(self)
        super().showEvent(event)

    def changeEvent(self, event):
        if event.type() == QEvent.Type.WindowStateChange:
            # O QTimer dentro da função garantirá que a cor é reaplicada
            # DEPOIS da animação de maximizar terminar.
            aplicar_estilo_janela(self) 
        super().changeEvent(event)


    def closeEvent(self, event):
        self.salvar_dados()
        event.accept()

    def salvar_dados(self):
        # Cria um dicionário contendo Contratos E Logs
        dados_completos = {
            "contratos": [c.to_dict() for c in self.db_contratos],
            "logs": [l.to_dict() for l in self.db_logs],
            "prestadores": [p.to_dict() for p in self.db_prestadores]
        }
        try:
            with open(self.arquivo_db, 'w', encoding='utf-8-sig') as f:
                json.dump(dados_completos, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar: {e}")

    def processar_alertas(self):
        """Varredura automática de riscos"""
        self.lista_alertas = []
        hoje = datetime.now()
        
        for c in self.db_contratos:
            # 1. Alerta de Vencimento (Prazos)
            try:
                dt_fim = str_to_date(c.get_vigencia_final_atual())
                dias_restantes = (dt_fim - hoje).days
                
                if dias_restantes < 0:
                    self.lista_alertas.append({
                        "tipo": "VENCIDO", "gravidade": "CRÍTICO",
                        "mensagem": f"Contrato {c.numero} ({c.prestador}) venceu há {abs(dias_restantes)} dias!"
                    })
                elif dias_restantes <= 45: # Avisa com 45 dias
                    self.lista_alertas.append({
                        "tipo": "VENCIMENTO", "gravidade": "ALTA",
                        "mensagem": f"Contrato {c.numero} vence em {dias_restantes} dias. Renove já!"
                    })
            except: pass

            # 2. Alerta de Saldo (Financeiro) - Olha o último ciclo ativo
            ciclo = c.ciclos[-1] if c.ciclos else None
            if ciclo and "(CANCELADO)" not in ciclo.nome:
                for sub in c.lista_servicos:
                    orcamento = sub.get_valor_ciclo(ciclo.id_ciclo)
                    # Calcula gasto
                    gasto = sum(ne.valor_inicial for ne in c.lista_notas_empenho 
                                if ne.subcontrato_idx == c.lista_servicos.index(sub) 
                                and ne.ciclo_id == ciclo.id_ciclo)
                    saldo = orcamento - gasto
                    
                    if orcamento > 0:
                        perc = (saldo / orcamento) * 100
                        if saldo < 0:
                            self.lista_alertas.append({
                                "tipo": "DÉFICIT", "gravidade": "CRÍTICO",
                                "mensagem": f"Contrato {c.numero}: '{sub.descricao}' estourou em {fmt_br(abs(saldo))}!"
                            })
                        elif perc < 15: # Menos de 15% de saldo
                            self.lista_alertas.append({
                                "tipo": "SALDO BAIXO", "gravidade": "MÉDIA",
                                "mensagem": f"Contrato {c.numero}: '{sub.descricao}' tem apenas {perc:.1f}% de saldo."
                            })

        # Atualiza o botão visualmente
        # ATUALIZA O BOTÃO VISUALMENTE (ESTILO MINIMALISTA)
        if hasattr(self, 'btn_notificacoes'):
            qtd = len(self.lista_alertas)
            if qtd > 0:
                self.btn_notificacoes.setText(f"🔔 {qtd}")
                # Fica Vermelho, mas sem fundo (apenas texto)
                self.btn_notificacoes.setStyleSheet("""
                    QPushButton { 
                        border: none; 
                        background: transparent; 
                        font-size: 14px; 
                        color: #e74c3c; /* Vermelho Alerta */
                        font-weight: bold; 
                    }
                    QPushButton:hover { background-color: #ffe6e6; border-radius: 5px; }
                """)
            else:
                self.btn_notificacoes.setText("🔔")
                # Fica Cinza discreto
                self.btn_notificacoes.setStyleSheet("""
                    QPushButton { 
                        border: none; 
                        background: transparent; 
                        font-size: 16px; 
                        color: #7f8c8d; /* Cinza */
                    }
                    QPushButton:hover { background-color: #f0f0f0; border-radius: 5px; }
                """)

    def abrir_notificacoes(self):
        self.processar_alertas() # Recalcula ao abrir
        dial = DialogoNotificacoes(self.lista_alertas, self.ia, parent=self)
        dial.exec()


    def carregar_dados(self):
        # Atualiza título para saber qual base está ativa
        nome_base = os.path.basename(self.arquivo_db)
        self.setWindowTitle(f"Gestão de Contratos - [Base: {nome_base}]")

        if not os.path.exists(self.arquivo_db): return
        try:
            with open(self.arquivo_db, 'r', encoding='utf-8-sig') as f:
                raw_data = json.load(f)
                
                if isinstance(raw_data, list):
                    self.db_contratos = [Contrato.from_dict(d) for d in raw_data]
                    self.db_logs = []
                else:
                    self.db_contratos = [Contrato.from_dict(d) for d in raw_data.get("contratos", [])]
                    self.db_logs = [RegistroLog.from_dict(d) for d in raw_data.get("logs", [])]
                    self.db_prestadores = [Prestador.from_dict(d) for d in raw_data.get("prestadores", [])]

            self.filtrar_contratos()
            self.processar_alertas()
        except Exception as e:
            DarkMessageBox.critical(self, "Erro ao Carregar", f"Erro: {str(e)}")

    def alternar_base_dados(self):
        # 1. Salva a base atual antes de trocar
        self.salvar_dados()
        
        # 2. Pede o novo arquivo
        fname, _ = QFileDialog.getOpenFileName(self, "Selecionar Base de Dados", "", "JSON Files (*.json)")
        
        if fname:
            # Verifica se é o mesmo
            if os.path.abspath(fname) == os.path.abspath(self.arquivo_db):
                DarkMessageBox.info(self, "Aviso", "Você selecionou a mesma base que já está aberta.")
                return

            # 3. Troca o caminho do arquivo alvo
            self.arquivo_db = fname
            
            # 4. Recarrega tudo
            self.db_contratos = []
            self.db_logs = []
            self.contrato_selecionado = None
            self.ne_selecionada = None
            
            self.carregar_dados() # Vai ler do novo self.arquivo_db
            
            # Atualiza Título da Janela
            nome_arquivo = os.path.basename(self.arquivo_db)
            self.setWindowTitle(f"Gestão de Contratos - [Base: {nome_arquivo}]")
            
            DarkMessageBox.info(self, "Base Trocada", f"Agora você está usando a base:\n{nome_arquivo}")
    
    def sincronizar_nuvem(self):
        try:
            driver = sinc.DriveConector()
            driver.conectar()
        except Exception as e:
            DarkMessageBox.critical(self, "Erro de Conexão", f"Erro: {str(e)}")
            return

        nome_nuvem = "dados_gestao_contratos_db.json"
        
        arquivo_remoto = None
        try:
            arquivo_remoto = driver.buscar_id_arquivo(nome_nuvem)
        except: pass

        msg_status = "Arquivo encontrado no Drive!" if arquivo_remoto else "Arquivo NÃO encontrado (Será criado)."
        
        mbox = DarkMessageBox(self)
        mbox.setWindowTitle("Sincronização Nuvem")
        mbox.setText(f"Status da Nuvem: {msg_status}\n\nBase Atual: {os.path.basename(self.arquivo_db)}\n\nEscolha a operação:")
        
        btn_enviar = mbox.addButton("Enviar (Sobrescrever Nuvem)", QMessageBox.ButtonRole.ActionRole)
        btn_mesclar = mbox.addButton("Sincronizar (Mesclar)", QMessageBox.ButtonRole.ActionRole)
        
        # --- MUDANÇA: BOTÃO NOVO ---
        btn_baixar_sep = mbox.addButton("Baixar Base Separada\n(Salvar Como...)", QMessageBox.ButtonRole.ActionRole)
        # ---------------------------
        
        btn_cancel = mbox.addButton("Cancelar", QMessageBox.ButtonRole.RejectRole)
        
        mbox.exec()
        
        if mbox.clickedButton() == btn_cancel: return

        # 1. ENVIAR
        if mbox.clickedButton() == btn_enviar:
            if DarkMessageBox.question(self, "Confirmar", "Sobrescrever a nuvem com sua base atual?") == QMessageBox.StandardButton.Yes:
                try:
                    dados = {"contratos": [c.to_dict() for c in self.db_contratos], "logs": [l.to_dict() for l in self.db_logs]}
                    fid = arquivo_remoto['id'] if arquivo_remoto else None
                    driver.subir_json(nome_nuvem, dados, file_id_existente=fid)
                    DarkMessageBox.info(self, "Sucesso", "Enviado!")
                except Exception as e: DarkMessageBox.critical(self, "Erro", str(e))

        # 2. MESCLAR
        elif mbox.clickedButton() == btn_mesclar:
            if not arquivo_remoto: return
            try:
                # (Lógica de mesclagem mantida igual ao anterior - omitida para brevidade, mantenha a sua)
                # ... copie a lógica do bloco 'elif mbox.clickedButton() == btn_baixar:' da resposta anterior
                # ... mas lembre de manter o nome btn_mesclar
                pass # Substitua pelo código de mesclagem
            except: pass

        # 3. BAIXAR SEPARADO (NOVO)
        elif mbox.clickedButton() == btn_baixar_sep:
            if not arquivo_remoto:
                DarkMessageBox.warning(self, "Aviso", "Nada na nuvem para baixar.")
                return

            # Pergunta onde salvar
            fpath, _ = QFileDialog.getSaveFileName(self, "Salvar Base da Nuvem Como...", "base_nuvem_copia.json", "JSON (*.json)")
            if not fpath: return

            try:
                dados_nuvem = driver.baixar_json(arquivo_remoto['id'])
                
                # Salva no arquivo escolhido
                with open(fpath, 'w', encoding='utf-8-sig') as f:
                    json.dump(dados_nuvem, f, indent=4, ensure_ascii=False)
                
                # Pergunta se quer usar essa base agora
                if DarkMessageBox.question(self, "Base Baixada", 
                                        f"Arquivo salvo em:\n{fpath}\n\nDeseja carregar esta base no sistema agora?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
                    
                    self.arquivo_db = fpath
                    self.db_contratos = []
                    self.db_logs = []
                    self.carregar_dados() # Recarrega do novo arquivo
                    
                else:
                    DarkMessageBox.info(self, "Sucesso", "Arquivo salvo. Você pode abri-lo depois pelo menu Arquivo > Trocar Base.")

            except Exception as e:
                DarkMessageBox.critical(self, "Erro", f"Falha ao baixar: {str(e)}")

    def alternar_tema(self):
        # 1. LIMPEZA: Remove as cores personalizadas para destravar os temas padrão
        self.custom_bg = None
        self.custom_sel = None

        # 2. Lógica padrão: Inverte o estado
        self.tema_escuro = not self.tema_escuro
        
        # 3. Aplica visualmente
        self.aplicar_tema_visual()
        aplicar_estilo_janela(self)
        
        # 4. Salva no arquivo
        self.salvar_config()


    def aplicar_tema_visual(self):
        aplicar_estilo_janela(self)
        app = QApplication.instance()

        # Definição de Cores Base
        if self.custom_bg:
            # --- MODO PERSONALIZADO ---
            # Se o usuário definiu cor, usamos ela como base e calculamos as outras
            cor_base = QColor(self.custom_bg)
            cor_destaque = QColor(self.custom_sel if self.custom_sel else "#4da6ff")
            
            # Detecta se a cor escolhida é escura ou clara para ajustar o texto
            is_dark = cor_base.lightness() < 128
            
            c_fundo = cor_base.name()
            
            # Gera variações mantendo proporção
            if is_dark:
                c_fundo_alt = cor_base.lighter(115).name() # 15% mais claro
                c_header = cor_base.lighter(130).name()    # 30% mais claro
                c_borda = cor_base.lighter(150).name()     # 50% mais claro
                c_texto = "#ffffff"
                c_texto_sec = "#cccccc"
                c_btn = cor_base.lighter(125).name()
                c_btn_hover = cor_base.lighter(140).name()
                c_azul_fundo = cor_base.lighter(110).name()
                c_resumo_bg = cor_base.lighter(105).name()
            else:
                c_fundo_alt = "#ffffff"
                c_header = cor_base.darker(110).name()
                c_borda = cor_base.darker(130).name()
                c_texto = "#000000"
                c_texto_sec = "#333333"
                c_btn = cor_base.lighter(105).name()
                c_btn_hover = cor_base.darker(105).name()
                c_azul_fundo = cor_base.darker(105).name()
                c_resumo_bg = "#f9f9f9"

            c_selecao = cor_destaque.name()
            c_azul = cor_destaque.name()
            c_texto_sel = "#ffffff" if is_dark else "#000000"
            c_borda_foco = c_selecao

        elif self.tema_escuro:
            # --- DARK MODE PADRÃO ---
            c_fundo = "#2b2b2b"; c_fundo_alt = "#1e1e1e"; c_texto = "#ffffff"; c_texto_sec = "#cccccc"
            c_borda = "#555555"; c_borda_foco = "#4da6ff"; c_azul = "#4da6ff"; c_azul_fundo = "#3e3e3e"
            c_btn = "#3c3c3c"; c_btn_hover = "#505050"; c_header = "#444444"; c_selecao = "#4da6ff"; c_texto_sel = "#000000"
            c_resumo_bg = "#383838"
        else:
            # --- LIGHT MODE PADRÃO ---
            c_fundo = "#e0e0e0"; c_fundo_alt = "#ffffff"; c_texto = "#1a1a1a"; c_texto_sec = "#555555"
            c_borda = "#b0b0b0"; c_borda_foco = "#505050"; c_azul = "#333333"; c_azul_fundo = "#d0d0d0"
            c_btn = "#e6e6e6"; c_btn_hover = "#d4d4d4"; c_header = "#d9d9d9"; c_selecao = "#606060"; c_texto_sel = "#ffffff"
            c_resumo_bg = "#f8f8f8"

        # Variáveis de Fonte e Borda
        s_font = f"{self.tamanho_fonte}px"
        s_borda_foco = "2px solid" if (self.tema_escuro or self.custom_bg) else "1px solid"

        # Atualiza labels manuais
        estilo_labels = f"color: {c_texto}; margin-bottom: 5px;"
        estilo_titulo = f"color: {c_texto_sec};"
        estilo_logo   = f"color: {c_texto}; margin-bottom: 20px; margin-top: 50px;"
        if hasattr(self, 'lbl_prestador'): self.lbl_prestador.setStyleSheet(estilo_labels)
        if hasattr(self, 'lbl_titulo'): self.lbl_titulo.setStyleSheet(estilo_titulo)
        if hasattr(self, 'lbl_logo'): self.lbl_logo.setStyleSheet(estilo_logo)

        # Palette do Qt (para popups padrão)
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(c_fundo))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(c_texto))
        palette.setColor(QPalette.ColorRole.Base, QColor(c_fundo_alt))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(c_fundo))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(c_texto))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(c_texto))
        palette.setColor(QPalette.ColorRole.Text, QColor(c_texto))
        palette.setColor(QPalette.ColorRole.Button, QColor(c_fundo))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(c_texto))
        palette.setColor(QPalette.ColorRole.Link, QColor(c_azul))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(c_selecao))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(c_texto_sel))
        app.setPalette(palette)

        # CSS Global Injetado
        estilo_css = f"""
        QMainWindow, QDialog {{ background-color: {c_fundo}; }}
        QWidget {{ color: {c_texto}; font-size: {s_font}; }}
        QLabel {{ color: {c_texto}; }}
        
        QGroupBox {{ border: 1px solid {c_borda}; border-radius: 6px; margin-top: 25px; font-weight: bold; }}
        QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 5px; color: {c_azul}; font-size: {int(self.tamanho_fonte)+2}px; font-weight: bold; }}

        QLineEdit, QDateEdit, QComboBox, QSpinBox {{ background-color: {c_fundo_alt}; border: 1px solid {c_borda}; border-radius: 4px; padding: 6px; color: {c_texto}; font-size: {s_font}; }}
        QLineEdit:focus, QDateEdit:focus, QComboBox:focus {{ border: {s_borda_foco} {c_borda_foco}; }}
        QLineEdit:disabled, QDateEdit:disabled {{ background-color: {c_fundo}; color: {c_texto_sec}; border: 1px solid {c_borda}; }}
        
        QTableWidget {{ background-color: {c_fundo_alt}; gridline-color: {c_borda}; border: 1px solid {c_borda}; color: {c_texto}; font-size: {s_font}; }}
        QHeaderView::section {{ background-color: {c_header}; color: {c_texto}; padding: 6px; border: 1px solid {c_borda}; font-weight: bold; font-size: {s_font}; }}
        QTableCornerButton::section {{ background-color: {c_header}; border: 1px solid {c_borda}; }}
        
        QPushButton {{ background-color: {c_btn}; border: 1px solid {c_borda}; border-radius: 4px; padding: 8px 16px; color: {c_texto}; font-weight: bold; font-size: {s_font}; }}
        QPushButton:hover {{ background-color: {c_btn_hover}; border: 1px solid {c_azul}; }}
        QPushButton:pressed {{ background-color: {c_azul}; color: {c_texto_sel}; }}
        
        QTabWidget::pane {{ border: 1px solid {c_borda}; background-color: {c_fundo}; }}
        QTabBar::tab {{ background-color: {c_fundo}; border: 1px solid {c_borda}; border-bottom: none; padding: 10px 20px; color: {c_texto_sec}; font-size: {int(self.tamanho_fonte)-1}px; }}
        QTabBar::tab:selected {{ background-color: {c_azul_fundo}; color: {c_azul}; font-weight: bold; border: 1px solid {c_borda}; border-bottom: 1px solid {c_azul_fundo}; }}
        
        QMenu {{ background-color: {c_fundo_alt}; border: 1px solid {c_borda}; }}
        QMenu::item {{ padding: 8px 25px; color: {c_texto}; }}
        QMenu::item:selected {{ background-color: {c_selecao}; color: {c_texto_sel}; }}
        """
        app.setStyleSheet(estilo_css)

    def abrir_aparencia(self):
        # Determina cores atuais para passar ao diálogo
        bg_atual = self.custom_bg if self.custom_bg else ("#2b2b2b" if self.tema_escuro else "#e0e0e0")
        sel_atual = self.custom_sel if self.custom_sel else ("#4da6ff" if self.tema_escuro else "#606060")
        
        dial = DialogoAparencia(bg_atual, sel_atual, self.tamanho_fonte, parent=self)
        if dial.exec():
            c_bg, c_sel, t_font = dial.get_dados()
            
            # Atualiza variáveis
            self.custom_bg = c_bg
            self.custom_sel = c_sel
            self.tamanho_fonte = t_font
            
            # Força tema escuro se estiver personalizando para garantir base correta
            # (Ou apenas aplica direto)
            self.aplicar_tema_visual()
            self.salvar_config()

    def salvar_ciclo_atual(self):
        if self.contrato_selecionado:
            id_atual = self.combo_ciclo_visualizacao.currentData()
            if id_atual is not None:
                self.contrato_selecionado.ultimo_ciclo_id = id_atual
                # Não chamamos salvar_dados() aqui para não ficar lento gravando disco a cada clique
                # O salvar_dados() será chamado ao fechar ou ao sair da tela.

    def init_ui(self):
        # --- CONFIGURAÇÃO DO ÍCONE ---
        caminho_script = os.path.dirname(os.path.abspath(__file__))
        caminho_icone = os.path.join(caminho_script, "icon_gc.png")
        if os.path.exists(caminho_icone):
            self.setWindowIcon(QIcon(caminho_icone))

        self.setWindowTitle("Gestão de Contratos")
        self.setGeometry(50, 50, 1300, 850)
        mb = self.menuBar()

        m_arq = mb.addMenu("Arquivo")

        m_arq.addAction("Trocar Base de Dados...", self.alternar_base_dados)
        m_arq.addSeparator()

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
        m_con.addSeparator()
        m_con.addAction("Histórico de Alterações (Auditoria)", self.abrir_auditoria)

        # --- NOVO MENU PRESTADORES (AO LADO DE CONTRATOS) ---
        m_pres = mb.addMenu("Prestadores")
        m_pres.addAction("Gerenciar Registro de Prestadores...", self.abrir_gestao_prestadores)
        # ----------------------------------------------------

        m_imp = mb.addMenu("Importação (Lote)")
        m_imp.addAction("Importar Prestadores (CSV)...", self.importar_prestadores)
        m_imp.addAction("Importar Contratos (CSV)...", self.importar_contratos)
        m_imp.addAction("Importar Serviços (CSV)...", self.importar_servicos)
        m_imp.addAction("Importar Empenhos (CSV)...", self.importar_empenhos)
        m_imp.addAction("Importar Pagamentos (CSV)...", self.importar_pagamentos)

        
        m_exi = mb.addMenu("Exibir")
        m_exi.addAction("Alternar Tema (Claro/Escuro)", self.alternar_tema)
        m_exi.addAction("Personalizar Aparência...", self.abrir_aparencia) # <--- NOVO
        m_exi.addSeparator()
        # m_exi.addAction("Histórico de Alterações (Auditoria)", self.abrir_auditoria)

        m_nuvem = mb.addMenu("Nuvem")
        m_nuvem.addAction("Sincronizar com Drive...", self.sincronizar_nuvem)

        m_ajuda = mb.addMenu("Ajuda")
        m_ajuda.addAction("Iniciar Tutorial Interativo", self.iniciar_tutorial_interativo)
        m_ajuda.addSeparator()
        m_ajuda.addAction("Manual do Sistema", self.abrir_manual)

        m_ajuda.addAction("Sobre", lambda: DarkMessageBox.info(self, "Sobre", "GC Gestor de Contratos - Versão 1.0\nDesenvolvido em Python/PyQt6\n\nAutor: Cássio de Souza Lopes\nServidor da Secretaria Municipal de Saúde de Montes Claros(MG) desde out/2017\nMestre em Desenvolvimento Social (Unimontes)\nBacharel em Economia (Unimontes\nGraduando em Análise e Desenvolvimento de Sistemas (UNINTER)\n\nGitHub: github.com/cassioslopes\nemail: cassio.souzza@gmail.ocm"))

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # --- PÁGINA 1: PESQUISA ---
        self.page_pesquisa = QWidget()
        layout_p = QVBoxLayout(self.page_pesquisa)
        layout_p.setAlignment(Qt.AlignmentFlag.AlignTop)

        # 1. BARRA SUPERIOR (TOP BAR) - BOTÕES NO CANTO DIREITO
        top_bar = QHBoxLayout()
        top_bar.addStretch() # Empurra tudo para a direita

        # Botão IA (Estilo Minimalista/Flat)
        btn_chat = QPushButton("💬 IA")
        btn_chat.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_chat.setToolTip("Perguntar à Inteligência Artificial")
        # Sem fundo, cor cinza discreta, fica roxo ao passar o mouse
        btn_chat.setStyleSheet("""
            QPushButton { border: none; background: transparent; font-size: 14px; color: #7f8c8d; font-weight: bold; padding: 5px; }
            QPushButton:hover { color: #8e44ad; background-color: #f0f0f0; border-radius: 5px; }
        """)
        btn_chat.clicked.connect(self.abrir_chat_ia)
        
        # Botão Notificações (Estilo Minimalista)
        self.btn_notificacoes = QPushButton("🔔")
        self.btn_notificacoes.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_notificacoes.setToolTip("Notificações e Alertas")
        self.btn_notificacoes.clicked.connect(self.abrir_notificacoes)
        # Inicialmente cinza discreto
        self.btn_notificacoes.setStyleSheet("""
            QPushButton { border: none; background: transparent; font-size: 16px; color: #7f8c8d; padding: 5px; }
            QPushButton:hover { background-color: #f0f0f0; border-radius: 5px; }
        """)

        top_bar.addWidget(btn_chat)
        top_bar.addSpacing(10)
        top_bar.addWidget(self.btn_notificacoes)
        top_bar.addSpacing(10) # Margem da borda direita

        layout_p.addLayout(top_bar) # Adiciona a barra no topo da página

        # 2. CONTAINER CENTRAL (LOGO + PESQUISA + TABELA)
        container = QFrame()
        # container.setFixedWidth(900) # (Opcional: Descomente se quiser limitar a largura do meio)
        l_cont = QVBoxLayout(container)

        # Logo
        self.lbl_logo = QLabel("Pesquisa de Contratos / Notas de Empenho / Prestadores")
        self.lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_logo.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.lbl_logo.setStyleSheet("color: #2c3e50; margin-bottom: 20px; margin-top: 10px")

        # Barra de Pesquisa
        self.inp_search = QLineEdit()
        self.inp_search.setPlaceholderText("Digite para pesquisar (Contrato, Prestador, CNPJ, Objeto)...")
        self.inp_search.setStyleSheet("font-size: 16px; padding: 10px; border: 1px solid #bdc3c7; border-radius: 5px;")
        self.inp_search.textChanged.connect(self.filtrar_contratos)

        # Tabela (Configuração das 8 colunas)
        self.tabela_resultados = QTableWidget()
        colunas = ["Número", "Prestador (Fantasia)", "Razão Social", "CNPJ", "CNES", "Cód. CP", "Objeto", "Status"]
        self.tabela_resultados.setColumnCount(len(colunas))
        self.tabela_resultados.setHorizontalHeaderLabels(colunas)
        
        header = self.tabela_resultados.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed); self.tabela_resultados.setColumnWidth(4, 80)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed); self.tabela_resultados.setColumnWidth(5, 80)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed); self.tabela_resultados.setColumnWidth(7, 90)

        self.tabela_resultados.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela_resultados.cellDoubleClicked.connect(self.abrir_contrato_pesquisa)
        self.tabela_resultados.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tabela_resultados.customContextMenuRequested.connect(self.menu_pesquisa)
        self.tabela_resultados.setSortingEnabled(True)

        # Adiciona tudo ao container central
        l_cont.addWidget(self.lbl_logo)
        l_cont.addWidget(self.inp_search)
        l_cont.addSpacing(15) # Espaço entre busca e tabela
        l_cont.addWidget(self.tabela_resultados)

        # Finaliza layout da página
        layout_p.addWidget(container)

        # --- PÁGINA 2: DETALHES ---
        self.page_detalhes = QWidget()
        self.layout_detalhes = QVBoxLayout(self.page_detalhes)

        top_bar = QHBoxLayout()
        btn_voltar = QPushButton("←")
        btn_voltar.setStyleSheet("font-size: 20px; padding: 7px; font-weight: bold; height: 15px; width: 20px;")
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

        top_bar.addWidget(btn_voltar);
        top_bar.addSpacing(20);
        top_bar.addLayout(header_text_layout);
        top_bar.addStretch()
        self.layout_detalhes.addLayout(top_bar)

        layout_filtro = QHBoxLayout()
        layout_filtro.setContentsMargins(0, 10, 0, 0)
        lbl_filtro = QLabel("Visualizar dados do Ciclo:")
        lbl_filtro.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.combo_ciclo_visualizacao = QComboBox()
        self.combo_ciclo_visualizacao.setFixedWidth(300)
        self.combo_ciclo_visualizacao.currentIndexChanged.connect(self.atualizar_painel_detalhes)
        self.combo_ciclo_visualizacao.currentIndexChanged.connect(self.salvar_ciclo_atual)

        layout_filtro.addWidget(lbl_filtro)
        layout_filtro.addWidget(self.combo_ciclo_visualizacao)
        layout_filtro.addStretch()
        self.layout_detalhes.addLayout(layout_filtro)

        self.abas = QTabWidget()
        self.layout_detalhes.addWidget(self.abas)

        # ABA 1: DADOS
        self.tab_dados = QWidget();
        l_dados = QFormLayout(self.tab_dados)
        self.lbl_d_licitacao = QLabel("-");
        self.lbl_d_dispensa = QLabel("-")
        self.lbl_d_vigencia = QLabel("-");
        self.lbl_d_comp = QLabel("-")

        self.tab_ciclos_resumo = TabelaExcel()
        self.tab_ciclos_resumo.setColumnCount(4)
        self.tab_ciclos_resumo.setHorizontalHeaderLabels(
            ["Ciclo / Período", "Teto Total", "Saldo de Pagamentos", "Valor Não Empenhado"])
        self.tab_ciclos_resumo.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tab_ciclos_resumo.setMinimumHeight(150)

        l_dados.addRow("Licitação:", self.lbl_d_licitacao);
        l_dados.addRow("Dispensa:", self.lbl_d_dispensa)
        l_dados.addRow("Vigência:", self.lbl_d_vigencia);
        l_dados.addRow("Competência:", self.lbl_d_comp)
        l_dados.addRow("Resumo Financeiro:", self.tab_ciclos_resumo)
        self.abas.addTab(self.tab_dados, "Dados")

        # ABA 2: FINANCEIRO
        tab_fin = QWidget();
        l_fin = QVBoxLayout(tab_fin)

        from PyQt6.QtWidgets import QGroupBox, QGridLayout
        self.grp_detalhes_ne = QGroupBox("Detalhes da Nota de Empenho Selecionada")
        self.grp_detalhes_ne.setMaximumHeight(100)
        layout_det_ne = QGridLayout(self.grp_detalhes_ne)

        self.lbl_ne_ciclo = QLabel("Ciclo: -");
        self.lbl_ne_emissao = QLabel("Emissão: -")
        self.lbl_ne_aditivo = QLabel("Aditivo: -");
        self.lbl_ne_desc = QLabel("Descrição: -");
        self.lbl_ne_desc.setWordWrap(True)

        font_bold = QFont("Arial", 9, QFont.Weight.Bold)
        for l in [self.lbl_ne_ciclo, self.lbl_ne_emissao, self.lbl_ne_aditivo, self.lbl_ne_desc]: l.setFont(font_bold)

        layout_det_ne.addWidget(self.lbl_ne_ciclo, 0, 0);
        layout_det_ne.addWidget(self.lbl_ne_emissao, 0, 1)
        layout_det_ne.addWidget(self.lbl_ne_aditivo, 0, 2);
        layout_det_ne.addWidget(self.lbl_ne_desc, 1, 0, 1, 3)
        l_fin.addWidget(self.grp_detalhes_ne)

        btns_fin = QHBoxLayout()
        b_ne = QPushButton("+ NE");
        b_ne.clicked.connect(self.dialogo_nova_ne)
        
        b_pg = QPushButton("Pagar");
        b_pg.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;") # Verde
        b_pg.clicked.connect(self.abrir_pagamento)
        
        # --- NOVO BOTÃO ANULAR ---
        b_anular = QPushButton("Anular");
        b_anular.setStyleSheet("background-color: #c0392b; color: white; font-weight: bold;") # Vermelho
        b_anular.clicked.connect(self.abrir_anulacao)
        # -------------------------

        # --- NOVO BOTÃO ANÁLISE ---
        b_analise = QPushButton("Analisar Risco (IA)");
        b_analise.setStyleSheet("background-color: #052c32; color: white; font-weight: bold;")
        b_analise.clicked.connect(self.abrir_analise_ia)
        
        btns_fin.addWidget(b_ne);
        btns_fin.addWidget(b_pg);
        btns_fin.addWidget(b_anular); 
        btns_fin.addWidget(b_analise); # Adiciona ao layout

        btns_fin.addWidget(b_ne);
        btns_fin.addWidget(b_pg);
        btns_fin.addWidget(b_anular); # Adiciona ao layout
        btns_fin.addStretch()
        l_fin.addLayout(btns_fin)

        self.tab_empenhos = TabelaExcel()
        self.tab_empenhos.setColumnCount(7)
        self.tab_empenhos.setHorizontalHeaderLabels(
            ["NE", "Fonte", "Serviço", "Valor Original", "Pago", "Saldo", "Média/mês (serviço)"])
        self.tab_empenhos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tab_empenhos.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tab_empenhos.itemClicked.connect(self.selecionar_ne)
        self.tab_empenhos.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tab_empenhos.customContextMenuRequested.connect(self.menu_empenho)
        l_fin.addWidget(self.tab_empenhos)

        # --- MUDANÇA AQUI: self.lbl_hist para poder alterar depois ---
        layout_hist_header = QHBoxLayout()
        self.lbl_hist = QLabel("Histórico Financeiro:") # <--- Tornou-se self
        self.lbl_hist.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        
        btn_max_hist = QPushButton("Maximizar Histórico")
        btn_max_hist.setFixedWidth(120)
        btn_max_hist.setStyleSheet("font-size: 11px; padding: 5px;")
        btn_max_hist.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_max_hist.clicked.connect(self.abrir_historico_maximizado)
        
        layout_hist_header.addWidget(self.lbl_hist)
        layout_hist_header.addStretch()
        layout_hist_header.addWidget(btn_max_hist)
        l_fin.addLayout(layout_hist_header)

        self.tab_mov = TabelaExcel()
        self.tab_mov.setColumnCount(4)
        self.tab_mov.setHorizontalHeaderLabels(["Competência", "Tipo", "Valor", "Saldo"])
        self.tab_mov.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tab_mov.setMaximumHeight(200)
        self.tab_mov.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tab_mov.customContextMenuRequested.connect(self.menu_movimentacao)
        l_fin.addWidget(self.tab_mov)

        self.abas.addTab(tab_fin, "Financeiro")

        # ABA 3: SERVIÇOS
        tab_serv = QWidget();
        l_serv = QVBoxLayout(tab_serv)
        b_nserv = QPushButton("+ Serviço")
        b_nserv.setFixedWidth(150)
        b_nserv.clicked.connect(self.abrir_novo_servico)
        l_serv.addWidget(b_nserv)

        self.tab_subcontratos = TabelaExcel()
        self.tab_subcontratos.setColumnCount(8)
        self.tab_subcontratos.setHorizontalHeaderLabels([
            "Descrição", "Valor Mensal", "Orçamento\n(neste ciclo)", "Empenhado", "Não Empenhado",
            "Total Pago", "Saldo de Empenhos", "Saldo Serviço"
        ])
        self.tab_subcontratos.cellDoubleClicked.connect(self.abrir_historico_servico)
        self.tab_subcontratos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tab_subcontratos.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tab_subcontratos.customContextMenuRequested.connect(self.menu_subcontrato)
        l_serv.addWidget(self.tab_subcontratos)
        self.abas.addTab(tab_serv, "Serviços")

        # ABA 4: ADITIVOS
        tab_adit = QWidget();
        l_adit = QVBoxLayout(tab_adit)
        b_nadit = QPushButton("+ Aditivo")
        b_nadit.setFixedWidth(150)
        b_nadit.clicked.connect(self.abrir_novo_aditivo)
        l_adit.addWidget(b_nadit)

        self.tab_aditivos = TabelaExcel()
        self.tab_aditivos.setColumnCount(6)
        self.tab_aditivos.setHorizontalHeaderLabels(
            ["Tipo", "Renova?", "Início Vigência", "Fim Vigência", "Valor", "Descrição"])
        self.tab_aditivos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tab_aditivos.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tab_aditivos.customContextMenuRequested.connect(self.menu_aditivo)
        l_adit.addWidget(self.tab_aditivos)
        self.abas.addTab(tab_adit, "Aditivos")

        # ABA 5: DETALHE GLOBAL
        self.painel_global = PainelDetalheGlobal()
        self.abas.addTab(self.painel_global, "Detalhe Contrato/Ciclo")

        self.stack.addWidget(self.page_pesquisa)
        self.stack.addWidget(self.page_detalhes)
        self.stack.setCurrentIndex(0)

    def abrir_auditoria(self):
        dial = DialogoAuditoria(self.db_logs, parent=self)
        dial.exec()


    # --- LÓGICA GERAL ---

    def voltar_para_pesquisa(self):
        self.salvar_dados()
        self.contrato_selecionado = None;
        self.ne_selecionada = None;
        self.inp_search.setText("");
        self.filtrar_contratos();
        self.stack.setCurrentIndex(0)

    def filtrar_contratos(self):
        texto = self.inp_search.text().lower()
        
        self.tabela_resultados.setSortingEnabled(False)
        self.tabela_resultados.setRowCount(0)
        
        def item_centro(txt):
            i = QTableWidgetItem(str(txt))
            i.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            return i

        # Mapa de prestadores para busca rápida
        mapa_prestadores = {}
        for p in self.db_prestadores:
            mapa_prestadores[p.nome_fantasia] = p
            mapa_prestadores[p.razao_social] = p

        # Função auxiliar atualizada para 8 colunas
        def preencher_linha(row, contrato_obj, objeto_texto, status_widget, ne_obj=None):
            # Coluna 0: Número
            texto_num = contrato_obj.numero
            if ne_obj: texto_num = f"NE {ne_obj.numero} (Ctr {contrato_obj.numero})"
            self.tabela_resultados.setItem(row, 0, item_centro(texto_num))
            
            # Busca dados do Prestador
            p_obj = mapa_prestadores.get(contrato_obj.prestador)
            razao = p_obj.razao_social if p_obj else "-" # <--- Pega Razão
            cnpj = p_obj.cnpj if p_obj else "-"
            cnes = p_obj.cnes if p_obj else "-"
            cod = p_obj.cod_cp if p_obj else "-"
            
            # Coluna 1: Prestador (Fantasia)
            self.tabela_resultados.setItem(row, 1, item_centro(contrato_obj.prestador))
            # Coluna 2: Razão Social (NOVA)
            self.tabela_resultados.setItem(row, 2, item_centro(razao))
            # Coluna 3: CNPJ
            self.tabela_resultados.setItem(row, 3, item_centro(cnpj))
            # Coluna 4: CNES
            self.tabela_resultados.setItem(row, 4, item_centro(cnes))
            # Coluna 5: Cód CP
            self.tabela_resultados.setItem(row, 5, item_centro(cod))
            # Coluna 6: Objeto
            self.tabela_resultados.setItem(row, 6, item_centro(objeto_texto))
            # Coluna 7: Status
            self.tabela_resultados.setItem(row, 7, status_widget)

        # LOOP PRINCIPAL DE BUSCA
        for c in self.db_contratos:
            # Verifica correspondência
            p_obj = mapa_prestadores.get(c.prestador)
            razao_busca = p_obj.razao_social.lower() if p_obj else ""
            cnpj_busca = p_obj.cnpj.lower() if p_obj else ""
            
            match_contrato = (texto in c.numero.lower() or 
                              texto in c.prestador.lower() or 
                              texto in c.descricao.lower() or
                              (texto in razao_busca and texto != "") or # Busca também na Razão
                              (texto in cnpj_busca and texto != ""))
            
            # A. Exibe Contrato
            if match_contrato or texto == "":
                row = self.tabela_resultados.rowCount()
                self.tabela_resultados.insertRow(row)
                
                # Status
                hoje = datetime.now()
                try:
                    fim = str_to_date(c.get_vigencia_final_atual())
                    st = "Vigente" if fim >= hoje else "Vencido"
                except: st = "Data Inválida"
                i_st = QTableWidgetItem(st)
                i_st.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                i_st.setForeground(QColor("green" if st == "Vigente" else "red"))
                
                preencher_linha(row, c, c.descricao, i_st)
                
                dados_linha = {"tipo": "CONTRATO", "obj": c}
                self.tabela_resultados.item(row, 0).setData(Qt.ItemDataRole.UserRole, dados_linha)

            # B. Exibe Notas de Empenho
            if texto != "":
                for ne in c.lista_notas_empenho:
                    if texto in ne.numero.lower() or texto in ne.descricao.lower():
                        row = self.tabela_resultados.rowCount()
                        self.tabela_resultados.insertRow(row)
                        
                        i_st = QTableWidgetItem("Empenho")
                        i_st.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        
                        preencher_linha(row, c, ne.descricao, i_st, ne_obj=ne)
                        
                        dados_linha = {"tipo": "NE", "obj": ne, "contrato": c}
                        self.tabela_resultados.item(row, 0).setData(Qt.ItemDataRole.UserRole, dados_linha)

        self.tabela_resultados.setSortingEnabled(True)

    def abrir_contrato_pesquisa(self, row, col):
        data = self.tabela_resultados.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        if not data: return
        
        if data["tipo"] == "CONTRATO":
            # Comportamento Padrão
            self.contrato_selecionado = data["obj"]
            self.ne_selecionada = None
            self.atualizar_painel_detalhes()
            self.stack.setCurrentIndex(1)
            self.abas.setCurrentIndex(0) # Aba Dados
            
        elif data["tipo"] == "NE":
            # Comportamento Inteligente (Vai direto para a NE)
            ne_alvo = data["obj"]
            contrato = data["contrato"]
            
            self.contrato_selecionado = contrato
            self.ne_selecionada = ne_alvo # Já deixa selecionada na memória
            
            # 1. Carrega a tela do contrato
            self.atualizar_painel_detalhes()
            self.stack.setCurrentIndex(1)
            
            # 2. Muda para a aba Financeiro (Índice 1)
            self.abas.setCurrentIndex(1)
            
            # 3. Seleciona visualmente a linha na tabela de empenhos
            # Precisamos achar em qual linha da tabela essa NE ficou
            for r in range(self.tab_empenhos.rowCount()):
                item = self.tab_empenhos.item(r, 0)
                ne_na_tabela = item.data(Qt.ItemDataRole.UserRole)
                
                if ne_na_tabela and ne_na_tabela.numero == ne_alvo.numero:
                    self.tab_empenhos.selectRow(r)
                    # Simula o clique para carregar o histórico financeiro lá embaixo
                    self.selecionar_ne(item)
                    break


    def menu_pesquisa(self, pos):
        item = self.tabela_resultados.itemAt(pos)
        if item:
            data = self.tabela_resultados.item(item.row(), 0).data(Qt.ItemDataRole.UserRole)
            
            menu = QMenu(self)
            
            # Ação de abrir funciona para ambos
            menu.addAction("Abrir Detalhes", lambda: self.abrir_contrato_pesquisa(item.row(), 0))
            
            # Edição/Exclusão só permitimos se for CONTRATO (para evitar confusão)
            if data["tipo"] == "CONTRATO":
                c = data["obj"]
                menu.addSeparator()
                menu.addAction("Editar Contrato", lambda: self.editar_contrato_externo(c))
                menu.addAction("Excluir Contrato", lambda: self.excluir_contrato_externo(c))
            
            menu.exec(self.tabela_resultados.mapToGlobal(pos))


    def abrir_novo_contrato(self):
        dial = DialogoCriarContrato(parent=self)
        
        # --- LÓGICA DO TUTORIAL ---
        if self.em_tutorial:
            dial.inp_numero.setText("999/2025")
            dial.inp_prestador.setText("Empresa Tutorial Ltda")
            dial.inp_desc.setText("Contrato de Exemplo para Aprendizado")
            dial.inp_valor.set_value(12000.00)
            dial.inp_licitacao.setText("Pregão 01/25")
            dial.setWindowTitle("Cadastro de Contrato (MODO TUTORIAL)")
        # --------------------------

        if dial.exec():
            dados = dial.get_dados()
            novo_c = Contrato(*dados)
            self.db_contratos.append(novo_c)
            self.registrar_log("Criar Contrato", f"Novo contrato criado: {novo_c.numero}")
            self.filtrar_contratos()
            self.salvar_dados()


    def editar_contrato_externo(self, c):
        dial = DialogoCriarContrato(contrato_editar=c, parent=self)
        if dial.exec():
            d = dial.get_dados()

            # Atualiza os dados básicos
            (c.numero, c.prestador, c.descricao,
             novo_valor_inicial,  # <--- Capturamos o novo valor aqui
             c.vigencia_inicio, c.vigencia_fim,
             c.comp_inicio, c.comp_fim,
             c.licitacao, c.dispensa) = d

            # Atualiza o valor no objeto Contrato
            c.valor_inicial = novo_valor_inicial

            # Atualiza também o valor base do Ciclo 0 (Contrato Inicial)
            if len(c.ciclos) > 0:
                c.ciclos[0].valor_base = novo_valor_inicial

            self.registrar_log("Editar Contrato", f"Alterou dados base do contrato {c.numero}")

            self.filtrar_contratos()
            self.salvar_dados()


    def excluir_contrato_externo(self, c):
        if DarkMessageBox.question(self, "Excluir", f"Excluir {c.numero}?") == QMessageBox.StandardButton.Yes:
            self.db_contratos.remove(c);
            self.filtrar_contratos();
            self.salvar_dados()

    def dialogo_nova_ne(self):
        if not self.contrato_selecionado: return
        if not self.contrato_selecionado.lista_servicos: DarkMessageBox.warning(self, "Aviso",
                                                                             "Cadastre um Serviço antes."); return
        dial = DialogoNovoEmpenho(self.contrato_selecionado, parent=self)

        # --- LÓGICA DO TUTORIAL ---
        if self.em_tutorial:
            dial.inp_num.setText("2025NE001")
            dial.inp_desc.setText("Empenho estimativo para manutenção")
            dial.inp_fonte.setText("1.500.000")
            dial.inp_val.set_value(5000.00)
            # Seleciona o primeiro serviço automaticamente
            if dial.combo_sub.count() > 0: dial.combo_sub.setCurrentIndex(0)
            dial.setWindowTitle("Nova NE (MODO TUTORIAL)")
        # --------------------------

        if dial.exec():
            num, desc, idx, val, fonte, data_em, id_ciclo, id_aditivo = dial.get_dados()
            nova_ne = NotaEmpenho(num, val, desc, idx, fonte, data_em, id_ciclo, id_aditivo)
            ok, msg = self.contrato_selecionado.adicionar_nota_empenho(nova_ne)
            if ok:
                self.registrar_log("Nova NE", f"NE {num} (R$ {fmt_br(val)}) adicionada ao contrato {self.contrato_selecionado.numero}")
                self.atualizar_painel_detalhes(); self.salvar_dados()
            else:
                DarkMessageBox.critical(self, "Bloqueio", msg)

    def abrir_pagamento(self):
        if not self.ne_selecionada:
            DarkMessageBox.warning(self, "Aviso", "Selecione uma Nota de Empenho primeiro.")
            return
        
        # Passa as datas do contrato para gerar a lista de meses
        dial = DialogoPagamento(self.contrato_selecionado.comp_inicio, self.contrato_selecionado.comp_fim, parent=self)
        
        if dial.exec():
            # Agora recebe 3 valores: Competencias (string), Valor e Obs
            comps_str, val, obs = dial.get_dados()
            
            ok, msg = self.ne_selecionada.realizar_pagamento(val, comps_str, obs)
            
            if not ok: 
                DarkMessageBox.warning(self, "Erro", msg)
            else:
                # --- AQUI: ADICIONANDO O LOG QUE FALTAVA ---
                self.registrar_log("Pagamento", f"Pagamento R$ {fmt_br(val)} na NE {self.ne_selecionada.numero}. Comp: {comps_str}")
                
            self.atualizar_painel_detalhes()
            self.atualizar_movimentos()
            self.salvar_dados()


    def abrir_historico_maximizado(self):
        if not self.ne_selecionada:
            DarkMessageBox.warning(self, "Aviso", "Selecione uma Nota de Empenho na tabela acima primeiro.")
            return
            
        dial = DialogoHistoricoMaximizado(self.ne_selecionada, parent=self)
        dial.exec()

    def abrir_anulacao(self):
        if not self.ne_selecionada:
            DarkMessageBox.warning(self, "Aviso", "Selecione uma Nota de Empenho primeiro.")
            return
        
        # Usa o novo diálogo simplificado (sem competência)
        dial = DialogoAnulacao(parent=self)
        
        if dial.exec():
            val, obs = dial.get_dados()
            
            if val <= 0:
                DarkMessageBox.warning(self, "Erro", "O valor deve ser maior que zero.")
                return

            # Chama o método de anulação (sem passar competência)
            ok, msg = self.ne_selecionada.realizar_anulacao(val, obs)
            
            if ok:
                self.registrar_log("Anulação", f"Anulou R$ {fmt_br(val)} na NE {self.ne_selecionada.numero}. Motivo: {obs}")
                
            self.atualizar_painel_detalhes()
            self.atualizar_movimentos()
            self.salvar_dados()

    def abrir_novo_servico(self):
        if not self.contrato_selecionado: return

        ciclo_atual_id = self.combo_ciclo_visualizacao.currentData() or 0

        # FILTRO: Só carrega ciclos que NÃO estão cancelados
        lista_ciclos = [(c.id_ciclo, c.nome) for c in self.contrato_selecionado.ciclos
                        if "(CANCELADO)" not in c.nome]

        dial = DialogoSubContrato(lista_ciclos, ciclo_atual_id, parent=self)

        # --- LÓGICA DO TUTORIAL ---
        if self.em_tutorial:
            dial.inp_desc.setText("Serviço de Manutenção Preventiva")
            dial.inp_mensal.set_value(1000.00)
            dial.inp_valor.set_value(12000.00) # Valor total anual
            dial.setWindowTitle("Serviço (MODO TUTORIAL)")
        # --------------------------

        if dial.exec():
            desc, val_total, val_mensal, replicar, id_ciclo_escolhido = dial.get_dados()

            sub = SubContrato(desc, val_mensal)

            if replicar:
                for c in self.contrato_selecionado.ciclos:
                    # Se for replicar, também evita jogar lixo nos cancelados
                    if "(CANCELADO)" not in c.nome:
                        sub.set_valor_ciclo(c.id_ciclo, val_total)
            else:
                sub.set_valor_ciclo(id_ciclo_escolhido, val_total)

            self.contrato_selecionado.lista_servicos.append(sub)

            if not replicar and id_ciclo_escolhido != ciclo_atual_id:
                idx_combo = self.combo_ciclo_visualizacao.findData(id_ciclo_escolhido)
                if idx_combo >= 0: self.combo_ciclo_visualizacao.setCurrentIndex(idx_combo)

            self.atualizar_painel_detalhes()
            self.salvar_dados()

    def abrir_novo_aditivo(self):
        if not self.contrato_selecionado: return

        # Captura o ID do ciclo atual (visualizado na combobox)
        ciclo_view_id = self.combo_ciclo_visualizacao.currentData()

        dial = DialogoAditivo(self.contrato_selecionado, parent=self)
        if dial.exec():
            tipo, valor, data_n, desc, renova, data_ini, serv_idx = dial.get_dados()
            adt = Aditivo(0, tipo, valor, data_n, desc, renova, data_ini, serv_idx)

            # Passamos o ciclo_view_id como destino
            msg = self.contrato_selecionado.adicionar_aditivo(adt, id_ciclo_alvo=ciclo_view_id)

            self.registrar_log("Novo Aditivo", f"Aditivo de {tipo} (R$ {fmt_br(valor)}) no contrato {self.contrato_selecionado.numero}")

            DarkMessageBox.info(self, "Aditivo", msg)
            self.atualizar_painel_detalhes()
            self.salvar_dados()

    # --- EXPORTAÇÃO E IMPORTAÇÃO ---

    def exportar_contrato_completo(self):
        if not self.contrato_selecionado: DarkMessageBox.warning(self, "Aviso", "Selecione um contrato."); return
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

            DarkMessageBox.info(self, "Sucesso", "Exportado com sucesso!")
        except Exception as e: DarkMessageBox.critical(self, "Erro", str(e))
    
    def exportar_ne_atual(self):
        if not self.ne_selecionada: DarkMessageBox.warning(self, "Aviso", "Selecione uma NE."); return
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
            DarkMessageBox.info(self, "Sucesso", "Exportado!")
        except Exception as e:
            DarkMessageBox.critical(self, "Erro", str(e))


    def importar_contratos(self):
        instrucao = "CSV (ponto e vírgula):\nNum;Prest;Obj;Valor;VigIni;VigFim;CompIni;CompFim;Lic;Disp"
        DarkMessageBox.info(self, "Instruções", instrucao)
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
            DarkMessageBox.info(self, "Sucesso", "Importado!")
        except Exception as e:
            DarkMessageBox.critical(self, "Erro", str(e))

    def importar_empenhos(self):
        if not self.contrato_selecionado: DarkMessageBox.warning(self, "Aviso", "Abra um contrato."); return
        instrucao = "CSV:\nNE;Valor;Desc;NomeServico;Fonte;Data"
        DarkMessageBox.info(self, "Instruções", instrucao)
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
            DarkMessageBox.info(self, "Sucesso", "Importado!")
        except Exception as e:
            DarkMessageBox.critical(self, "Erro", str(e))

    def importar_servicos(self):
        if not self.contrato_selecionado:
            DarkMessageBox.warning(self, "Aviso", "Selecione (abra) um contrato primeiro na tela de pesquisa.")
            return

        lista_ciclos = [c.nome for c in self.contrato_selecionado.ciclos]
        idx_padrao = len(lista_ciclos) - 1

        nome_ciclo, ok = QInputDialog.getItem(self, "Selecionar Ciclo",
                                              "Para qual ciclo financeiro estes valores pertencem?",
                                              lista_ciclos, idx_padrao, False)

        if not ok: return

        id_ciclo_alvo = 0
        for c in self.contrato_selecionado.ciclos:
            if c.nome == nome_ciclo:
                id_ciclo_alvo = c.id_ciclo
                break

        instrucao = (
            f"IMPORTANDO PARA: {nome_ciclo}\n\n"
            "ESTRUTURA DO CSV (Separador: ponto e vírgula ';')\n"
            "Colunas: Descrição; Valor Total; [Valor Mensal (Opcional)]"
        )
        DarkMessageBox.info(self, "Instruções", instrucao)

        fname, _ = QFileDialog.getOpenFileName(self, "Selecionar CSV Serviços", "", "Arquivos CSV (*.csv)")
        if not fname: return

        sucesso = 0
        try:
            with open(fname, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter=';')
                next(reader, None)
                for row in reader:
                    if len(row) < 2: continue

                    desc = row[0].strip()
                    val_total = parse_float_br(row[1])

                    # Tenta ler a 3ª coluna (Mensal), se não existir usa 0.0
                    val_mensal = 0.0
                    if len(row) > 2:
                        val_mensal = parse_float_br(row[2])

                    if desc:
                        # Passa o mensal na criação
                        sub = SubContrato(desc, 0.0, val_mensal)
                        sub.set_valor_ciclo(id_ciclo_alvo, val_total)

                        self.contrato_selecionado.lista_servicos.append(sub)
                        sucesso += 1

            idx_combo = self.combo_ciclo_visualizacao.findData(id_ciclo_alvo)
            if idx_combo >= 0: self.combo_ciclo_visualizacao.setCurrentIndex(idx_combo)

            self.atualizar_painel_detalhes()
            self.salvar_dados()
            DarkMessageBox.info(self, "Concluído", f"{sucesso} serviços importados para o ciclo '{nome_ciclo}'!")

        except Exception as e:
            DarkMessageBox.critical(self, "Erro", f"Erro na importação: {str(e)}")


    def importar_pagamentos(self):
        if not self.contrato_selecionado:
            DarkMessageBox.warning(self, "Aviso", "Selecione (abra) um contrato primeiro.")
            return

        instrucao = (
            "ESTRUTURA DO CSV PARA PAGAMENTOS (Separador: ponto e vírgula ';')\n\n"
            "O sistema buscará a Nota de Empenho pelo NÚMERO exato.\n"
            "Colunas necessárias:\n"
            "1. Número da NE (Deve já existir no contrato)\n"
            "2. Valor do Pagamento (ex: 500,00)\n"
            "3. Competência (MM/AAAA)\n"
        )
        DarkMessageBox.info(self, "Instruções", instrucao)

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

            DarkMessageBox.info(self, "Relatório", resumo)

        except Exception as e:
            DarkMessageBox.critical(self, "Erro", f"Erro na importação: {str(e)}")

    # --- MENUS CONTEXTO E AUXILIARES ---

    def selecionar_ne(self, item):
        self.ne_selecionada = self.tab_empenhos.item(item.row(), 0).data(Qt.ItemDataRole.UserRole)

        if self.ne_selecionada and self.contrato_selecionado:
            # (Código de labels de ciclo/emissão/aditivo mantém igual...)
            c = self.contrato_selecionado
            ne = self.ne_selecionada
            
            nome_ciclo = "?"
            for ciclo in c.ciclos:
                if ciclo.id_ciclo == ne.ciclo_id: nome_ciclo = ciclo.nome; break
            
            info_aditivo = "Não vinculado"
            if ne.aditivo_vinculado_id:
                for a in c.lista_aditivos:
                    if a.id_aditivo == ne.aditivo_vinculado_id: info_aditivo = f"{a.descricao} (ID {a.id_aditivo})"; break

            self.lbl_ne_ciclo.setText(f"Ciclo: {nome_ciclo}")
            self.lbl_ne_emissao.setText(f"Emissão: {ne.data_emissao}")
            self.lbl_ne_aditivo.setText(f"Aditivo: {info_aditivo}")
            self.lbl_ne_desc.setText(f"Descrição: {ne.descricao}")

            # --- CORREÇÃO DO TÍTULO VERDE ---
            if hasattr(self, 'lbl_hist'):
                # Usa a nova property .saldo_disponivel
                saldo = ne.saldo_disponivel
                
                info_nota = (f"NE {ne.numero} | {ne.descricao} | "
                             f"Valor: {fmt_br(ne.valor_inicial)} | "
                             f"<span style='color: #27ae60; font-weight: bold;'>Saldo: {fmt_br(saldo)}</span>")
                
                self.lbl_hist.setText(f"Histórico Financeiro: {info_nota}")

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
        if self.ne_selecionada and DarkMessageBox.question(self, "Confirma", "Excluir?") == QMessageBox.StandardButton.Yes:
            self.contrato_selecionado.lista_notas_empenho.remove(self.ne_selecionada);
            self.ne_selecionada = None;
            self.atualizar_painel_detalhes();
            self.salvar_dados()

    def menu_subcontrato(self, pos):
        item = self.tab_subcontratos.itemAt(pos)
        if item:
            # Pega a linha visual
            row_visual = item.row()
            # Pega o ID REAL do serviço (guardado na coluna 0)
            real_index = self.tab_subcontratos.item(row_visual, 0).data(Qt.ItemDataRole.UserRole)

            menu = QMenu(self)
            menu.addAction("Editar", lambda: self.editar_servico(real_index))
            menu.addAction("Excluir", lambda: self.excluir_servico(real_index))
            menu.addAction("Exportar", lambda: self.exportar_servico(real_index))
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
                DarkMessageBox.info(self, "Sucesso", "Serviço exportado!")
            except Exception as e: DarkMessageBox.critical(self, "Erro", str(e))

    def editar_servico(self, row):
        # Pega índice real oculto na tabela (segurança contra filtros)
        real_index = row  # Se vier do menu, já é o real. Se vier de clique duplo, cuidado.
        # Nota: O método menu_subcontrato já manda o 'real_index'.

        sub = self.contrato_selecionado.lista_servicos[real_index]
        ciclo_id = self.combo_ciclo_visualizacao.currentData() or 0

        # FILTRO AQUI TAMBÉM
        lista_ciclos = [(c.id_ciclo, c.nome) for c in self.contrato_selecionado.ciclos
                        if "(CANCELADO)" not in c.nome]

        valor_atual = sub.get_valor_ciclo(ciclo_id)

        dial = DialogoSubContrato(lista_ciclos, ciclo_id, sub_editar=sub, valor_editar=valor_atual, parent=self)
        dial.setWindowTitle(f"Editar Serviço")

        if dial.exec():
            desc, novo_valor, novo_mensal, replicar, _ = dial.get_dados()

            sub.descricao = desc
            sub.valor_mensal = novo_mensal

            if replicar:
                for c in self.contrato_selecionado.ciclos:
                    if "(CANCELADO)" not in c.nome:
                        sub.set_valor_ciclo(c.id_ciclo, novo_valor)
            else:
                sub.set_valor_ciclo(ciclo_id, novo_valor)

            self.atualizar_painel_detalhes()
            self.salvar_dados()

    def abrir_historico_servico(self, row, col):
        if not self.contrato_selecionado: return

        # Pega o índice real, pois a tabela pode estar filtrada
        real_index = self.tab_subcontratos.item(row, 0).data(Qt.ItemDataRole.UserRole)

        sub = self.contrato_selecionado.lista_servicos[real_index]
        ciclo_view_id = self.combo_ciclo_visualizacao.currentData() or 0

        # Pega as datas corretas do ciclo para desenhar as colunas
        ciclo = next((c for c in self.contrato_selecionado.ciclos if c.id_ciclo == ciclo_view_id), None)
        if ciclo:
            dt_ini = ciclo.inicio if hasattr(ciclo, 'inicio') and ciclo.inicio else self.contrato_selecionado.comp_inicio
            dt_fim = ciclo.fim if hasattr(ciclo, 'fim') and ciclo.fim else self.contrato_selecionado.comp_fim
        else:
            # Fallback seguro
            dt_ini = self.contrato_selecionado.comp_inicio
            dt_fim = self.contrato_selecionado.comp_fim

        # Filtra apenas as NEs deste serviço e deste ciclo
        lista_nes = [ne for ne in self.contrato_selecionado.lista_notas_empenho
                     if ne.subcontrato_idx == real_index and ne.ciclo_id == ciclo_view_id]

        # Chama a nova versão da janela (Maximizada e com ícones)
        dial = DialogoDetalheServico(sub, lista_nes, dt_ini, dt_fim, ciclo_id=ciclo_view_id, parent=self)
        dial.exec()


    def excluir_servico(self, row):
        # 1. Identificar o serviço e o ciclo atual
        # (Usamos o índice real escondido na tabela para garantir segurança)
        sub = self.contrato_selecionado.lista_servicos[row]
        ciclo_atual_id = self.combo_ciclo_visualizacao.currentData() or 0

        # 2. Bloqueio: Tem NEs NESTE ciclo? (Se tiver, não pode remover daqui)
        # Se tiver NE em OUTROS ciclos, não tem problema, pois vamos preservar o histórico lá.
        tem_ne_neste_ciclo = any(ne.subcontrato_idx == row and ne.ciclo_id == ciclo_atual_id
                                 for ne in self.contrato_selecionado.lista_notas_empenho)

        if tem_ne_neste_ciclo:
            DarkMessageBox.warning(self, "Bloqueado",
                                "Este serviço possui Notas de Empenho neste ciclo.\n"
                                "Não é possível removê-lo enquanto houver movimentação financeira.")
            return

        # 3. Verificação: Existe em OUTROS ciclos?
        # Verifica se existe algum valor gravado em chaves diferentes do ciclo atual
        tem_historico = any(cid != ciclo_atual_id for cid in sub.valores_por_ciclo.keys())

        # 4. Tomada de Decisão
        if tem_historico:
            msg = (f"O serviço '{sub.descricao}' possui histórico em OUTROS ciclos financeiros.\n\n"
                   "O que deseja fazer?")

            btns = QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            # MUDANÇA AQUI: Instancia DarkMessageBox em vez de QMessageBox
            box = DarkMessageBox(parent=self) 
            box.setIcon(QMessageBox.Icon.Question)
            box.setWindowTitle("Excluir Serviço")
            box.setText(msg)
            box.setStandardButtons(btns)
            box.setButtonText(QMessageBox.StandardButton.Yes, "Remover DESTE Ciclo (Manter Histórico)")
            box.setButtonText(QMessageBox.StandardButton.No, "Apagar de TODOS (Exclusão Total)")
            box.setButtonText(QMessageBox.StandardButton.Cancel, "Cancelar")

            resp = box.exec()

            if resp == QMessageBox.StandardButton.Cancel:
                return

            if resp == QMessageBox.StandardButton.Yes:
                # OPÇÃO A: Remove apenas a chave deste ciclo
                # O filtro da tabela vai esconder o serviço automaticamente porque ele não terá valor aqui
                if ciclo_atual_id in sub.valores_por_ciclo:
                    del sub.valores_por_ciclo[ciclo_atual_id]

                self.atualizar_painel_detalhes()
                self.salvar_dados()
                return

            # Se for 'No', cai no código abaixo (Exclusão Total)

        # 5. Exclusão Total (Apaga do Contrato)

        # Antes, verifica se tem NEs em QUALQUER lugar (já que vamos apagar tudo)
        for ne in self.contrato_selecionado.lista_notas_empenho:
            if ne.subcontrato_idx == row:
                DarkMessageBox.warning(self, "Bloqueado",
                                    "Para exclusão TOTAL, não pode haver nenhuma NE em nenhum ciclo.\n"
                                    "Encontrei movimentação em outros períodos.")
                return

        # Confirmação final
        if DarkMessageBox.question(self, "Confirmar", "Tem a certeza que deseja apagar permanentemente?",
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:

            # Reindexação (Atualiza índices das NEs e Aditivos de outros serviços)
            for ne in self.contrato_selecionado.lista_notas_empenho:
                if ne.subcontrato_idx > row: ne.subcontrato_idx -= 1

            for adt in self.contrato_selecionado.lista_aditivos:
                if adt.servico_idx > row: adt.servico_idx -= 1

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
        adt = self.contrato_selecionado.lista_aditivos[row]
        id_original = adt.id_aditivo

        # Guardamos os dados ANTIGOS para poder desfazer a soma no serviço
        old_tipo = adt.tipo
        old_valor = adt.valor
        old_serv_idx = adt.servico_idx
        old_ciclo_id = adt.ciclo_pertencente_id

        dial = DialogoAditivo(self.contrato_selecionado, aditivo_editar=adt, parent=self)
        if dial.exec():
            tipo, valor, data_n, desc, renova, data_ini, new_serv_idx = dial.get_dados()

            # --- PASSO A: DESFAZER O IMPACTO ANTIGO NO SERVIÇO ---
            if old_tipo == "Valor" and old_serv_idx >= 0 and old_ciclo_id != -1:
                if old_serv_idx < len(self.contrato_selecionado.lista_servicos):
                    sub_old = self.contrato_selecionado.lista_servicos[old_serv_idx]
                    val_atual_old = sub_old.get_valor_ciclo(old_ciclo_id)
                    # Subtrai o valor antigo
                    sub_old.set_valor_ciclo(old_ciclo_id, val_atual_old - old_valor)

            # --- PASSO B: LIMPEZA DOS CICLOS (Remove da lista geral de soma) ---
            for c in self.contrato_selecionado.ciclos:
                c.aditivos_valor = [a for a in c.aditivos_valor if a.id_aditivo != id_original]

            # --- PASSO C: ATUALIZAR O OBJETO ---
            adt.tipo = tipo
            adt.valor = valor
            adt.data_nova = data_n
            adt.descricao = desc
            adt.renovacao_valor = renova
            adt.data_inicio_vigencia = data_ini
            adt.servico_idx = new_serv_idx

            # --- PASSO D: REAPLICAR NOVO IMPACTO ---
            if adt.renovacao_valor and adt.ciclo_pertencente_id != -1:
                for c in self.contrato_selecionado.ciclos:
                    if c.id_ciclo == adt.ciclo_pertencente_id:
                        c.valor_base = adt.valor;
                        break

            elif adt.tipo == "Valor":
                # Acha o ciclo correto (ou o último válido)
                ciclo_alvo = next(
                    (c for c in self.contrato_selecionado.ciclos if c.id_ciclo == adt.ciclo_pertencente_id), None)
                if not ciclo_alvo or "(CANCELADO)" in ciclo_alvo.nome:
                    ciclo_alvo = next(
                        (c for c in reversed(self.contrato_selecionado.ciclos) if "(CANCELADO)" not in c.nome),
                        self.contrato_selecionado.ciclos[0])
                    adt.ciclo_pertencente_id = ciclo_alvo.id_ciclo  # Atualiza vínculo

                # Adiciona na soma geral do ciclo
                ciclo_alvo.aditivos_valor.append(adt)

                # --- APLICA NOVO VALOR AO SERVIÇO ---
                if adt.servico_idx >= 0 and adt.servico_idx < len(self.contrato_selecionado.lista_servicos):
                    sub_new = self.contrato_selecionado.lista_servicos[adt.servico_idx]
                    val_atual_new = sub_new.get_valor_ciclo(adt.ciclo_pertencente_id)
                    # Soma o novo valor
                    sub_new.set_valor_ciclo(adt.ciclo_pertencente_id, val_atual_new + adt.valor)

            self.salvar_dados()
            self.atualizar_painel_detalhes()

    def excluir_aditivo(self, row):
        adt = self.contrato_selecionado.lista_aditivos[row]
        id_alvo = adt.id_aditivo

        # 1. Verificação de Ciclo de Renovação (Mantém a proteção existente)
        if adt.renovacao_valor and adt.ciclo_pertencente_id != -1:
            tem_ne = any(
                ne.ciclo_id == adt.ciclo_pertencente_id for ne in self.contrato_selecionado.lista_notas_empenho)
            if tem_ne:
                DarkMessageBox.warning(self, "Bloqueado", "Ciclo com NEs. Exclua as NEs antes.")
                return
            for c in self.contrato_selecionado.ciclos:
                if c.id_ciclo == adt.ciclo_pertencente_id:
                    c.valor_base = 0.0;
                    c.nome += " (CANCELADO)";
                    break

        # 2. ESTORNO NO SERVIÇO (A CORREÇÃO ESTÁ AQUI)
        # Se for um aditivo de Valor e estiver vinculado a um serviço, subtrai o valor dele do serviço
        if adt.tipo == "Valor" and adt.servico_idx >= 0 and adt.ciclo_pertencente_id != -1:
            if adt.servico_idx < len(self.contrato_selecionado.lista_servicos):
                sub = self.contrato_selecionado.lista_servicos[adt.servico_idx]
                valor_atual = sub.get_valor_ciclo(adt.ciclo_pertencente_id)
                # Remove o valor do aditivo do saldo do serviço
                sub.set_valor_ciclo(adt.ciclo_pertencente_id, valor_atual - adt.valor)

        # 3. Limpeza Geral dos Ciclos
        for c in self.contrato_selecionado.ciclos:
            c.aditivos_valor = [a for a in c.aditivos_valor if a.id_aditivo != id_alvo]

        # 4. Apaga
        del self.contrato_selecionado.lista_aditivos[row]

        self.salvar_dados()
        self.atualizar_painel_detalhes()

    def menu_movimentacao(self, pos):
        item = self.tab_mov.itemAt(pos)
        if item:
            row = item.row()
            tipo = self.ne_selecionada.historico[row].tipo
            
            # Agora permite editar Pagamento OU Anulação
            if tipo in ["Pagamento", "Anulação"]:
                menu = QMenu(self)
                menu.addAction("Editar", lambda: self.editar_pagamento(row))
                menu.addAction("Excluir", lambda: self.excluir_pagamento(row))
                menu.exec(self.tab_mov.mapToGlobal(pos))

    def editar_pagamento(self, row):
        mov = self.ne_selecionada.historico[row]
        
        # Lógica diferente dependendo do tipo
        if mov.tipo == "Anulação":
            # Abre diálogo de Anulação (menor, sem data)
            dial = DialogoAnulacao(editar_valor=mov.valor, editar_obs=mov.observacao, parent=self)
            if dial.exec():
                v, obs = dial.get_dados()
                # Anulação não tem competência, passamos "-"
                ok, m = self.ne_selecionada.editar_movimentacao(row, v, "-", obs)
                if ok:
                    self.registrar_log("Editar Anulação", f"Editou anulação na NE {self.ne_selecionada.numero}.")
                    self.atualizar_painel_detalhes(); self.atualizar_movimentos(); self.salvar_dados()
                else:
                    DarkMessageBox.warning(self, "Erro", m)
        
        else:
            # Abre diálogo de Pagamento (com data)
            dial = DialogoPagamento(self.contrato_selecionado.comp_inicio, self.contrato_selecionado.comp_fim,
                                    pg_editar=mov, parent=self)
            if dial.exec():
                c, v, obs = dial.get_dados()
                ok, m = self.ne_selecionada.editar_movimentacao(row, v, c, obs)
                if ok:
                    self.registrar_log("Editar Pagamento", f"Editou pgto na NE {self.ne_selecionada.numero}.")
                    self.atualizar_painel_detalhes(); self.atualizar_movimentos(); self.salvar_dados()
                else:
                    DarkMessageBox.warning(self, "Erro", m)

    def excluir_pagamento(self, row):
        mov = self.ne_selecionada.historico[row]
        tipo = mov.tipo
        valor_apagado = mov.valor
        
        if self.ne_selecionada.excluir_movimentacao(row): 
            self.registrar_log(f"Excluir {tipo}", f"Excluiu {tipo} de R$ {fmt_br(abs(valor_apagado))} da NE {self.ne_selecionada.numero}")
            
            self.atualizar_painel_detalhes(); 
            self.atualizar_movimentos(); 
            self.salvar_dados()

    def atualizar_movimentos(self):
        if not self.ne_selecionada: return
        self.tab_mov.setRowCount(0)
        
        self.tab_mov.setColumnCount(5) 
        self.tab_mov.setHorizontalHeaderLabels(["Competência", "Tipo", "Valor", "Saldo", "Obs."])
        self.tab_mov.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)

        saldo_corrente = self.ne_selecionada.valor_inicial
        fonte_negrito = QFont(); fonte_negrito.setBold(True)
        fonte_pequena = QFont(); fonte_pequena.setPointSize(8); fonte_pequena.setBold(True)

        for row, m in enumerate(self.ne_selecionada.historico):
            self.tab_mov.insertRow(row)

            # --- LÓGICA DO SALDO VISUAL ---
            if m.tipo == "Pagamento":
                saldo_corrente -= m.valor # Paga, diminui saldo
            elif m.tipo == "Anulação":
                saldo_corrente -= abs(m.valor) # Anula, também diminui saldo (corta a nota)

            item_comp = QTableWidgetItem(m.competencia)
            item_tipo = QTableWidgetItem(m.tipo)
            item_valor = QTableWidgetItem(fmt_br(m.valor))
            item_saldo = QTableWidgetItem(fmt_br(saldo_corrente))

            if m.tipo == "Anulação":
                item_tipo.setForeground(QColor("#c0392b"))
                item_valor.setForeground(QColor("#c0392b"))
            elif m.tipo == "Pagamento":
                item_valor.setForeground(QColor("black"))
            
            txt_obs = m.observacao
            if m.tipo == "Emissão Original":
                nome_serv = "?"
                if 0 <= self.ne_selecionada.subcontrato_idx < len(self.contrato_selecionado.lista_servicos):
                    nome_serv = self.contrato_selecionado.lista_servicos[self.ne_selecionada.subcontrato_idx].descricao
                txt_obs = f"Serv: {nome_serv} | Fonte: {self.ne_selecionada.fonte_recurso} | {self.ne_selecionada.descricao}"

            item_obs = QTableWidgetItem(txt_obs)

            for i in [item_comp, item_tipo, item_valor, item_saldo]:
                i.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            item_saldo.setForeground(QColor("#27ae60"))

            if m.tipo == "Emissão Original":
                for i in [item_comp, item_tipo, item_valor, item_saldo]: i.setFont(fonte_negrito)
                item_obs.setFont(fonte_pequena)

            self.tab_mov.setItem(row, 0, item_comp)
            self.tab_mov.setItem(row, 1, item_tipo)
            self.tab_mov.setItem(row, 2, item_valor)
            self.tab_mov.setItem(row, 3, item_saldo)
            self.tab_mov.setItem(row, 4, item_obs)

    def atualizar_painel_detalhes(self):
        if not self.contrato_selecionado: return
        c = self.contrato_selecionado

        # --- ATUALIZAÇÃO DOS CAMPOS DE TEXTO ---
        self.lbl_prestador.setText(c.prestador)
        self.lbl_titulo.setText(f"{c.numero} - {c.descricao}")
        self.lbl_d_licitacao.setText(c.licitacao)
        self.lbl_d_dispensa.setText(c.dispensa)
        self.lbl_d_vigencia.setText(f"{c.vigencia_inicio} a {c.get_vigencia_final_atual()}")

        # Competência Geral
        comp_final_geral = c.comp_fim
        if len(c.ciclos) > 1:
            ultimo_adt_prazo = next((a for a in reversed(c.lista_aditivos)
                                     if a.tipo == "Prazo" and a.renovacao_valor), None)
            if ultimo_adt_prazo:
                try:
                    parts = ultimo_adt_prazo.data_nova.split('/')
                    if len(parts) == 3: comp_final_geral = f"{parts[1]}/{parts[2]}"
                except:
                    pass
        self.lbl_d_comp.setText(f"{c.comp_inicio} a {comp_final_geral}")

        # --- TABELA RESUMO (ABA DADOS) ---
        self.tab_ciclos_resumo.setRowCount(0)

        def extrair_comp(data_str):
            try:
                parts = data_str.split('/')
                if len(parts) == 3: return f"{parts[1]}/{parts[2]}"
                return data_str
            except:
                return "?"

        def item_centro(txt):
            i = QTableWidgetItem(str(txt));
            i.setTextAlignment(Qt.AlignmentFlag.AlignCenter);
            return i

        for ciclo in c.ciclos:
            if "(CANCELADO)" in ciclo.nome: continue
            periodo_str = ""
            if ciclo.id_ciclo == 0:
                periodo_str = f"[{c.comp_inicio} a {c.comp_fim}]"
            else:
                adt_gerador = next((a for a in c.lista_aditivos
                                    if a.ciclo_pertencente_id == ciclo.id_ciclo and a.renovacao_valor), None)
                if adt_gerador:
                    inicio = extrair_comp(adt_gerador.data_inicio_vigencia)
                    fim = extrair_comp(adt_gerador.data_nova)
                    periodo_str = f"[{inicio} a {fim}]"

            teto = ciclo.get_teto_total()
            
            # --- CÁLCULO CORRIGIDO PARA O RESUMO ---
            total_empenhado_ciclo = sum(ne.valor_inicial for ne in c.lista_notas_empenho if ne.ciclo_id == ciclo.id_ciclo)
            
            total_pago_ciclo = 0.0
            total_anulado_ciclo = 0.0
            
            for ne in c.lista_notas_empenho:
                if ne.ciclo_id == ciclo.id_ciclo:
                    for mov in ne.historico:
                        if mov.tipo == "Pagamento":
                            total_pago_ciclo += mov.valor
                        elif mov.tipo == "Anulação":
                            total_anulado_ciclo += abs(mov.valor) # Soma como positivo para abater depois

            # Valor Não Empenhado = Teto do Ciclo - (Empenhos - Anulações de Saldo)
            # Se a anulação reduz o empenho, ela libera saldo no ciclo.
            valor_nao_empenhado = teto - (total_empenhado_ciclo - total_anulado_ciclo)
            
            # Saldo de Pagamentos = O que tenho de contrato - O que paguei
            saldo_pagamentos = teto - total_pago_ciclo

            row = self.tab_ciclos_resumo.rowCount()
            self.tab_ciclos_resumo.insertRow(row)
            self.tab_ciclos_resumo.setItem(row, 0, item_centro(f"{ciclo.nome}  {periodo_str}"))
            self.tab_ciclos_resumo.setItem(row, 1, item_centro(fmt_br(teto)))
            
            item_sp = item_centro(fmt_br(saldo_pagamentos))
            item_sp.setForeground(QColor("#2980b9"))
            self.tab_ciclos_resumo.setItem(row, 2, item_sp)

            item_vne = item_centro(fmt_br(valor_nao_empenhado))
            item_vne.setForeground(QColor("#27ae60"))
            self.tab_ciclos_resumo.setItem(row, 3, item_vne)

        # --- SELETOR (COMBOBOX) ---
        id_selecionado = self.combo_ciclo_visualizacao.currentData()
        if id_selecionado is None and c.ultimo_ciclo_id is not None:
            id_selecionado = c.ultimo_ciclo_id
        self.combo_ciclo_visualizacao.blockSignals(True)
        self.combo_ciclo_visualizacao.clear()

        for ciclo in c.ciclos:
            if "(CANCELADO)" in ciclo.nome: continue
            self.combo_ciclo_visualizacao.addItem(ciclo.nome, ciclo.id_ciclo)

        idx = self.combo_ciclo_visualizacao.findData(id_selecionado)
        if idx >= 0: self.combo_ciclo_visualizacao.setCurrentIndex(idx)
        elif self.combo_ciclo_visualizacao.count() > 0:
            self.combo_ciclo_visualizacao.setCurrentIndex(self.combo_ciclo_visualizacao.count() - 1)
        self.combo_ciclo_visualizacao.blockSignals(False)

        ciclo_view_id = self.combo_ciclo_visualizacao.currentData() or 0

        # --- CÁLCULO DE MÉDIAS ---
        medias_por_servico = {}
        for idx_serv, sub in enumerate(c.lista_servicos):
            nes_do_servico = [n for n in c.lista_notas_empenho if n.subcontrato_idx == idx_serv and n.ciclo_id == ciclo_view_id]
            
            total_pago_bruto = 0.0
            competencias_pagas = set()
            
            for n in nes_do_servico:
                for mov in n.historico:
                    if mov.tipo == "Pagamento":
                        total_pago_bruto += mov.valor
                        if mov.competencia and mov.competencia != "-":
                            partes = [p.strip() for p in mov.competencia.split(',') if p.strip()]
                            for p in partes:
                                competencias_pagas.add(p)
            
            medias_por_servico[idx_serv] = total_pago_bruto / len(competencias_pagas) if competencias_pagas else 0.0

        # --- TABELA EMPENHOS ---
        self.tab_empenhos.setRowCount(0);
        self.tab_mov.setRowCount(0)
        self.lbl_ne_ciclo.setText("Ciclo: -"); self.lbl_ne_emissao.setText("Emissão: -");
        self.lbl_ne_aditivo.setText("Aditivo: -"); self.lbl_ne_desc.setText("Selecione uma NE...")
        
        if hasattr(self, 'lbl_hist'): self.lbl_hist.setText("Histórico Financeiro:")

        for row, ne in enumerate(c.lista_notas_empenho):
            if ne.ciclo_id != ciclo_view_id: continue
            new_row = self.tab_empenhos.rowCount();
            self.tab_empenhos.insertRow(new_row)
            n_serv = c.lista_servicos[ne.subcontrato_idx].descricao if 0 <= ne.subcontrato_idx < len(c.lista_servicos) else "?"
            
            # Recálculo local para garantir integridade visual
            val_pago_ne = sum(m.valor for m in ne.historico if m.tipo == "Pagamento")
            val_anulado_ne = sum(abs(m.valor) for m in ne.historico if m.tipo == "Anulação")
            saldo_ne = ne.valor_inicial - val_anulado_ne - val_pago_ne

            self.tab_empenhos.setItem(new_row, 0, item_centro(ne.numero))
            self.tab_empenhos.setItem(new_row, 1, item_centro(ne.fonte_recurso))
            self.tab_empenhos.setItem(new_row, 2, item_centro(n_serv))
            self.tab_empenhos.setItem(new_row, 3, item_centro(fmt_br(ne.valor_inicial)))
            self.tab_empenhos.setItem(new_row, 4, item_centro(fmt_br(val_pago_ne))) # Mostra apenas Pagamento Positivo
            
            i_s = QTableWidgetItem(fmt_br(saldo_ne))
            i_s.setTextAlignment(Qt.AlignmentFlag.AlignCenter); i_s.setForeground(QColor("#27ae60"))
            self.tab_empenhos.setItem(new_row, 5, i_s)
            
            media_servico = medias_por_servico.get(ne.subcontrato_idx, 0.0)
            self.tab_empenhos.setItem(new_row, 6, item_centro(fmt_br(media_servico)))
            self.tab_empenhos.item(new_row, 0).setData(Qt.ItemDataRole.UserRole, ne)

        # --- TABELA SERVIÇOS ---
        self.tab_subcontratos.setRowCount(0)
        font_bold = QFont(); font_bold.setBold(True)

        for idx_real, sub in enumerate(c.lista_servicos):
            tem_ne_neste_ciclo = any(ne.subcontrato_idx == idx_real and ne.ciclo_id == ciclo_view_id for ne in c.lista_notas_empenho)
            if ciclo_view_id not in sub.valores_por_ciclo and not tem_ne_neste_ciclo: continue

            valor_ciclo = sub.get_valor_ciclo(ciclo_view_id); val_mensal = sub.valor_mensal
            
            # Variáveis acumuladoras do serviço
            gasto_empenhado = 0.0
            gasto_pago = 0.0
            total_anulado_serv = 0.0
            
            for ne in c.lista_notas_empenho:
                if ne.subcontrato_idx == idx_real and ne.ciclo_id == ciclo_view_id:
                    gasto_empenhado += ne.valor_inicial
                    # Soma histórico da NE
                    for mov in ne.historico:
                        if mov.tipo == "Pagamento":
                            gasto_pago += mov.valor
                        elif mov.tipo == "Anulação":
                            total_anulado_serv += abs(mov.valor)

            # LÓGICA DE SALDO DO SERVIÇO:
            # 1. Saldo a Empenhar = Orçamento - (O que empenhei - O que cancelei do empenho)
            #    Se anulei, o empenho "líquido" diminuiu, logo volta saldo pro serviço.
            saldo_a_empenhar = valor_ciclo - (gasto_empenhado - total_anulado_serv)

            # 2. Saldo das NEs = (Empenhos - Anulações) - Pagos
            #    Dinheiro que está preso nas notas aguardando pagamento
            saldo_das_nes = (gasto_empenhado - total_anulado_serv) - gasto_pago
            
            # 3. Saldo do Serviço (Caixa) = Orçamento - Pagos
            saldo_real_caixa = valor_ciclo - gasto_pago

            new_row_idx = self.tab_subcontratos.rowCount();
            self.tab_subcontratos.insertRow(new_row_idx)
            
            item_desc = item_centro(sub.descricao); item_desc.setData(Qt.ItemDataRole.UserRole, idx_real)
            self.tab_subcontratos.setItem(new_row_idx, 0, item_desc)
            self.tab_subcontratos.setItem(new_row_idx, 1, item_centro(fmt_br(val_mensal)))
            self.tab_subcontratos.setItem(new_row_idx, 2, item_centro(fmt_br(valor_ciclo)))
            
            # Coluna "Empenhado" mostra o valor BRUTO das notas criadas
            self.tab_subcontratos.setItem(new_row_idx, 3, item_centro(fmt_br(gasto_empenhado)))
            
            # Coluna "Não Empenhado" (Livre para novas notas)
            i_s1 = QTableWidgetItem(fmt_br(saldo_a_empenhar))
            i_s1.setTextAlignment(Qt.AlignmentFlag.AlignCenter); i_s1.setForeground(QColor("#A401F0")) 
            self.tab_subcontratos.setItem(new_row_idx, 4, i_s1)
            
            # Coluna "Total Pago" (Apenas pagamentos positivos)
            i_pg = QTableWidgetItem(fmt_br(gasto_pago))
            i_pg.setTextAlignment(Qt.AlignmentFlag.AlignCenter); i_pg.setForeground(QColor("#099453")); i_pg.setFont(font_bold)
            self.tab_subcontratos.setItem(new_row_idx, 5, i_pg)
            
            # Coluna "Saldo de Empenhos" (Dinheiro sobrando nas notas)
            i_s2 = QTableWidgetItem(fmt_br(saldo_das_nes))
            i_s2.setTextAlignment(Qt.AlignmentFlag.AlignCenter); i_s2.setForeground(QColor("#3dae27"))
            self.tab_subcontratos.setItem(new_row_idx, 6, i_s2)
            
            # Coluna "Saldo Serviço" (O que resta do contrato todo)
            i_s3 = QTableWidgetItem(fmt_br(saldo_real_caixa))
            i_s3.setTextAlignment(Qt.AlignmentFlag.AlignCenter); i_s3.setForeground(QColor("#39379e")); i_s3.setFont(font_bold)
            self.tab_subcontratos.setItem(new_row_idx, 7, i_s3)

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

        # --- ATUALIZA O NOVO PAINEL ---
        self.painel_global.carregar_dados(c, ciclo_view_id)

    def abrir_manual(self):
        dial = DialogoAjuda(parent=self)
        dial.exec()
    def abrir_chat_ia(self):
        # Atualiza a IA com os dados mais recentes antes de abrir
        self.ia.dados = self.db_contratos 
        
        ok, msg = self.ia.verificar_status()
        if not ok:
            DarkMessageBox.warning(self, "IA Indisponível", msg)
            return

        dial = DialogoChatIA(self.ia, parent=self)
        dial.exec()

    def abrir_analise_ia(self):
        if not self.contrato_selecionado: return
        
        ok, msg = self.ia.verificar_status()
        if not ok:
            DarkMessageBox.warning(self, "IA Indisponível", msg)
            return

        DarkMessageBox.info(self, "Aguarde", "Enviando dados para auditoria inteligente...\nIsso pode levar alguns segundos.")
        
        ciclo_view = self.combo_ciclo_visualizacao.currentData() or 0
        parecer = self.ia.analisar_risco_contrato(self.contrato_selecionado, ciclo_view)
        
        # Mostra resultado
        dial = BaseDialog(self)
        dial.setWindowTitle("Parecer da Auditoria IA")
        dial.resize(600, 500)
        l = QVBoxLayout(dial)
        txt = QTextEdit()
        txt.setMarkdown(parecer)
        txt.setReadOnly(True)
        l.addWidget(txt)
        btn = QPushButton("Fechar")
        btn.clicked.connect(dial.accept)
        l.addWidget(btn)
        dial.exec()
    def abrir_gestao_prestadores(self):
        dial = DialogoGerenciarPrestadores(self.db_prestadores, parent=self)
        dial.exec() # O salvamento acontece dentro do diálogo ao fechar/alterar

    def importar_prestadores(self):
        instrucao = "CSV (ponto e vírgula):\nRazaoSocial;NomeFantasia;CNPJ;CNES;CodCP"
        DarkMessageBox.info(self, "Instruções", instrucao)
        fname, _ = QFileDialog.getOpenFileName(self, "CSV Prestadores", "", "CSV (*.csv)")
        if not fname: return
        
        sucesso = 0
        try:
            with open(fname, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter=';')
                next(reader, None) # Pula cabeçalho
                for row in reader:
                    if len(row) < 3: continue # Mínimo Razao, Fantasia, CNPJ
                    p = Prestador(
                        row[0].strip(), # Razao
                        row[1].strip(), # Fantasia
                        row[2].strip(), # CNPJ
                        row[3].strip() if len(row) > 3 else "", # CNES
                        row[4].strip() if len(row) > 4 else ""  # CodCP
                    )
                    self.db_prestadores.append(p)
                    sucesso += 1
            
            self.salvar_dados()
            DarkMessageBox.info(self, "Sucesso", f"{sucesso} prestadores importados!")
        except Exception as e:
            DarkMessageBox.critical(self, "Erro", str(e))

        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # --- ÍCONE DA APLICAÇÃO ---
    # Define o ícone globalmente para a barra de tarefas
    caminho_script = os.path.dirname(os.path.abspath(__file__))
    caminho_icone = os.path.join(caminho_script, "icon_gc.png")
    if os.path.exists(caminho_icone):
        app.setWindowIcon(QIcon(caminho_icone))
    # --------------------------------

    win = SistemaGestao()
    
    # 1. Força a criação do ID da janela (invisível) para podermos pintar antes de mostrar
    win.winId()
    
    # 2. Aplica a cor escura AGORA (antes de aparecer na tela)
    aplicar_estilo_janela(win)
    
    # 3. Abre Maximizada (Isso força o Windows a desenhar já com a cor certa)
    win.showMaximized()
    
    sys.exit(app.exec())