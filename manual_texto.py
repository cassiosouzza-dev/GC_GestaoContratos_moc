# ARQUIVO: manual_texto.py
# Documentação Técnica Operacional - GC Gestor v2.2
# Atualizado conforme código-fonte da versão 2.2

HTML_MANUAL = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Manual Técnico Operacional - GC Gestor v2.2</title>
    <style>
        :root {
            --primary-color: #0078d7; /* Azul Corporativo */
            --secondary-color: #2c3e50; /* Cinza Escuro */
            --accent-color: #27ae60; /* Verde Sucesso */
            --danger-color: #c0392b; /* Vermelho Alerta */
            --warning-color: #f39c12; /* Laranja */
            --purple-color: #8e44ad; /* Roxo */
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

        /* Tipografia */
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

        h4 {
            color: #555;
            margin-top: 20px;
            font-weight: 700;
        }

        /* Componentes de Texto */
        p {
            margin-bottom: 15px;
            text-align: justify;
        }

        ul, ol {
            margin-bottom: 20px;
            padding-left: 25px;
        }

        li {
            margin-bottom: 8px;
        }

        /* Accordion / Sanfona */
        details {
            background-color: #fff;
            border: 1px solid var(--border-color);
            border-radius: 6px;
            margin-bottom: 15px;
            transition: all 0.3s ease;
        }

        details[open] {
            border-left: 6px solid var(--primary-color);
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }

        summary {
            padding: 18px;
            cursor: pointer;
            font-weight: 600;
            font-size: 1.05em;
            background-color: #ffffff;
            border-radius: 6px;
            list-style: none;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        summary:hover {
            background-color: #f8fbff;
        }

        summary::after {
            content: '+';
            color: var(--primary-color);
            font-weight: bold;
            font-size: 1.5em;
        }

        details[open] summary::after {
            content: '-';
            color: var(--danger-color);
        }

        details[open] summary {
            border-bottom: 1px solid #eee;
        }

        .content {
            padding: 25px;
            background-color: #fff;
            border-radius: 0 0 6px 6px;
        }

        /* Tabelas */
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 0.95em;
            background-color: #fff;
        }

        th, td {
            border: 1px solid var(--border-color);
            padding: 10px 15px;
            text-align: left;
        }

        th {
            background-color: #eef2f5;
            color: var(--secondary-color);
            font-weight: 700;
            text-transform: uppercase;
            font-size: 0.85em;
        }

        tr:nth-child(even) {
            background-color: #fdfdfd;
        }

        /* Caixas de Alerta e Nota */
        .box-info {
            background-color: #ebf5fb;
            border-left: 5px solid var(--primary-color);
            padding: 15px;
            margin: 20px 0;
            color: #2c3e50;
        }

        .box-warning {
            background-color: #fef5e7;
            border-left: 5px solid var(--warning-color);
            padding: 15px;
            margin: 20px 0;
            color: #d35400;
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

    <h1>MANUAL TÉCNICO OPERACIONAL<br><small style="font-size: 0.4em; color: #7f8c8d;">GC GESTOR DE CONTRATOS E CONVÊNIOS - v2.2</small></h1>

    <div class="box-info">
        <strong>Versão Atualizada:</strong><br>
        Este documento reflete as funcionalidades da versão 2.2, incluindo novos módulos de Rateio de Pagamentos, Bloqueio de NE, Monitoramento de Vigências e Integração com IA.
    </div>

    <h2>1. ACESSO E SEGURANÇA</h2>

    <details open>
        <summary>1.1. Login e Autenticação</summary>
        <div class="content">
            <p>O sistema utiliza controle de acesso local baseado em CPF e Senha criptografada (Hash SHA-256).</p>
            <ul>
                <li><b>Primeiro Acesso:</b> Caso não existam usuários cadastrados, o sistema permitirá entrada como "Administrador" para configuração inicial.</li>
                <li><b>Cadastro de Usuário:</b> Na tela de login, utilize a opção "Criar Nova Conta". É obrigatório definir uma <b>Palavra Secreta</b> para recuperação de senha.</li>
                <li><b>Recuperação de Senha:</b> Caso esqueça sua senha, utilize a opção "Esqueci minha senha" e informe seu CPF e a Palavra Secreta cadastrada.</li>
            </ul>
        </div>
    </details>

    <details>
        <summary>1.2. Integridade de Dados</summary>
        <div class="content">
            <p>O GC Gestor implementa camadas robustas de proteção:</p>
            <ul>
                <li><b>Ponto de Restauração (Undo):</b> Antes de ações críticas (Exclusão em massa, Importação, Rateio), o sistema cria um backup temporário. Utilize o menu <i>Editar > Desfazer</i> ou <code>Ctrl+Alt+Z</code> para reverter.</li>
                <li><b>Soft Delete (Lixeira):</b> Contratos excluídos não somem do banco de dados imediatamente. Eles são marcados como "Anulados" e podem ser restaurados via <i>Ferramentas > Lixeira</i>.</li>
                <li><b>Auditoria (Logs):</b> Todas as ações são registradas com Data, Hora, Usuário e CPF. Acesse em <i>Cadastros > Auditoria</i>.</li>
            </ul>
        </div>
    </details>

    <h2>2. ESTRUTURA ORÇAMENTÁRIA (Conceitos Chave)</h2>

    <details>
        <summary>2.1. Hierarquia do Contrato</summary>
        <div class="content">
            <p>Para garantir a execução financeira correta, o sistema segue esta estrutura rígida:</p>
            <ol>
                <li><b>Prestador:</b> Entidade jurídica (CNPJ) credora. Deve ser cadastrado <i>antes</i> do contrato.</li>
                <li><b>Contrato:</b> O instrumento legal base.</li>
                <li><b>Ciclo Financeiro:</b> O "balde" orçamentário.
                    <ul>
                        <li><i>Contrato Inicial:</i> Primeiro ciclo.</li>
                        <li><i>Termos Aditivos:</i> Novos ciclos criados apenas quando há renovação de prazo <b>com</b> renovação de valor.</li>
                    </ul>
                </li>
                <li><b>Serviço (Subcontrato):</b> A categorização da despesa (Item de orçamento). Possui saldo independente dentro de cada ciclo.</li>
                <li><b>Nota de Empenho (NE):</b> A reserva de recurso vinculada a um Serviço e a um Ciclo.</li>
            </ol>
        </div>
    </details>

    <details>
        <summary>2.2. Tipos de Termos Aditivos</summary>
        <div class="content">
            <p>O sistema diferencia o impacto financeiro dos aditivos:</p>
            <ul>
                <li><b>Aditivo de Valor (Acréscimo/Supressão):</b> Altera o teto financeiro do <i>Ciclo Vigente</i> (soma ou subtrai do saldo atual).</li>
                <li><b>Aditivo de Prazo (Prorrogação Simples):</b> Estende a data de vigência sem aporte de novos recursos.</li>
                <li><b>Aditivo de Prazo com Renovação de Valor:</b> Ação crítica. O sistema encerra o ciclo atual e gera um <b>Novo Ciclo Financeiro</b> (ex: 2º TA), zerando os saldos anteriores e iniciando um novo orçamento.</li>
            </ul>
            <div class="box-warning">
                <b>Atenção:</b> Ao criar aditivos de renovação, é obrigatório informar as Competências (MM/AAAA) Inicial e Final para que os relatórios mensais funcionem corretamente.
            </div>
        </div>
    </details>

    <h2>3. FUNCIONALIDADES OPERACIONAIS</h2>

    <details>
        <summary>3.1. Monitor de Vigências e Prazos</summary>
        <div class="content">
            <p>Acessível via menu <i>Exibir > Monitor de Vigências</i> ou botão "Prazos" na barra de ferramentas. Utiliza código de cores para priorização:</p>
            <ul>
                <li><span class="badge" style="background-color: #8e44ad;">ROXO</span> <b>Vencido:</b> Contrato já expirado.</li>
                <li><span class="badge" style="background-color: #c0392b;">VERMELHO</span> <b>Crítico:</b> Vence em menos de 90 dias. Ação imediata necessária.</li>
                <li><span class="badge" style="background-color: #f39c12;">AMARELO</span> <b>Atenção:</b> Vence em menos de 180 dias. Planejamento necessário.</li>
                <li><span class="badge" style="background-color: #27ae60;">VERDE</span> <b>Vigente:</b> Mais de 180 dias de prazo. Situação confortável.</li>
            </ul>
        </div>
    </details>

    <details>
        <summary>3.2. Execução Financeira (Empenhos e Pagamentos)</summary>
        <div class="content">
            <p>Localizado na aba "Financeiro" dentro dos detalhes do contrato.</p>

            <h4>Funcionalidades Principais:</h4>
            <ul>
                <li><b>[+ NE]:</b> Emite nova Nota de Empenho. Exige vínculo com um Serviço.</li>
                <li><b>[Pagar]:</b> Registra liquidação. O valor é abatido do saldo da NE.</li>
                <li><b>[Ratear Pagamento]:</b> <i>(Novo)</i> Divide um valor total de fatura entre várias NEs automaticamente, priorizando as mais antigas ou permitindo ajuste manual.</li>
                <li><b>[Bloquear 🔒]:</b> Congela a NE. O saldo restante deixa de ser considerado "Disponível" para o serviço. Útil para Restos a Pagar não processados.</li>
                <li><b>[Anular]:</b> Estorno de valor (devolução de saldo para a NE).</li>
                <li><b>Maximizar Histórico:</b> Abre uma janela dedicada para visualizar toda a movimentação da NE selecionada.</li>
            </ul>
        </div>
    </details>

    <details>
        <summary>3.3. Assistente de Importação (Lote)</summary>
        <div class="content">
            <p>Permite carregar grandes volumes de dados via arquivos CSV (separados por ponto e vírgula). O sistema possui proteção contra erros de codificação (UTF-8 / Latin-1).</p>
            <p><b>Ordem Recomendada de Importação:</b></p>
            <ol>
                <li><b>Prestadores:</b> <code>Razao; Fantasia; CNPJ; CNES; CodCP</code></li>
                <li><b>Contratos:</b> Requer estrutura específica de 11 colunas (ver modelo no sistema).</li>
                <li><b>Serviços:</b> Requer contrato aberto. <code>Descrição; Valor Total; Valor Mensal</code>.</li>
                <li><b>Empenhos:</b> <code>Numero; Valor; Descricao; Servico; Fonte; Data; Competencias</code>.</li>
                <li><b>Pagamentos:</b> Vincula por número da NE. <code>NumeroNE; Valor; Competencia; Obs</code>.</li>
            </ol>
        </div>
    </details>

    <h2>4. FERRAMENTAS AVANÇADAS</h2>

    <details>
        <summary>4.1. Sincronização em Nuvem (Google Drive)</summary>
        <div class="content">
            <p>Módulo para trabalho colaborativo ou backup remoto. Requer arquivo <code>credentials.json</code> na pasta do sistema.</p>
            <ul>
                <li><b>Sincronizar Tudo:</b> Baixa alterações da nuvem (fusão inteligente) e envia suas modificações locais.</li>
                <li><b>Apenas Importar:</b> Atualiza seu sistema com dados da nuvem sem enviar nada.</li>
                <li><b>Apenas Subir:</b> Força o envio dos seus dados para a nuvem.</li>
                <li><b>Baixar Arquivo:</b> Salva uma cópia do JSON da nuvem no seu computador para análise.</li>
            </ul>
        </div>
    </details>

    <details>
        <summary>4.2. Inteligência Artificial (Gemini)</summary>
        <div class="content">
            <p>O sistema integra-se à API do Google para análise de dados. Requer arquivo <code>chave_api.txt</code>.</p>
            <ul>
                <li><b>Análise de Risco:</b> Avalia a execução financeira do contrato e aponta tendências de déficit ou superávit.</li>
                <li><b>Chat com Dados:</b> Interface de conversação natural. Ex: "Qual contrato vence em março?" ou "Quanto pagamos para a empresa X?".</li>
                <li><b>Interpretação de Alertas:</b> Sugere planos de ação para notificações críticas de saldo.</li>
            </ul>
        </div>
    </details>

    <details>
        <summary>4.3. Personalização e Aparência</summary>
        <div class="content">
            <p>Acesse via menu <i>Exibir > Personalizar Cores e Fontes</i>.</p>
            <ul>
                <li><b>Temas Prontos:</b> Escuro (Dark), Claro (Light), Dracula, Ocean, Matrix, Alto Contraste.</li>
                <li><b>Ajuste Manual:</b> Permite definir cores específicas para Fundo, Seleção, Tabelas e Cabeçalhos.</li>
                <li><b>Tamanho da Fonte:</b> Ajuste global de legibilidade (12px a 18px).</li>
            </ul>
        </div>
    </details>

    <details>
        <summary>4.4. Arquivamento Histórico</summary>
        <div class="content">
            <p>Para manter o sistema leve, contratos antigos podem ser movidos para uma base secundária.</p>
            <p>Acesse <i>Ferramentas > Arquivar Contratos Antigos</i>. O sistema moverá contratos encerrados antes do ano selecionado para o arquivo <code>arquivo_historico.db</code>, limpando a visualização principal.</p>
        </div>
    </details>

    <br><br>
    <div class="footer">
        GC Gestor de Contratos e Convênios &copy; 2026<br>
        Documentação Técnica Gerada Automaticamente pelo Sistema.
    </div>

</body>
</html>
"""