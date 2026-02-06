import sys
import os
import csv
from datetime import datetime
from PyQt6.QtWidgets import QApplication

# Importa as classes do seu sistema principal
# Certifique-se de que o arquivo principal se chama 'gestao_contratos.py'
try:
    from gestao_contratos import (
        SistemaGestao, BancoDados, Contrato, Prestador,
        SubContrato, NotaEmpenho, Movimentacao, TelaCarregamento
    )
except ImportError:
    print("ERRO: Não foi possível importar 'gestao_contratos.py'.")
    print("Verifique se este script está na mesma pasta do arquivo principal.")
    sys.exit(1)

# --- CONFIGURAÇÃO DO AMBIENTE DE TESTE ---
ARQUIVO_DB_TESTE = "banco_teste_funcionalidades.db"


def criar_ambiente_teste():
    print("--- PREPARANDO AMBIENTE DE TESTE ---")

    # 1. Limpa banco anterior para teste limpo
    if os.path.exists(ARQUIVO_DB_TESTE):
        os.remove(ARQUIVO_DB_TESTE)
        print(f"Banco antigo '{ARQUIVO_DB_TESTE}' removido.")

    # 2. Inicializa Banco
    banco = BancoDados(ARQUIVO_DB_TESTE)

    # 3. Cria Dados Fictícios

    # Prestador
    p1 = Prestador("Empresa de Teste Ltda", "Tech Solutions", "12.345.678/0001-90", "123456", "999")

    # Contrato
    c1 = Contrato(
        numero="100/2025",
        prestador="Tech Solutions",
        descricao="Contrato de Teste Geral",
        valor_inicial=150000.00,
        vig_inicio="01/01/2025",
        vig_fim="31/12/2025",
        comp_inicio="01/2025",
        comp_fim="12/2025",
        licitacao="Pregão 01/25",
        dispensa="",
        sequencial_inicio=0
    )

    # Serviço (Com texto LONGO para testar a quebra de linha na tabela)
    desc_longa = (
        "Serviço de Manutenção Preventiva e Corretiva com Fornecimento de Peças "
        "Genuínas para a Frota de Veículos Leves e Pesados da Secretaria de Saúde "
        "(Este texto é propositalmente longo para validar se a tabela ajusta a altura da linha "
        "e se a coluna não fica infinita na tela)."
    )

    sub1 = SubContrato(desc_longa, valor_mensal=5000.00)
    sub1.set_valor_ciclo(0, 60000.00)  # Orçamento do ciclo 0
    c1.lista_servicos.append(sub1)

    # Serviço Curto (para comparação)
    sub2 = SubContrato("Serviço de Limpeza Simples", valor_mensal=1000.00)
    sub2.set_valor_ciclo(0, 12000.00)
    c1.lista_servicos.append(sub2)

    # Nota de Empenho (Para testar Histórico Maximizado e Nova Coluna)
    ne1 = NotaEmpenho(
        numero="2025NE001",
        valor=10000.00,
        descricao="Empenho estimativo inicial",
        subcontrato_idx=0,  # Vinculado ao serviço longo
        fonte_recurso="1.500",
        data_emissao="02/01/2025",
        ciclo_id=0,
        competencias_ne="01/2025, 02/2025"
    )

    # Adiciona histórico para testar a coluna "Descrição / Obs"
    ne1.historico.append(Movimentacao("Pagamento", 2000.00, "01/2025", "Pgto referente Medição 1 (Teste Coluna Obs)"))
    ne1.historico.append(Movimentacao("Pagamento", 2000.00, "02/2025", "Pgto referente Medição 2"))
    ne1.historico.append(Movimentacao("Anulação", -500.00, "-", "Valor não utilizado no período"))

    c1.lista_notas_empenho.append(ne1)

    # Salva no Banco
    print("Salvando dados no banco SQLite...")
    # Cria dicionário de usuários fake para logar direto
    usuarios = {"000.000.000-00": {"nome": "Testador", "hash": "...", "admin": True}}

    banco.salvar_tudo_snapshot([c1], [p1], [], usuarios)
    print("Dados salvos.")

    return banco


