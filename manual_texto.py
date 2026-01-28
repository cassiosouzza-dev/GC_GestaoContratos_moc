# ARQUIVO: manual_texto.py
# Documentação Técnica Oficial - GC Gestor Enterprise v9.0

HTML_MANUAL = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Manual Técnico Operacional - GC Gestor</title>
    <style>
        :root {
            --primary-color: #0078d7; /* Azul Windows */
            --secondary-color: #2c3e50;
            --accent-color: #27ae60;
            --danger-color: #c0392b;
            --bg-color: #f9f9f9;
            --text-color: #333;
            --border-color: #ddd;
        }

        body {
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: var(--text-color);
            background-color: var(--bg-color);
            margin: 0;
            padding: 30px;
        }

        /* Títulos */
        h1 {
            color: var(--secondary-color);
            text-align: center;
            border-bottom: 3px solid var(--primary-color);
            padding-bottom: 15px;
            font-size: 2.2em;
            margin-bottom: 40px;
        }

        h2 {
            background-color: var(--secondary-color);
            color: #fff;
            padding: 10px 15px;
            border-radius: 5px;
            margin-top: 40px;
            font-size: 1.5em;
            display: flex;
            align-items: center;
        }

        h3 {
            color: var(--primary-color);
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 5px;
            margin-top: 25px;
        }

        /* Sanfona (Details/Summary) */
        details {
            background-color: #fff;
            border: 1px solid var(--border-color);
            border-radius: 5px;
            margin-bottom: 15px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            transition: all 0.3s ease;
        }

        details[open] {
            border-left: 5px solid var(--primary-color);
        }

        summary {
            padding: 15px;
            cursor: pointer;
            font-weight: bold;
            font-size: 1.1em;
            list-style: none;
            background-color: #ffffff;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-radius: 5px;
        }

        summary:hover {
            background-color: #f0f8ff;
        }

        summary::after {
            content: '+';
            font-weight: bold;
            color: var(--primary-color);
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
            padding: 20px;
            background-color: #fff;
            border-radius: 0 0 5px 5px;
        }

        /* Elementos Visuais */
        .btn-sim {
            display: inline-block;
            padding: 2px 8px;
            background-color: #e0e0e0;
            border: 1px solid #999;
            border-radius: 4px;
            font-family: monospace;
            font-weight: bold;
            color: #333;
            font-size: 0.9em;
        }

        .badge {
            background-color: var(--primary-color);
            color: white;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.8em;
            vertical-align: middle;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            font-size: 0.95em;
        }

        th, td {
            border: 1px solid var(--border-color);
            padding: 8px 12px;
            text-align: left;
        }

        th {
            background-color: #f1f1f1;
            color: var(--secondary-color);
        }

        tr:nth-child(even) {
            background-color: #f9f9f9;
        }

        /* Caixas de Destaque */
        .box-warning {
            background-color: #fff3e0;
            border-left: 5px solid #e67e22;
            padding: 15px;
            margin: 15px 0;
        }

        .box-tip {
            background-color: #e8f6f3;
            border-left: 5px solid #27ae60;
            padding: 15px;
            margin: 15px 0;
        }

        .box-code {
            background-color: #2d3436;
            color: #dfe6e9;
            padding: 15px;
            font-family: monospace;
            border-radius: 5px;
            overflow-x: auto;
        }

        .breadcrumbs {
            font-size: 0.9em;
            color: #7f8c8d;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>

    <h1>MANUAL TÉCNICO OPERACIONAL (MTO)<br><small style="font-size: 0.5em; color: #7f8c8d;">GC Gestor Enterprise v9.0</small></h1>

    <div class="box-tip">
        <strong>👋 Bem-vindo!</strong><br>
        Este manual é interativo. Clique nos tópicos abaixo para expandir e ver os detalhes. 
        Recomendamos ler a seção "Conceitos Fundamentais" antes de começar a operar.
    </div>

    <h2>1. CONCEITOS FUNDAMENTAIS</h2>

    <details open>
        <summary>1.1. O Princípio dos Ciclos Financeiros</summary>
        <div class="content">
            <p>Diferente de planilhas simples de Excel, o GC Gestor foi desenhado para respeitar o <b>Princípio da Anualidade Orçamentária</b> do setor público.</p>

            <p>Um contrato não é uma linha infinita de tempo. Ele é dividido em "gavetas" chamadas <b>Ciclos</b>:</p>
            <ul>
                <li><b>Ciclo 0 (Contrato Inicial):</b> É o período original do contrato (geralmente 12 meses). O saldo deste ciclo é definido pelo valor inicial da licitação.</li>
                <li><b>Ciclos Subsequentes (Renovações):</b> Quando você faz um Aditivo de Prazo com Renovação de Valor, o sistema cria automaticamente uma nova "gaveta" (Ciclo 1, Ciclo 2...).</li>
            </ul>

            <div class="box-warning">
                <b>Por que isso é importante?</b><br>
                Ao emitir uma Nota de Empenho (NE), você deve selecionar a qual <b>Ciclo</b> ela pertence. O sistema impede que você use o saldo do Ano 1 para pagar uma despesa do Ano 2, garantindo conformidade fiscal.
            </div>



            <p>Na tela de detalhes do contrato, há uma caixa de seleção no topo (ComboBox) que permite "viajar no tempo" e ver os saldos de cada ciclo separadamente.</p>
        </div>
    </details>

    <details>
        <summary>1.2. Estrutura Hierárquica dos Dados</summary>
        <div class="content">
            <p>O sistema organiza os dados na seguinte estrutura de dependência:</p>
            <ol>
                <li><b>Prestador (Empresa):</b> A entidade raiz. Possui CNPJ, Razão Social, etc.</li>
                <li><b>Contrato:</b> Vinculado a um prestador. Possui número, vigência e regras.</li>
                <li><b>Serviços (Subcontratos):</b> São os itens do contrato (ex: "Locação de Veículo", "Plantão Médico"). O orçamento é definido aqui.</li>
                <li><b>Notas de Empenho (NE):</b> São a reserva do dinheiro. Uma NE deve ser obrigatoriamente vinculada a um Serviço e a um Ciclo.</li>
                <li><b>Movimentações:</b> São os <b>Pagamentos</b> (liquidações) ou <b>Anulações</b> feitos dentro de uma NE.</li>
            </ol>
            <p>Essa estrutura permite relatórios de "Gasto por Serviço" extremamente precisos.</p>
        </div>
    </details>

    <h2>2. INSTALAÇÃO E CONFIGURAÇÃO TÉCNICA</h2>

    <details>
        <summary>2.1. Arquivos Necessários</summary>
        <div class="content">
            <p>O sistema funciona em modo "Portable" (não requer instalação no Windows, apenas execução). Para o funcionamento completo (Enterprise), a pasta do executável deve conter:</p>
            <table border="1">
                <tr><th>Arquivo</th><th>Função</th><th>Obrigatório?</th></tr>
                <tr><td><code>gestao_contratos.exe</code></td><td>O programa principal.</td><td>Sim</td></tr>
                <tr><td><code>dados_sistema.json</code></td><td>O banco de dados local. Se não existir, o sistema cria um vazio.</td><td>Sim</td></tr>
                <tr><td><code>chave_api.txt</code></td><td>Contém a chave da IA (Google Gemini). Sem ele, o chat e a análise de risco não funcionam.</td><td>Não (Recomendado)</td></tr>
                <tr><td><code>credentials.json</code></td><td>Credenciais de API do Google Drive para sincronização na nuvem.</td><td>Não (Recomendado)</td></tr>
                <tr><td><code>icon_gc.png</code></td><td>Ícone visual do sistema.</td><td>Não</td></tr>
            </table>
        </div>
    </details>

    <details>
        <summary>2.2. Configurando a Inteligência Artificial (Gemini)</summary>
        <div class="content">
            <p>Para ativar o botão <b>[💬 IA]</b> e a <b>Análise de Risco</b>, siga os passos:</p>
            <ol>
                <li>Acesse o <b>Google AI Studio</b> (<a href="https://aistudio.google.com/app/apikey" target="_blank">aistudio.google.com/app/apikey</a>).</li>
                <li>Faça login com uma conta Google.</li>
                <li>Clique em <b>Create API Key</b>.</li>
                <li>Copie a string gerada (começa geralmente com "AIza...").</li>
                <li>Na pasta do sistema, crie um arquivo de texto chamado <code>chave_api.txt</code>.</li>
                <li>Cole a chave dentro dele e salve.</li>
                <li>Reinicie o sistema. A barra de status mostrará "✅ IA Online".</li>
            </ol>
        </div>
    </details>

    <details>
        <summary>2.3. Configurando a Nuvem (Google Drive)</summary>
        <div class="content">
            <p>Para permitir que múltiplos usuários compartilhem a mesma base de dados via nuvem:</p>
            <ol>
                <li>Vá ao <b>Google Cloud Console</b>.</li>
                <li>Crie um projeto e ative a <b>Google Drive API</b>.</li>
                <li>Configure a "Tela de Consentimento OAuth" (adicione os e-mails dos usuários como testadores).</li>
                <li>Crie uma credencial do tipo "OAuth Client ID" (Desktop App).</li>
                <li>Baixe o JSON da credencial e renomeie para <code>credentials.json</code>.</li>
                <li>Coloque esse arquivo na pasta do sistema de todos os usuários.</li>
            </ol>
            <div class="box-tip">Na primeira vez que você clicar em "Sincronizar", o navegador abrirá pedindo permissão de acesso ao Drive.</div>
        </div>
    </details>

    <h2>3. GUIA DE OPERAÇÃO DIÁRIA</h2>

    <details>
        <summary>3.1. Tela Inicial e Pesquisa</summary>
        <div class="content">
            <p>A tela inicial é seu painel de controle. A barra de busca central é "Omni-search", ou seja, procura em tudo ao mesmo tempo:</p>
            <ul>
                <li>Número do Contrato.</li>
                <li>Número da Nota de Empenho (NE).</li>
                <li>Nome Fantasia ou Razão Social do Prestador.</li>
                <li>CNPJ ou CPF.</li>
                <li>Descrição do Objeto.</li>
            </ul>
            <p><b>Dica de Uso:</b> Se você digitar o número de uma NE específica, o sistema mostrará o contrato relacionado e destacará que encontrou uma NE. Ao clicar duas vezes, ele abrirá o contrato já focado na aba Financeiro e com a NE selecionada.</p>
        </div>
    </details>

    <details>
        <summary>3.2. Cadastrando um Novo Contrato</summary>
        <div class="content">
            <div class="breadcrumbs">Menu: Arquivo > Novo Contrato ou Botão "+ Novo Contrato"</div>
            <p>Ao abrir a tela de cadastro:</p>
            <ol>
                <li><b>Número:</b> Use o formato padrão do seu órgão (ex: 123/2025).</li>
                <li><b>Prestador:</b> É uma caixa de seleção. O sistema exige que o prestador já esteja cadastrado previamente. Isso evita erros de digitação (ex: "Empresa X" vs "Empresa X Ltda").</li>
                <li><b>Valor Inicial:</b> Insira o valor global do contrato. Este valor será o teto do "Ciclo 0".</li>
                <li><b>Vigência e Competências:</b> Defina as datas de início e fim. O sistema calcula automaticamente os alertas de vencimento com base nisso.</li>
            </ol>
        </div>
    </details>

    <details>
        <summary>3.3. Aba Financeiro: Empenhos e Pagamentos</summary>
        <div class="content">
            <p>Esta é a aba mais importante. Ela é dividida em duas tabelas: Superior (Lista de NEs) e Inferior (Histórico da NE selecionada).</p>

            <h4>Criar Nota de Empenho (+ NE)</h4>
            <p>Você deve informar:</p>
            <ul>
                <li><b>Ciclo Financeiro:</b> De qual "ano/gaveta" o dinheiro vai sair.</li>
                <li><b>Serviço:</b> A qual item do contrato essa NE se refere (o sistema valida se há saldo no serviço).</li>
                <li><b>Fonte de Recurso:</b> Apenas informativo.</li>
                <li><b>Valor:</b> O valor bloqueado.</li>
            </ul>

            <h4>Realizar Pagamento (Liquidação)</h4>
            <ol>
                <li>Selecione a NE na tabela superior.</li>
                <li>Clique no botão verde <b>Pagar</b>.</li>
                <li>Selecione as competências (meses) a que se refere o pagamento na lista. Você pode marcar várias.</li>
                <li>Informe o valor e uma observação.</li>
            </ol>
            <p>O saldo da NE será reduzido e o percentual de execução do contrato aumentará.</p>

            <h4>Anular (Estorno)</h4>
            <p>Use o botão vermelho <b>Anular</b> para devolver saldo para a NE. Isso é usado quando uma NE foi emitida a maior ou o serviço não foi prestado. O valor "Pago" diminui e o "Saldo" aumenta.</p>
        </div>
    </details>

    <details>
        <summary>3.4. Aba Serviços e Aditivos</summary>
        <div class="content">
            <h4>Aba Serviços</h4>
            <p>Aqui você define <b>no que</b> o dinheiro pode ser gasto. Cada serviço tem um "Valor Mensal" estimado.</p>
            <p>Ao criar um serviço, você pode definir se o valor dele se aplica apenas ao ciclo atual ou se deve ser replicado para todos os ciclos do contrato.</p>

            <h4>Aba Aditivos</h4>
            <p>Gerencia alterações contratuais:</p>
            <ul>
                <li><b>Aditivo de Valor:</b> Aumenta ou diminui o teto do contrato. Exige vínculo com um serviço.</li>
                <li><b>Aditivo de Prazo (Renovação):</b> Estende a vigência. Se a opção <i>"Haverá renovação de valor?"</i> for marcada, o sistema <b>cria um novo Ciclo Financeiro</b> e zera os empenhos para o novo período, preservando o histórico do anterior.</li>
            </ul>
        </div>
    </details>

    <h2>4. SINCRONIZAÇÃO EM NUVEM (ENTERPRISE)</h2>

    <details>
        <summary>4.1. O Painel de Sincronização</summary>
        <div class="content">
            <div class="breadcrumbs">Menu: Ferramentas > Sincronizar com Google Drive</div>
            <p>O sistema possui um motor robusto de resolução de conflitos. As opções são:</p>

            <h4>1. ⬇️⬆️ Sincronizar Tudo (Recomendado)</h4>
            <p>É o modo inteligente. Ele realiza três passos:</p>
            <ol>
                <li><b>Baixa:</b> Pega o arquivo da nuvem e compara com o seu.</li>
                <li><b>Mescla:</b> Se um colega criou um contrato novo, ele aparece pra você. Se você criou um, ele vai para a nuvem. Se ambos editaram o mesmo contrato, o sistema usa a data de modificação mais recente.</li>
                <li><b>Sobe:</b> Envia o resultado final consolidado para a nuvem.</li>
            </ol>

            <h4>2. ⬇️ Apenas Importar (Mesclar Localmente)</h4>
            <p>Traz as novidades da nuvem para o seu computador, mas <b>NÃO</b> envia suas alterações de volta. Use isso se quiser apenas atualizar seu sistema sem risco de alterar o trabalho dos outros.</p>

            <h4>3. ⬆️ Apenas Subir (Sobrescrever Nuvem)</h4>
            <p>Pega o seu banco de dados e joga na nuvem. O sistema tenta preservar dados que existam lá e não no seu (merge), mas a sua versão tem prioridade total.</p>

            <h4>4. ⚠️ Resetar Nuvem</h4>
            <p>Apaga o arquivo do Google Drive e faz upload da sua versão local. Use apenas em casos extremos onde a nuvem esteja corrompida.</p>
        </div>
    </details>

    <details>
        <summary>4.2. Importação em Lote (CSV)</summary>
        <div class="content">
            <p>Se você tem dados legados em Excel, pode importá-los em massa.</p>
            <p>Os arquivos CSV devem usar <b>ponto e vírgula (;)</b> como separador.</p>
            <div class="box-code">
                <b>Layout para Contratos:</b><br>
                Numero;Prestador;Objeto;Valor;VigInicio;VigFim;CompInicio;CompFim;Licitacao;Dispensa<br><br>
                <b>Layout para Empenhos:</b><br>
                NE;Valor;Descricao;NomeDoServico;Fonte;DataEmissao
            </div>
            <p>Vá em <i>Ferramentas > Assistente de Importação</i> para utilizar.</p>
        </div>
    </details>

    <h2>5. PERSONALIZAÇÃO E EXTRAS</h2>

    <details>
        <summary>5.1. Temas e Aparência</summary>
        <div class="content">
            <div class="breadcrumbs">Menu: Exibir > Personalizar Cores e Fontes</div>
            <p>O sistema vem com o tema padrão <b>Claro (Corporate Blue)</b>. Você pode alterar para:</p>
            <ul>
                <li><b>Modo Escuro (Slate):</b> Um tema cinza-chumbo moderno para descanso visual.</li>
                <li><b>Dracula / Ocean / Matrix:</b> Temas coloridos de alto contraste.</li>
                <li><b>Personalizado:</b> Você pode escolher a cor exata de fundo, seleção, cabeçalhos de tabela e tamanho da fonte.</li>
            </ul>
        </div>
    </details>

    <details>
        <summary>5.2. Sistema de Segurança (Undo/Reforço)</summary>
        <div class="content">
            <p><b>Desfazer (Ctrl+Alt+Z):</b> O sistema cria um "ponto de restauração" oculto antes de qualquer operação crítica (como excluir um contrato ou importar um CSV). Se você errar, use o menu <i>Editar > Desfazer</i> para voltar no tempo.</p>
            <p><b>Backup Manual (.bak):</b> No menu Arquivo, você pode gerar uma cópia timestamped (com data e hora) do banco de dados na mesma pasta do sistema.</p>
        </div>
    </details>

    <h2>6. RESOLUÇÃO DE PROBLEMAS (FAQ)</h2>

    <details>
        <summary>6.1. O sistema não abre ou fecha sozinho</summary>
        <div class="content">
            <ul>
                <li>Verifique se o arquivo <code>dados_sistema.json</code> está corrompido. Tente renomeá-lo para .old e abrir o sistema (ele criará um novo).</li>
                <li>Verifique se há algum antivírus bloqueando o executável.</li>
            </ul>
        </div>
    </details>

    <details>
        <summary>6.2. A IA diz "Indisponível"</summary>
        <div class="content">
            <ul>
                <li>Verifique se o arquivo <code>chave_api.txt</code> existe na pasta.</li>
                <li>Abra o arquivo e verifique se não há espaços em branco antes ou depois da chave.</li>
                <li>Verifique sua conexão com a internet.</li>
            </ul>
        </div>
    </details>

    <details>
        <summary>6.3. Erro ao Sincronizar: "Token Expired" ou "Auth Error"</summary>
        <div class="content">
            <p>Isso acontece quando a permissão do Google Drive expira.</p>
            <ol>
                <li>Feche o sistema.</li>
                <li>Vá na pasta do sistema e apague o arquivo <code>token.json</code> (se existir). NÃO apague o credentials.json.</li>
                <li>Abra o sistema e tente sincronizar novamente. O navegador pedirá login mais uma vez.</li>
            </ol>
        </div>
    </details>

    <br><br>
    <div style="text-align: center; color: #aaa; font-size: 0.8em; border-top: 1px solid #eee; padding-top: 20px;">
        GC Gestor de Contratos Enterprise &copy; 2025<br>
        Desenvolvido com Python, PyQt6 e Google Gemini AI.
    </div>

</body>
</html>
"""