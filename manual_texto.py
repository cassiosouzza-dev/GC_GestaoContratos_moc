# MANUAL TÉCNICO OPERACIONAL - GC GESTOR ENTERPRISE
# DOCUMENTAÇÃO OFICIAL UNIFICADA

HTML_MANUAL = """
<style>
    body { font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; margin: 20px; }
    h1 { color: #2c3e50; text-align: center; border-bottom: 3px solid #2c3e50; padding-bottom: 10px; margin-bottom: 30px; }

    /* Hierarquia Visual */
    h2 { 
        background: linear-gradient(to right, #34495e, #2c3e50); 
        color: white; 
        padding: 10px 15px; 
        margin-top: 40px; 
        border-radius: 4px; 
        font-size: 18px; 
        text-transform: uppercase; 
        letter-spacing: 1px;
    }
    h3 { 
        color: #16a085; 
        border-left: 5px solid #16a085; 
        padding-left: 10px; 
        margin-top: 30px; 
        font-size: 16px; 
        background-color: #f9f9f9;
        padding-top: 5px;
        padding-bottom: 5px;
    }

    /* Caixas Especiais */
    .box-info { background-color: #e8f6f3; border: 1px solid #a2d9ce; border-left: 5px solid #1abc9c; padding: 15px; margin: 15px 0; font-size: 13px; border-radius: 3px; }
    .box-ai { background-color: #f4ecf7; border: 1px solid #d2b4de; border-left: 5px solid #8e44ad; padding: 15px; margin: 15px 0; font-size: 13px; border-radius: 3px; }
    .box-security { background-color: #fff8e1; border: 1px solid #ffe082; border-left: 5px solid #ffb300; padding: 15px; margin: 15px 0; font-size: 13px; border-radius: 3px; }

    /* Tabelas e Atalhos */
    table { width: 100%; border-collapse: collapse; font-size: 12px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
    th { background-color: #ecf0f1; border: 1px solid #bdc3c7; padding: 10px; text-align: left; font-weight: bold; color: #2c3e50; }
    td { border: 1px solid #bdc3c7; padding: 8px; }
    tr:nth-child(even) { background-color: #fbfbfb; }
    kbd { background-color: #eee; border-radius: 3px; border: 1px solid #b4b4b4; padding: 2px 4px; font-weight: 700; font-size: 0.85em; }
</style>

<h1>MANUAL TÉCNICO DE OPERAÇÃO (MTO)</h1>
<p style='text-align: center; color: #7f8c8d; font-size: 12px;'>GC Gestor Enterprise | Documentação Oficial</p>

<div class="box-info">
    <b>Conceito Central: Ciclos Financeiros Estanques</b><br>
    O GC Gestor não trata o contrato como uma linha contínua, mas como "gavetas" separadas (Ciclos). O saldo do Ano 1 não se mistura automaticamente com o Ano 2. Isso garante conformidade com o princípio da anualidade orçamentária pública.
</div>

<h2>1. A TELA INICIAL (DASHBOARD)</h2>

<h3>1.1 Barra Superior: O Centro de Inteligência</h3>
<ul>
    <li><b>Botão [💬 IA] (Consultor Global):</b> 
        <br>Chat geral com acesso a <i>todos</i> os contratos. Use para perguntas transversais (ex: "Qual o total gasto com a empresa X em todos os contratos?").
    </li>

    <li><b>Botão [🔔 Notificações] (Auditor de Prazos):</b> 
        <br>Monitora vencimentos e saldos em tempo real. Ícone vermelho indica alertas críticos.
        <br><b>Recurso de IA:</b> Na central de alertas, o botão <b>[🤖 Recomendação IA]</b> gera um plano de ação executivo para resolver as pendências listadas.
    </li>
</ul>

<h3>1.2 Painel de Pesquisa Expandido</h3>
<p>Visão panorâmica de todos os contratos cadastrados.</p>
<ul>
    <li><b>Busca Inteligente:</b> Filtra por qualquer campo (Número, Prestador, CNPJ, Objeto).</li>
    <li><b>Ordenação:</b> Clique no cabeçalho das colunas para organizar A-Z ou Z-A.</li>
    <li><b>Ação:</b> Clique duplo abre o contrato. Clique direito abre opções rápidas.</li>
</ul>

<hr>

<h2>2. DETALHAMENTO DA BARRA DE MENUS</h2>

<h3>2.1 Menu ARQUIVO</h3>
<ul>
    <li><b>Novo Contrato:</b> Inicia o assistente de cadastro.</li>
    <li><b>Trocar Base de Dados:</b> Alterna entre arquivos <code>.json</code> diferentes (ex: separar contratos da Saúde e da Educação).</li>
    <li><b>Fazer Backup de Segurança (.bak):</b> Cria uma cópia permanente com data/hora. Use antes de fechamentos.</li>
    <li><b>Salvar Tudo (<kbd>Ctrl</kbd>+<kbd>S</kbd>):</b> Gravação forçada em disco.</li>
</ul>

<h3>2.2 Menu EDITAR (Segurança de Dados)</h3>
<div class="box-security">
    <b>Comando: Desfazer Última Exclusão/Importação (Ctrl+Alt+Z)</b><br>
    O sistema cria automaticamente um "Ponto de Restauração" oculto antes de ações de alto risco:
    <ul>
        <li>Exclusão de Contratos, NEs, Serviços ou Aditivos.</li>
        <li>Importação de dados em lote (CSV).</li>
    </ul>
    Se algo for apagado indevidamente, vá em <b>Editar > Desfazer Última Exclusão/Importação</b> para voltar no tempo.
    <br><i>Nota: A criação manual de registros simples não gera ponto de restauração individual para manter a performance.</i>
</div>

<h3>2.3 Menu EXIBIR</h3>
<ul>
    <li><b>Painel de Pesquisa:</b> Retorna à tela inicial.</li>
    <li><b>Alternar Tema:</b> Modos Claro/Escuro.</li>
    <li><b>Personalizar:</b> Ajuste de cores e tamanho da fonte (Acessibilidade).</li>
</ul>

<h3>2.4 Menu CADASTROS</h3>
<ul>
    <li><b>Gerenciar Prestadores:</b> Base única de empresas. Edite um CNPJ aqui e ele atualiza em todos os contratos vinculados.</li>
    <li><b>Auditoria (Logs):</b> Rastreabilidade completa das ações dos usuários.</li>
</ul>

<h3>2.5 Menu RELATÓRIOS</h3>
<ul>
    <li><b>Geral e Por Serviço:</b> Visões macro e micro da execução financeira.</li>
    <li><b>Evolução Mensal:</b> Gráfico em tabela (Matriz) para análise de sazonalidade.</li>
    <li><b>Caderno de NEs:</b> Extrato bancário detalhado de cada empenho.</li>
</ul>

<h3>2.6 Menu FERRAMENTAS</h3>
<ul>
    <li><b>Verificar Integridade:</b> Diagnóstico do banco de dados.</li>
    <li><b>Assistente de Importação:</b> Carga em lote via CSV (Gera ponto de restauração automático).</li>
    <li><b>Sincronizar Nuvem:</b> Enviar (Sobrescrever) ou Mesclar (Colaborativo).</li>
</ul>

<hr>

<h2>3. GESTÃO OPERACIONAL (TELA DE DETALHES)</h2>

<h3>3.1 Aba 1: DADOS</h3>
<p>Resumo estático da licitação e tabela sumária dos tetos financeiros de cada ciclo.</p>

<h3>3.2 Aba 2: FINANCEIRO (Execução)</h3>
<ul>
    <li><b>Barra de Busca:</b> Filtre NEs por número, valor ou descrição.</li>
    <li><b>Botões [+ NE] / [Pagar] / [Anular]:</b> Operações financeiras básicas.</li>
    <div class="box-ai">
        <b>[Analisar Risco]:</b> Aciona a IA para ler o Ciclo Atual e calcular riscos de execução (déficit ou sobra excessiva).
    </div>
    <li><b>Maximizar Histórico:</b> Visualização focada do extrato da NE.</li>
</ul>

<h3>3.3 Aba 3: SERVIÇOS (Orçamento)</h3>
<p>Monitoramento dos tetos por item de despesa.</p>

<h4>3.3.1 Detalhamento Avançado (Janela Filha)</h4>
<p>Dê <b>duplo clique</b> em um serviço para abrir:</p>
<ul>
    <li><b>Evolução Mensal:</b> Matriz de pagamentos.</li>
    <li><b>Árvore de NEs:</b> Visualização hierárquica (NE -> Pagamentos).</li>
    <div class="box-ai">
        <b>[🤖 Analisar Este Serviço]:</b> A IA audita especificamente o histórico deste item em busca de anomalias (ex: pagamentos duplicados).
    </div>
</ul>

<h3>3.4 Aba 4: ADITIVOS</h3>
<ul>
    <li><b>Aditivo de Valor:</b> Ajusta o teto do ciclo atual.</li>
    <li><b>Aditivo de Prazo (Renovação):</b> Encerra o ciclo atual e cria um novo (zera saldos).</li>
</ul>

<hr>

<h2 style='background-color: #c0392b; color: white; padding: 5px;'>4. REGRAS DE BLOQUEIO E SEGURANÇA</h2>

<table border="1" cellpadding="5" cellspacing="0">
    <tr style="background-color: #f2f2f2;">
        <th>Ação</th>
        <th>Comportamento do Sistema</th>
    </tr>
    <tr>
        <td><b>Emitir NE</b></td>
        <td>Bloqueia se <code>Valor > Saldo Livre do Serviço</code> no ciclo.</td>
    </tr>
    <tr>
        <td><b>Pagar</b></td>
        <td>Bloqueia se <code>Valor > Saldo da NE</code>.</td>
    </tr>
    <tr>
        <td><b>Excluir</b></td>
        <td>Gera Ponto de Restauração automático antes de apagar registros críticos.</td>
    </tr>
</table>

<p style='text-align: right; font-size: 10px; color: #555; margin-top: 50px;'>Documentação gerada internamente pelo sistema GC Gestor.</p>
"""