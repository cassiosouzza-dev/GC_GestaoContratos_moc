# ARQUIVO: manual_texto.py
# Documentação Técnica Operacional - GC Gestor v3.0
# Atualizado para refletir o Monitor Global e Novas Métricas

HTML_MANUAL = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Manual Técnico Operacional - GC Gestor v3.0</title>
    <style>
        :root {
            --primary-color: #0078d7; 
            --secondary-color: #2c3e50; 
            --accent-color: #27ae60; 
            --danger-color: #c0392b; 
            --warning-color: #f39c12; 
            --purple-color: #8e44ad; 
            --bg-color: #f4f6f7;
            --text-color: #333;
            --border-color: #dcdcdc;
        }

        body {
            font-family: 'Segoe UI', 'Roboto', Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: var(--text-color);
            background-color: var(--bg-color);
            margin: 0;
            padding: 40px;
        }

        h1 {
            color: var(--secondary-color);
            text-align: center;
            border-bottom: 4px solid var(--primary-color);
            padding-bottom: 20px;
            font-size: 2.4em;
            margin-bottom: 50px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        h2 {
            background: linear-gradient(to right, var(--secondary-color), #4b6cb7);
            color: #fff;
            padding: 12px 20px;
            border-radius: 6px;
            margin-top: 50px;
            font-size: 1.4em;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        h3 {
            color: var(--primary-color);
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 8px;
            margin-top: 30px;
            font-size: 1.2em;
        }

        .box-info {
            background-color: #ebf5fb;
            border-left: 5px solid var(--primary-color);
            padding: 15px;
            margin: 20px 0;
            color: #2c3e50;
        }

        .box-success {
            background-color: #eafaf1;
            border-left: 5px solid var(--accent-color);
            padding: 15px;
            margin: 20px 0;
            color: #1d8348;
        }

        details {
            background-color: #fff;
            border: 1px solid var(--border-color);
            border-radius: 6px;
            margin-bottom: 15px;
        }

        summary {
            padding: 18px;
            cursor: pointer;
            font-weight: 600;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .content {
            padding: 25px;
            background-color: #fff;
        }

        .badge {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: bold;
            color: white;
        }

        .footer {
            margin-top: 60px;
            text-align: center;
            font-size: 0.8em;
            color: #95a5a6;
            border-top: 1px solid var(--border-color);
            padding-top: 20px;
        }
    </style>
</head>
<body>

    <h1>MANUAL TÉCNICO OPERACIONAL<br><small style="font-size: 0.4em; color: #7f8c8d;">GC GESTOR DE CONTRATOS E CONVÊNIOS - v3.0</small></h1>

    <div class="box-success">
        <strong>Novidades da Versão 3.0:</strong><br>
        Implementação do <b>Monitor Global de Empenhos</b>, lógica contábil líquida, comparação de metas (Valor Mensal vs Produção Real) e drill-down (clique duplo) para auditoria detalhada.
    </div>

    <h2>1. GESTÃO DE SALDOS E ORÇAMENTO</h2>

    <details open>
        <summary>1.1. Lógica Orçamentária Líquida</summary>
        <div class="content">
            <p>O sistema utiliza o conceito de <b>Saldo Disponível Real</b>:</p>
            <ul>
                <li><b>Cálculo:</b> <code>Saldo = Teto do Ciclo - (Valor Empenhado - Valor Anulado)</code>.</li>
                <li><b>Impacto:</b> Ao realizar uma anulação de NE, o saldo "sobe" imediatamente no painel principal, permitindo novos empenhos sem bloqueios indevidos.</li>
            </ul>
        </div>
    </details>

    <details>
        <summary>1.2. Ciclos e Aditivos</summary>
        <div class="content">
            <p>O sistema gerencia a evolução do contrato através de ciclos financeiros:</p>
            <ul>
                <li><b>Contrato Inicial:</b> O primeiro ciclo orçamentário.</li>
                <li><b>Aditivos de Valor:</b> Acréscimos que aumentam o teto do ciclo vigente.</li>
                <li><b>Novos Ciclos (Prorrogação):</b> Ao criar um aditivo que renova a vigência e o valor, o sistema encerra o ciclo anterior e inicia um novo controle de saldo zerado.</li>
            </ul>
        </div>
    </details>

    <h2>2. EXECUÇÃO FINANCEIRA AVANÇADA</h2>

    <details>
        <summary>2.1. Monitor Global de Saldos (Empenhos)</summary>
        <div class="content">
            <p>Nova ferramenta centralizada para análise financeira em massa (Menu Exibir ou Barra de Ferramentas):</p>
            <ul>
                <li><b>Visão Unificada:</b> Exibe todos os empenhos de todos os contratos ativos em uma única tabela.</li>
                <li><b>Filtros Dinâmicos:</b> Pesquise instantaneamente por Prestador, Número do Contrato, Fonte de Recurso ou Número da NE.</li>
                <li><b>Drill-down (Aprofundamento):</b> Dê um <b>clique duplo</b> em qualquer linha para abrir a janela de "Histórico Maximizado", onde é possível ver cada pagamento e anulação daquela NE específica.</li>
                <li><b>Novas Métricas:</b>
                    <ul>
                        <li><b>Valor Mensal (Fixo):</b> O valor cadastrado como meta/teto mensal do serviço.</li>
                        <li><b>Média Produção (Real):</b> A média aritmética real dos pagamentos efetuados no histórico. (Permite identificar subutilização ou estouro de meta).</li>
                    </ul>
                </li>
            </ul>
        </div>
    </details>

    <details>
        <summary>2.2. Assistente de Rateio de Pagamento</summary>
        <div class="content">
            <p>O assistente de rateio foi redesenhado para maior segurança operacional:</p>
            <ul>
                <li><b>Seleção por Checkbox:</b> Escolha exatamente quais Notas de Empenho (NE) farão parte do pagamento.</li>
                <li><b>Cores de Validação:</b> 
                    <br>- <span style="color: #c0392b; font-weight: bold;">Vermelho:</span> Valor distribuído excede o saldo da NE.
                    <br>- <span style="color: #27ae60; font-weight: bold;">Verde:</span> Distribuição válida.</li>
                <li><b>Bloqueio de Segurança:</b> O botão "Confirmar" só é habilitado quando a soma das NEs selecionadas bate com o valor da fatura.</li>
            </ul>
        </div>
    </details>

    <details>
        <summary>2.3. Bloqueio de NE (Cadeado 🔒)</summary>
        <div class="content">
            <p>Funcionalidade para "congelar" saldos remanescentes:</p>
            <ul>
                <li>Ao bloquear uma NE, o saldo que não foi pago é ignorado nos cálculos de "Saldo Disponível" do serviço.</li>
                <li>Ideal para encerramento de exercícios financeiros.</li>
            </ul>
        </div>
    </details>

    <h2>3. ACESSO E SEGURANÇA</h2>

    <details>
        <summary>3.1. Login e Recuperação</summary>
        <div class="content">
            <p>Autenticação local via CPF e Hash SHA-256.</p>
            <ul>
                <li><b>Palavra Secreta:</b> Essencial para recuperação automática de acesso.</li>
                <li><b>Auditoria:</b> Registro completo de quem empenhou, pagou ou alterou dados.</li>
            </ul>
        </div>
    </details>

    <details>
        <summary>3.2. Backup e Restauração</summary>
        <div class="content">
            <p>O sistema possui proteção contra falhas:</p>
            <ul>
               <li><b>Ponto de Restauração (Undo):</b> Atalho <code>Ctrl+Alt+Z</code> para desfazer ações críticas.</li>
               <li><b>Sincronização Nuvem:</b> Integração opcional com Google Drive para backup remoto.</li>
            </ul>
        </div>
    </details>

    <h2>4. FERRAMENTAS E IA</h2>

    <details>
        <summary>4.1. Monitor de Vigências (Prazos)</summary>
        <div class="content">
            <p>Visualização em grid de todos os contratos com alertas automáticos baseados no prazo restante (cores Roxo, Vermelho, Amarelo e Verde).</p>
        </div>
    </details>

    <details>
        <summary>4.2. Integração Gemini IA</summary>
        <div class="content">
            <p>Análise preditiva de contratos através de inteligência artificial. O sistema analisa o histórico de pagamentos e projeta cenários futuros.</p>
        </div>
    </details>

    <br><br>
    <div class="footer">
        GC Gestor de Contratos e Convênios &copy; 2026<br>
        Documentação Técnica Gerada pela Engine do Sistema - v3.0
    </div>

</body>
</html>
"""