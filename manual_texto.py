# manual_texto.py
# MTO - Manual Técnico Operacional do Sistema GC Gestor de Contratos v3.2

HTML_MANUAL = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; background-color: #f9f9f9; padding: 20px; }
        h1 { color: #2c3e50; border-bottom: 3px solid #2c3e50; padding-bottom: 10px; text-transform: uppercase; font-size: 28px; margin-top: 0; }
        h2 { color: #2980b9; border-left: 5px solid #2980b9; padding-left: 10px; margin-top: 40px; font-size: 22px; background-color: #e8f4f8; padding-top: 5px; padding-bottom: 5px; }
        h3 { color: #16a085; margin-top: 25px; font-size: 18px; border-bottom: 1px solid #ddd; padding-bottom: 5px; }
        h4 { color: #7f8c8d; font-size: 16px; margin-top: 15px; font-weight: bold; }
        p { margin-bottom: 15px; text-align: justify; }
        ul { margin-bottom: 15px; }
        li { margin-bottom: 8px; }
        code { background-color: #f0f0f0; padding: 2px 5px; border-radius: 3px; font-family: 'Consolas', monospace; color: #c0392b; font-size: 0.9em; }
        .note { background-color: #fff3cd; border: 1px solid #ffeeba; padding: 15px; border-radius: 5px; margin: 20px 0; color: #856404; }
        .technical { background-color: #d4edda; border: 1px solid #c3e6cb; padding: 15px; border-radius: 5px; margin: 20px 0; color: #155724; font-size: 0.95em; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 0.9em; }
        th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
        th { background-color: #2c3e50; color: white; }
        tr:nth-child(even) { background-color: #f2f2f2; }
        .breadcrumbs { font-size: 0.85em; color: #777; margin-bottom: 30px; }
    </style>
</head>
<body>

    <div class="breadcrumbs">GC Gestor > Documentação > Manual Técnico Operacional (v3.2)</div>

    <h1>Manual Técnico Operacional - GC Gestor v3.2</h1>
    <p><strong>Última Atualização:</strong> Fevereiro de 2026</p>
    <p>Este documento constitui a referência oficial para operação, manutenção e auditoria do sistema <em>GC Gestor de Contratos</em>. O software foi desenvolvido para o controle integral do ciclo de vida de contratos públicos, abrangendo desde a fase de licitação até a execução financeira, incluindo aditivos, apostilamentos e integração com ferramentas de inteligência artificial.</p>

    <h2>1. Introdução e Arquitetura</h2>
    <p>O GC Gestor é uma aplicação <em>desktop</em> desenvolvida em Python, utilizando a biblioteca gráfica PyQt6. A persistência de dados é realizada através de um banco de dados relacional SQLite local, garantindo alta performance e independência de servidores dedicados para operações básicas. O sistema opera com uma arquitetura híbrida, permitindo o trabalho offline com sincronização posterior via API do Google Drive.</p>

    <div class="technical">
        <strong>Especificações Técnicas:</strong>
        <ul>
            <li>Linguagem: Python 3.x</li>
            <li>Interface Gráfica: PyQt6 (Qt Framework)</li>
            <li>Banco de Dados: SQLite3 (Arquivo .db criptografado logicamente via aplicação)</li>
            <li>IA: Integração via Google Generative AI (Gemini 1.5)</li>
            <li>Nuvem: Google Drive API v3 (OAuth2)</li>
        </ul>
    </div>

    <h2>2. Acesso, Segurança e Autenticação</h2>

    <h3>2.1. Credenciais e Login</h3>
    <p>O acesso ao sistema é restrito a usuários cadastrados. O identificador único é o CPF, garantindo unicidade na auditoria de logs. As senhas são armazenadas utilizando <em>hashing</em> criptográfico (SHA-256), impedindo a leitura direta mesmo em caso de acesso ao banco de dados.</p>
    <ul>
        <li><strong>Primeiro Acesso (Admin):</strong> Caso o banco de dados esteja vazio, o sistema permite a criação de um usuário Administrador inicial.</li>
        <li><strong>Lembrar Credenciais:</strong> A opção "Lembrar meu CPF" armazena apenas o identificador em um arquivo de configuração local (<em>config.json</em>), jamais a senha.</li>
    </ul>

    <h3>2.2. Recuperação de Senha</h3>
    <p>O sistema implementa um mecanismo de recuperação autônomo baseado em uma "Palavra Secreta" definida pelo usuário no ato do cadastro. Não há envio de e-mail. Para redefinir a senha:</p>
    <ol>
        <li>Na tela de login, selecione "Esqueci minha senha".</li>
        <li>Informe o CPF e a Palavra Secreta exata cadastrada.</li>
        <li>Defina a nova senha. A alteração é registrada imediatamente no banco de dados.</li>
    </ol>

    <h2>3. Interface do Usuário e Navegação</h2>
    <p>A interface foi projetada seguindo o padrão MDI (<em>Multiple Document Interface</em>) adaptado para abas e painéis empilhados.</p>

    <h3>3.1. Barra de Ferramentas (Toolbar)</h3>
    <p>Localizada no topo da aplicação, oferece acesso rápido às funções mais críticas:</p>
    <table>
        <tr><th>Ferramenta</th><th>Descrição Funcional</th></tr>
        <tr><td><strong>Início</strong></td><td>Retorna ao painel de pesquisa global de contratos, limpando a seleção ativa.</td></tr>
        <tr><td><strong>Novo Contrato</strong></td><td>Abre o formulário para cadastro de um novo instrumento contratual.</td></tr>
        <tr><td><strong>Salvar Tudo</strong></td><td>Força a gravação imediata do estado da memória para o disco (Commit no SQLite).</td></tr>
        <tr><td><strong>Backup Local</strong></td><td>Gera uma cópia instantânea do arquivo .db com carimbo de data/hora (Timestamp) na mesma pasta do executável.</td></tr>
        <tr><td><strong>Prestadores</strong></td><td>Abre o módulo de gestão de empresas credoras (CRUD).</td></tr>
        <tr><td><strong>Prazos</strong></td><td>Abre o Monitor de Vigência, exibindo alertas visuais baseados na proximidade do fim do contrato.</td></tr>
        <tr><td><strong>Saldos NE</strong></td><td>Abre o Monitor Global de Empenhos, permitindo análise transversal de saldo por fonte ou serviço.</td></tr>
        <tr><td><strong>Filtrar Tags</strong></td><td>Permite selecionar categorias (ex: "TI", "Obras") para restringir a lista de contratos visíveis.</td></tr>
        <tr><td><strong>Sincronizar</strong></td><td>Inicia o módulo de conexão com o Google Drive para Upload/Download/Merge de dados.</td></tr>
        <tr><td><strong>IA Gemini</strong></td><td>Abre o chat interativo com a Inteligência Artificial para perguntas sobre a base de dados.</td></tr>
        <tr><td><strong>Calculadora</strong></td><td>Invoca a calculadora nativa do sistema operacional.</td></tr>
        <tr><td><strong>Lixeira</strong></td><td>Acesso aos registros marcados como "Anulados" (Soft Delete).</td></tr>
        <tr><td><strong>Notificações (Sino)</strong></td><td>Central de alertas automáticos (Vencimentos, Déficit Orçamentário).</td></tr>
    </table>

    <h3>3.2. Menu Principal</h3>
    <p>O menu superior expande as funcionalidades da toolbar, oferecendo opções de manutenção e relatórios.</p>
    <ul>
        <li><strong>Arquivo:</strong> Troca de base de dados, alteração de senha e logout.</li>
        <li><strong>Editar:</strong> Comandos de área de transferência e o comando global "Desfazer" (Undo).</li>
        <li><strong>Exibir:</strong> Personalização de temas (Cores/Fontes) e alternância de painéis.</li>
        <li><strong>Cadastros:</strong> Acesso direto às tabelas mestras e Logs de Auditoria.</li>
        <li><strong>Relatórios:</strong> Geração de documentos HTML/PDF (Geral, Por Serviço, Evolução Mensal, Extrato de NE).</li>
        <li><strong>Ferramentas:</strong> Assistentes de Importação em Lote (CSV) e Arquivamento de Contratos Antigos.</li>
        <li><strong>Ajuda:</strong> Acesso a este manual e configurações de conectividade.</li>
    </ul>

    <h2>4. Módulo de Contratos</h2>

    <h3>4.1. Cadastro e Validação</h3>
    <p>O cadastro de um contrato é a entidade raiz do sistema. O formulário exige:</p>
    <ul>
        <li><strong>Número:</strong> Identificador único (Chave Primária Lógica).</li>
        <li><strong>Prestador:</strong> Deve ser selecionado a partir da base de prestadores cadastrados. O sistema exibe automaticamente os badges de CNPJ e CNES ao selecionar.</li>
        <li><strong>Categoria (Tag):</strong> Classificação opcional para filtros rápidos.</li>
        <li><strong>Vigência e Competências:</strong> Define o período legal e o período financeiro (competências de faturamento).</li>
        <li><strong>Sequencial de Início:</strong> Define se o contrato inicia no ciclo "0" (Contrato Inicial) ou se é um contrato legado que já começa no "5º Aditivo", por exemplo.</li>
    </ul>

    <h3>4.2. Estrutura de Ciclos Financeiros</h3>
    <p class="note">Atenção: O conceito de <strong>Ciclo Financeiro</strong> é fundamental para a operação do sistema.</p>
    <p>Um contrato não possui um orçamento único estático. Ele evolui no tempo. Cada renovação (Termo Aditivo de Prazo com Renovação de Valor) cria um novo <strong>Ciclo</strong>.</p>
    <ul>
        <li><strong>Ciclo 0:</strong> Contrato Inicial.</li>
        <li><strong>Ciclo 1:</strong> 1º Termo Aditivo (Renovação).</li>
        <li>...</li>
    </ul>
    <p>Todas as operações financeiras (Orçamento do Serviço, Empenhos, Pagamentos) são vinculadas a um ciclo específico. O usuário deve selecionar o ciclo ativo no topo da tela de detalhes ("Visualizar Ciclo") para filtrar os dados correspondentes.</p>

    <h2>5. Gestão Financeira e Execução</h2>

    <h3>5.1. Notas de Empenho (NE)</h3>
    <p>A NE é o documento que reserva o orçamento. No sistema, a NE deve ser vinculada a:</p>
    <ul>
        <li>Um <strong>Ciclo Financeiro</strong> (de onde sairá o saldo global).</li>
        <li>Um <strong>Serviço/Subcontrato</strong> (para deduzir do teto específico daquele serviço).</li>
        <li>Uma <strong>Fonte de Recurso</strong>.</li>
    </ul>
    <p>O sistema impede a emissão de NE se não houver saldo orçamentário no serviço dentro do ciclo selecionado.</p>

    <h3>5.2. Pagamentos e Rastreabilidade</h3>
    <p>O pagamento é uma "Movimentação" dentro da NE. Ele deduz do saldo da NE.</p>
    <h4>Novo Campo: Link do Processo (1DOC)</h4>
    <p>Ao registrar ou editar um pagamento, existe um campo específico para inserção de URL (Link Web). Este campo é destinado a armazenar o link direto para o processo de pagamento no sistema 1DOC ou Google Drive.</p>
    <ul>
        <li><strong>Visualização:</strong> Na tabela de histórico financeiro (abaixo das NEs) e na tabela maximizada, aparece um ícone de corrente (🔗).</li>
        <li><strong>Ação:</strong> Clicar neste ícone abre automaticamente o navegador padrão do sistema no endereço cadastrado.</li>
    </ul>

    <h3>5.3. Anulações e Bloqueios</h3>
    <ul>
        <li><strong>Anulação:</strong> Reverte um valor empenhado. O saldo retorna para a NE e para o Serviço.</li>
        <li><strong>Bloqueio de NE:</strong> O botão de cadeado (🔒) permite "congelar" uma NE. Uma NE bloqueada não aceita novos pagamentos e seu saldo residual é desconsiderado nos cálculos de "Disponível para Anular" ou "Disponível para Reempenho".</li>
    </ul>

    <h3>5.4. Rateio Automático</h3>
    <p>A função "Ratear Pagamento" permite distribuir um valor único de fatura entre múltiplas Notas de Empenho do mesmo serviço/ciclo. O sistema sugere a distribuição baseada no saldo disponível de cada nota, mas permite ajuste manual.</p>

    <h2>6. Gestão de Serviços (Subcontratos)</h2>
    <p>Os serviços representam os itens contratados (ex: "Serviço de Limpeza", "Locação de Software").</p>
    <p>Cada serviço possui um valor mensal e um valor total <strong>POR CICLO</strong>. Ao criar um novo ciclo (Aditivo), os serviços podem ter seus valores renovados, reajustados ou suprimidos.</p>
    <p><strong>Visão Detalhada (Tree View):</strong> Ao clicar duas vezes em um serviço na aba "Serviços", abre-se uma janela detalhada contendo:</p>
    <ol>
        <li><strong>Evolução Mensal:</strong> Tabela comparativa mês a mês (Meta vs Executado).</li>
        <li><strong>Árvore de Detalhes:</strong> Uma estrutura hierárquica mostrando <em>Serviço > Notas de Empenho > Pagamentos Individuais</em>.</li>
    </ol>

    <h2>7. Alterações Contratuais (Aditivos e Apostilamentos)</h2>
    <p>O sistema suporta quatro tipos de alterações contratuais na aba "Alterações":</p>
    <ul>
        <li><strong>Aditivo de Valor:</strong> Acrescenta saldo ao teto do ciclo atual e a um serviço específico. (Limite legal de 25%).</li>
        <li><strong>Supressão:</strong> Reduz o saldo do contrato. O sistema valida se há saldo suficiente para suprimir.</li>
        <li><strong>Aditivo de Prazo (Prorrogação):</strong> Estende a data de vigência final. Pode ou não renovar o valor (criar novo ciclo).</li>
        <li><strong>Apostilamento (Remanejamento):</strong> Permite retirar saldo de um "Serviço de Origem" e adicionar em um "Serviço de Destino" dentro do mesmo ciclo, sem alterar o valor global do contrato.</li>
    </ul>

    <h2>8. Ferramentas Avançadas e Integrações</h2>

    <h3>8.1. Sincronização com Nuvem (Google Drive)</h3>
    <p>O sistema de sincronização foi projetado com lógica de <strong>Fusão Inteligente (Smart Merge)</strong> com prioridade local.</p>
    <ul>
        <li>O arquivo remoto é <code>dados_gestao_contratos_db.json</code>.</li>
        <li>Ao enviar dados (Upload), o sistema <strong>não apaga</strong> o que está na nuvem cegamente. Ele baixa o mapa de contratos da nuvem, atualiza com os dados locais (sobrescrevendo apenas os contratos que foram modificados localmente) e envia o pacote unificado de volta.</li>
        <li>Isso garante que os dados dos <strong>Serviços</strong> e <strong>Orçamentos por Ciclo</strong> sejam preservados integralmente durante o trânsito de dados.</li>
    </ul>

    <h3>8.2. Importação de Dados (CSV)</h3>
    <p>O sistema possui importadores robustos que tentam detectar automaticamente a codificação do arquivo (UTF-8, Latin-1, CP1252) para evitar erros de acentuação.</p>
    <h4>Especificações para Importação de Pagamentos:</h4>
    <p>O arquivo CSV deve conter estritamente as colunas na ordem:</p>
    <ol>
        <li>Número da NE (Obrigatório - Chave de busca)</li>
        <li>Valor do Pagamento</li>
        <li>Competência (MM/AAAA)</li>
        <li>Observação</li>
        <li><strong>Link do Processo</strong> (Coluna E - Opcional)</li>
    </ol>

    <h4>Especificações para Importação Global de Serviços:</h4>
    <p>Permite carregar serviços para múltiplos contratos de uma vez. Colunas:</p>
    <ol>
        <li>Nº Contrato</li>
        <li>Índice do Ciclo (0, 1, 2...) - <em>Nota: Se o índice for inválido, o sistema tentará alocar no ciclo vigente.</em></li>
        <li>Descrição</li>
        <li>Valor Mensal</li>
        <li>Valor Total</li>
        <li>Replicar? (S/N)</li>
        <li>Fonte</li>
    </ol>

    <h3>8.3. Inteligência Artificial (Gemini 1.5)</h3>
    <p>O módulo de IA atua como um auditor passivo. Ele não altera dados, apenas lê e analisa.</p>
    <ul>
        <li><strong>Chat IA:</strong> Permite perguntas em linguagem natural (ex: "Quais contratos vencem em maio?").</li>
        <li><strong>Análise de Risco:</strong> Na aba Financeiro, o botão "Analisar Risco" envia o contexto financeiro do contrato para a IA, que retorna um parecer sobre a saúde da execução (Déficit, ritmo de gastos, prazos).</li>
    </ul>

    <h2>9. Auditoria e Logs</h2>
    <p>Todas as ações críticas (Criação, Edição, Exclusão, Importação) geram um registro na tabela de Logs.</p>
    <ul>
        <li>O log contém: Data/Hora, Nome do Usuário, CPF, Ação Realizada e Detalhe Técnico.</li>
        <li>Os logs são imutáveis via interface do sistema.</li>
        <li>O recurso "Desfazer Última Exclusão/Importação" (Ctrl+Alt+Z) utiliza um ponto de restauração temporário criado automaticamente antes de operações em lote.</li>
    </ul>

    <h2>10. Manutenção e Atualização</h2>
    <p>O sistema possui um verificador automático de atualizações.</p>
    <ul>
        <li>Ao detectar uma nova versão no repositório remoto, o sistema baixa o executável temporário.</li>
        <li>Ao confirmar a atualização, o sistema executa um comando de encerramento forçado (<code>os._exit</code>) para liberar o arquivo em uso e roda um script <code>.bat</code> externo para substituir o executável antigo pelo novo e reiniciar a aplicação automaticamente.</li>
    </ul>

    <hr>
    <p style="text-align: center; font-size: 0.8em; color: #999;">
        GC Gestor de Contratos - Desenvolvido para Eficiência na Gestão Pública.<br>
        Documentação gerada via código-fonte v3.2
    </p>

</body>
</html>
"""