def gerar_csvs_para_teste():
    """Gera arquivos CSV na pasta para testar as novas importações globais"""
    print("--- GERANDO ARQUIVOS CSV DE EXEMPLO ---")

    # 1. CSV Empenhos Global (9 Colunas)
    # Contrato; Ciclo; NE; Valor; Descrição; Serviço; Fonte; Data; Competências
    with open("teste_import_empenhos_global.csv", "w", newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(["Contrato", "Ciclo", "NE", "Valor", "Desc", "Serviço", "Fonte", "Data", "Comps"])
        # Linha Válida (Serviço existe)
        writer.writerow(
            ["100/2025", "0", "2025NE999", "1500,00", "Teste Import", "Serviço de Limpeza Simples", "100", "01/03/2025",
             "03/2025"])
        # Linha com Erro (Serviço não existe - para testar o alerta)
        writer.writerow(
            ["100/2025", "0", "2025NE888", "100,00", "Erro Proposital", "Serviço Inexistente", "100", "01/03/2025", ""])
    print("Criado: teste_import_empenhos_global.csv")

    # 2. CSV Serviços Global (7 Colunas)
    # Contrato; Ciclo; Descrição; Mensal; Total; Replicar; Fonte
    with open("teste_import_servicos_global.csv", "w", newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(["Contrato", "Ciclo", "Descrição", "Mensal", "Total", "Replicar", "Fonte"])
        writer.writerow(["100/2025", "0", "Novo Serviço Importado Via CSV", "500,00", "6000,00", "S", "100"])
    print("Criado: teste_import_servicos_global.csv")


def main():
    # 1. Gera o ambiente
    banco = criar_ambiente_teste()
    gerar_csvs_para_teste()

    # 2. Inicia a Aplicação Qt
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # 3. Inicia o Sistema apontando para o banco de teste
    # Precisamos injetar o splash screen fake ou real para não quebrar o init
    janela = SistemaGestao(splash=None)

    # 4. FORÇA o uso do banco de teste e recarrega
    janela.arquivo_db = ARQUIVO_DB_TESTE
    janela.banco = banco
    janela.carregar_dados()  # Recarrega memória com os dados do banco de teste

    # 5. Loga automaticamente como Admin
    janela.usuario_nome = "Usuário de Teste"
    janela.usuario_cpf = "000.000.000-00"
    janela.atualizar_barra_status()

    # 6. Abre o contrato de teste automaticamente para agilizar
    if janela.db_contratos:
        janela.contrato_selecionado = janela.db_contratos[0]
        janela.atualizar_painel_detalhes()
        janela.stack.setCurrentIndex(1)  # Vai para aba detalhes
        janela.abas.setCurrentIndex(2)  # Vai para aba Serviços (para ver a tabela nova)

    janela.showMaximized()

    print("\n=== ROTEIRO DE TESTE ===")
    print("1. ABA SERVIÇOS: Veja se o 'Serviço de Manutenção...' quebrou a linha e a altura da célula aumentou.")
    print("2. ABA FINANCEIRO: Clique na NE 2025NE001 e depois em 'Maximizar Histórico'.")
    print("   -> Verifique se apareceu a coluna 'Descrição / Obs' no meio.")
    print("   -> Verifique se a janela abriu mais larga.")
    print("3. FERRAMENTAS > IMPORTAÇÃO (LOTE):")
    print("   -> Teste 'Importar Empenhos (GLOBAL)' selecionando o arquivo 'teste_import_empenhos_global.csv'.")
    print("   -> Teste 'Importar Serviços (GLOBAL)' selecionando o arquivo 'teste_import_servicos_global.csv'.")
    print("4. RATEIO:")
    print("   -> Na aba Financeiro, clique em [Ratear Pagamento] SEM selecionar nenhuma NE.")
    print("   -> Veja se ele abre a lista para escolher o serviço.")
    print("========================\n")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()