# ARQUIVO: manual_texto.py
# Documentação Técnica Operacional - GC Gestor v1.0

HTML_MANUAL = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Manual Técnico Operacional - GC Gestor</title>
    <style>
        :root {
            --primary-color: #0078d7; /* Azul Corporativo */
            --secondary-color: #2c3e50; /* Cinza Escuro */
            --accent-color: #27ae60; /* Verde Sucesso */
            --danger-color: #c0392b; /* Vermelho Alerta */
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
            border-left: 5px solid var(--danger-color);
            padding: 15px;
            margin: 20px 0;
            color: #bf360c;
        }

        .box-code {
            background-color: #2d3436;
            color: #dfe6e9;
            padding: 15px;
            font-family: 'Consolas', monospace;
            border-radius: 4px;
            font-size: 0.9em;
            overflow-x: auto;
            margin: 15px 0;
        }

        /* Elementos de Interface */
        code {
            background-color: #f0f0f0;
            padding: 2px 5px;
            border-radius: 3px;
            font-family: monospace;
            color: #d63031;
        }

        .breadcrumbs {
            font-size: 0.85em;
            color: #7f8c8d;
            text-transform: uppercase;
            margin-bottom: 10px;
            letter-spacing: 0.5px;
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

    <h1>MANUAL TÉCNICO OPERACIONAL<br><small style="font-size: 0.4em; color: #7f8c8d;">GC GESTOR DE CONTRATOS E CONVÊNIOS</small></h1>

    <div class="box-info">
        <strong>Objetivo do Documento:</strong><br>
        Este manual descreve as funcionalidades, regras de negócio e procedimentos operacionais do sistema GC Gestor, destinado ao controle financeiro e administrativo de contratos públicos.
    </div>

    <h2>1. ESTRUTURA E CONCEITOS DO SISTEMA</h2>

    <details open>
        <summary>1.1. Hierarquia de Dados</summary>
        <div class="content">
            <p>O sistema opera sob uma lógica relacional estrita para garantir a integridade da execução orçamentária. A hierarquia de dependência é:</p>
            <ol>
                <li><b>Prestador (Entidade):</b> O cadastro base (CNPJ, Razão Social). Nenhum contrato pode ser criado sem um prestador previamente cadastrado.</li>
                <li><b>Contrato:</b> O instrumento legal. Define o objeto, valor inicial e vigência.</li>
                <li><b>Ciclo Financeiro:</b> A divisão temporal do orçamento (ex: Exercício 2025, Exercício 2026).
                    <ul>
                        <li><b>Ciclo 0 (Contrato Inicial):</b> Período original de vigência.</li>
                        <li><b>Ciclos Subsequentes:</b> Criados automaticamente mediante Aditivos de Prazo com Renovação de Valor (Prorrogações).</li>
                    </ul>
                </li>
                <li><b>Serviço (Subcontrato):</b> A categorização da despesa (ex: "Manutenção", "Insumos"). O orçamento é alocado por serviço dentro de cada ciclo.</li>
                <li><b>Nota de Empenho (NE):</b> A reserva orçamentária. Vincula-se obrigatoriamente a um Ciclo e a um Serviço.</li>
                <li><b>Movimentação Financeira:</b> A execução real da despesa (Pagamentos ou Anulações de empenho).</li>
            </ol>
        </div>
    </details>

    <details>
        <summary>1.2. Tipos de Termos Aditivos (TA)</summary>
        <div class="content">
            <p>O sistema diferencia o impacto financeiro dos aditivos:</p>
            <ul>
                <li><b>Aditivo de Valor (Acréscimo/Supressão):</b> Altera o teto financeiro do <i>Ciclo Vigente</i>. Não altera a vigência final do contrato, apenas o saldo disponível.</li>
                <li><b>Aditivo de Prazo (Prorrogação Simples):</b> Estende a data de vigência sem aporte de novos recursos.</li>
                <li><b>Aditivo de Prazo com Renovação de Valor:</b> Estende a vigência e aporta novo orçamento. 
                    <br><i>Ação do Sistema:</i> Encerra o ciclo atual e gera um <b>Novo Ciclo Financeiro</b> (ex: 1º TA, 2º TA), zerando os saldos comprometidos e iniciando um novo período contábil.</li>
            </ul>
        </div>
    </details>

    <h2>2. INTERFACE E NAVEGAÇÃO</h2>

    <details>
        <summary>2.1. Barra de Menus (Superior)</summary>
        <div class="content">
            <p>Funcionalidades acessíveis através do menu principal:</p>

            <h3>Arquivo</h3>
            <ul>
                <li><b>Novo Contrato:</b> Inicia o assistente de cadastro.</li>
                <li><b>Trocar Base de Dados:</b> Permite alternar entre diferentes arquivos <code>.json</code> (ex: bases de setores diferentes).</li>
                <li><b>Fazer Backup de Segurança (.bak):</b> Gera uma cópia imediata da base atual com carimbo de data/hora na pasta do sistema.</li>
                <li><b>Alterar Minha Senha:</b> Redefinição de credenciais do usuário logado.</li>
                <li><b>Trocar Usuário (Logout):</b> Retorna à tela de login.</li>
            </ul>

            <h3>Editar</h3>
            <ul>
                <li><b>Desfazer (Undo):</b> Reverte a última ação crítica (exclusão, importação em lote). O sistema mantém um ponto de restauração automático.</li>
                <li><b>Recortar/Copiar/Colar:</b> Operações padrão de texto.</li>
            </ul>

            <h3>Exibir</h3>
            <ul>
                <li><b>Painel de Pesquisa:</b> Retorna à tela inicial.</li>
                <li><b>Personalizar Cores e Fontes:</b> Ajustes de acessibilidade e tema (Modo Escuro, Alto Contraste).</li>
                <li><b>Contratos Excluídos (Lixeira):</b> Acesso a registros ocultos (Soft Delete) com opção de restauração.</li>
            </ul>

            <h3>Cadastros</h3>
            <ul>
                <li><b>Gerenciar Prestadores:</b> Cadastro, edição e remoção de empresas/entidades.</li>
                <li><b>Auditoria (Logs):</b> Visualização do rastro de atividades (quem fez o quê e quando).</li>
            </ul>

            <h3>Ferramentas</h3>
            <ul>
                <li><b>Assistente de Importação:</b> Importação em lote de dados via arquivos CSV (Contratos, Serviços, NEs, Pagamentos).</li>
                <li><b>Sincronizar com Google Drive:</b> Módulo de integração em nuvem para trabalho colaborativo.</li>
                <li><b>Verificar Integridade:</b> Diagnóstico técnico da estrutura do banco de dados.</li>
            </ul>
        </div>
    </details>

    <details>
        <summary>2.2. Painel de Pesquisa (Tela Inicial)</summary>
        <div class="content">
            <p>A tela principal apresenta uma barra de busca global ("Omni-search"). A filtragem ocorre em tempo real nos seguintes campos:</p>
            <ul>
                <li>Número do Contrato.</li>
                <li>Número da Nota de Empenho (NE).</li>
                <li>Razão Social ou Nome Fantasia do Prestador.</li>
                <li>CNPJ.</li>
                <li>Descrição do Objeto.</li>
            </ul>
            <p><b>Observação:</b> Ao digitar o número de uma NE, o sistema exibirá o contrato correspondente. O duplo clique no resultado abrirá diretamente o detalhe do contrato ou focará na NE pesquisada.</p>
        </div>
    </details>

    <h2>3. MÓDULOS OPERACIONAIS</h2>

    <details>
        <summary>3.1. Gestão de Contratos (Aba Dados)</summary>
        <div class="content">
            <div class="breadcrumbs">Localização: Tela de Detalhes > Aba "Dados"</div>
            <p>Esta aba apresenta a "Linha do Tempo" financeira do contrato.</p>

            <h4>Tabela de Resumo Financeiro</h4>
            <p>Exibe cronologicamente todos os eventos (Contrato Inicial e Aditivos). Colunas:</p>
            <ul>
                <li><b>Evento/Referência:</b> Identificação do ato (ex: Contrato Inicial, 1º Termo Aditivo).</li>
                <li><b>Vigência e Competência:</b> Período legal e meses de competência abrangidos.</li>
                <li><b>Valor do Ato:</b> O impacto financeiro específico daquele evento (Acréscimo ou Decréscimo).</li>
                <li><b>Teto (Ref.):</b> O limite orçamentário acumulado ou específico do ciclo.</li>
                <li><b>Saldo de Pagamentos:</b> Valor disponível em caixa (Teto - Pagamentos Realizados).</li>
                <li><b>Não Empenhado:</b> Valor disponível para emissão de novas NEs (Teto - Empenhos Emitidos).</li>
            </ul>
        </div>
    </details>

    <details>
        <summary>3.2. Execução Financeira (Aba Financeiro)</summary>
        <div class="content">
            <div class="breadcrumbs">Localização: Tela de Detalhes > Aba "Financeiro"</div>
            <p>Módulo responsável pela emissão de empenhos e liquidação de despesas.</p>

            <h4>Tabela de Notas de Empenho (Superior)</h4>
            <p>Lista as NEs do ciclo selecionado. Ícones e cores indicam o status:</p>
            <ul>
                <li><b>Texto Preto:</b> NE ativa normal.</li>
                <li><b>Texto Cinza + Ícone Cadeado (🔒):</b> NE Bloqueada. O saldo desta nota não é computado como disponível e não permite novos pagamentos.</li>
            </ul>

            <h4>Funcionalidades (Botões):</h4>
            <ul>
                <li><b>[+ NE]:</b> Emite nova nota. Exige a definição das competências (meses) que a nota cobre para fins de rateio em relatórios.</li>
                <li><b>[Pagar]:</b> Registra liquidação. O usuário deve selecionar as competências a que se refere o pagamento na lista de meses.</li>
                <li><b>[Anular]:</b> Realiza o estorno de valor (devolução de saldo para a NE).</li>
                <li><b>[Bloquear/Desbloq.]:</b> Congela a NE. Útil para restos a pagar não processados ou notas encerradas administrativamente.</li>
                <li><b>[Analisar Risco (IA)]:</b> Solicita uma análise preditiva do módulo de Inteligência Artificial sobre a execução financeira.</li>
            </ul>
        </div>
    </details>

    <details>
        <summary>3.3. Serviços e Orçamento (Aba Serviços)</summary>
        <div class="content">
            <p>Define a distribuição analítica do orçamento. Cada serviço (item de despesa) possui seu próprio controle de saldo.</p>
            <p>Ao cadastrar um serviço, define-se um "Valor Mensal Estimado". O sistema projeta o valor total para o ciclo vigente. O controle de saldo impede a emissão de NEs se o serviço não possuir dotação suficiente, mesmo que o contrato global possua saldo.</p>
        </div>
    </details>

    <details>
        <summary>3.4. Gestão de Aditivos (Aba Aditivos)</summary>
        <div class="content">
            <p>Permite o registro de alterações contratuais. O sistema valida a integridade das datas:</p>
            <ul>
                <li><b>Validação de Competência:</b> Para aditivos de renovação, é <b>obrigatório</b> informar as competências inicial e final (formato MM/AAAA) para correta geração dos relatórios mensais.</li>
                <li><b>Reordenação Automática:</b> Caso um aditivo seja excluído, o sistema renomeia automaticamente a sequência dos ciclos financeiros subsequentes para manter a consistência (ex: o antigo 3º TA torna-se o 2º TA).</li>
            </ul>
        </div>
    </details>

    <details>
        <summary>3.5. Painel Detalhe Contrato/Ciclo (Aba Global)</summary>
        <div class="content">
            <p>Oferece uma visão matricial ("Cross-tab") da execução mensal. Exibe, mês a mês:</p>
            <ul>
                <li>Meta Mensal (Previsão).</li>
                <li>Valor Executado (Pago).</li>
                <li>Saldo Mensal (Superávit/Déficit).</li>
                <li>Percentual de Execução.</li>
            </ul>
            <p>Permite identificar rapidamente meses descobertos ou com execução acima do teto.</p>
        </div>
    </details>

    <h2>4. FERRAMENTAS AVANÇADAS</h2>

    <details>
        <summary>4.1. Sincronização Híbrida (Google Drive)</summary>
        <div class="content">
            <p>O módulo de sincronização permite o trabalho colaborativo através de arquivo JSON compartilhado. O sistema oferece modos distintos de operação para evitar conflitos:</p>
            <ol>
                <li><b>Sincronizar Tudo (Bidirecional):</b> Baixa alterações da nuvem, mescla com os dados locais e envia o resultado consolidado.</li>
                <li><b>Apenas Importar:</b> Atualiza o sistema local com dados da nuvem, mas <b>não envia</b> as alterações locais. Ideal para consulta.</li>
                <li><b>Apenas Subir:</b> Força o envio dos dados locais, sobrescrevendo a nuvem (com preservação de registros inexistentes localmente).</li>
            </ol>
        </div>
    </details>

    <details>
        <summary>4.2. Módulo de Inteligência Artificial</summary>
        <div class="content">
            <p>O sistema integra-se à API Google Gemini para fornecer:</p>
            <ul>
                <li><b>Chat com Dados:</b> Interface de linguagem natural para consultas complexas (ex: "Quais contratos vencem em março?").</li>
                <li><b>Análise de Risco:</b> Avaliação automática da saúde financeira do contrato, identificando padrões de execução anômalos.</li>
                <li><b>Interpretação de Alertas:</b> Sugestão de planos de ação para notificações críticas (ex: saldo insuficiente).</li>
            </ul>
        </div>
    </details>

    <h2>5. SEGURANÇA DA INFORMAÇÃO</h2>

    <details>
        <summary>5.1. Mecanismos de Proteção</summary>
        <div class="content">
            <p>O GC Gestor implementa camadas de segurança para integridade dos dados:</p>
            <ul>
                <li><b>Ponto de Restauração (Undo):</b> Antes de qualquer operação destrutiva (Exclusão, Importação), o sistema salva um snapshot do estado anterior, permitindo reversão via <i>Ctrl+Alt+Z</i>.</li>
                <li><b>Soft Delete:</b> Contratos excluídos não são apagados fisicamente, mas movidos para a "Lixeira" (acessível no menu Exibir), mantendo o histórico de auditoria.</li>
                <li><b>Auditoria (Logs):</b> Todas as ações de alteração de dados são registradas com Carimbo de Tempo, Usuário e CPF.</li>
            </ul>
        </div>
    </details>

    <br><br>
    <div class="footer">
        GC Gestor de Contratos e Convênios &copy; 2025<br>
        Documentação Técnica Gerada Automaticamente pelo Sistema.
    </div>

</body>
</html>
"""