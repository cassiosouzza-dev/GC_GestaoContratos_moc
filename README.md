# <img src="https://github.com/cassiosouzza-dev/GC_GestaoContratos_moc/raw/master/img/icon_gc.png" width="40" style="vertical-align: middle;"> GCi Gestão de Contratos Inteligente

> **Sistema Corporativo de Gestão Contratual, Financeira e Auditoria.**

![ABA Financeiro](https://github.com/cassiosouzza-dev/GC_GestaoContratos_moc/blob/master/img/contrato_financ.png)

> *Desenvolvido para alta performance, segurança e controle total.*

![Status](https://img.shields.io/badge/Status-Estável-green)
![Versão](https://img.shields.io/badge/Versão-4.3-blue)
![Plataforma](https://img.shields.io/badge/Plataforma-Windows-0078d7)

---

## 🚀 O que é o GC Gestor?

O **GC Gestor** é uma solução completa para administração de contratos públicos e privados. Ele elimina o uso de planilhas dispersas, centralizando dados financeiros, vigências, aditivos e documentos em um único **Workspace Integrado**.

### 🌟 Principais Funcionalidades

* **Workspace Multi-Abas:** Trabalhe em vários contratos simultaneamente sem perder o foco.

![Página Inicial](https://github.com/cassiosouzza-dev/GC_GestaoContratos_moc/blob/master/img/pag_inicial.png)

* **Gestão Financeira:** Controle de saldos de empenho, pagamentos parciais e anulações.
* **BI & Analytics:** Tabelas dinâmicas (Pivot Tables) e gráficos gerados em tempo real.

![Tabela Dinâmica](https://github.com/cassiosouzza-dev/GC_GestaoContratos_moc/blob/master/img/BI.png)

![Gráfico](https://github.com/cassiosouzza-dev/GC_GestaoContratos_moc/blob/master/img/graficos.png)

* **Auditoria IA (Gemini):** Inteligência Artificial integrada para analisar riscos e responder perguntas sobre seus contratos.
* **Nuvem Híbrida:** Sincronização inteligente com Google Drive (trabalhe offline e sincronize depois).
* **Alertas Automáticos:** Notificações de vencimento de prazos e déficit de saldo.

---

## 📥 Como Instalar

Não é necessária instalação complexa. O sistema é **Portátil (Portable)**.

1.  Vá até a aba **[Releases](https://github.com/SEU_USUARIO/GC_GestaoContratos_moc/releases)** aqui no topo da página.
2.  Baixe o arquivo mais recente: `GC_Gestor.exe`.
3.  Coloque o arquivo em uma pasta de sua preferência (Ex: `Meus Documentos/Sistema GC`).
4.  Execute o arquivo.

> **Nota:** No primeiro acesso, utilize o usuário `Administrador` (se for uma instalação limpa) ou restaure seu backup.

---

## 📖 Manual de Uso Rápido

### 1. A Tela Inicial (Workspace)
Ao abrir, você verá a **Barra de Pesquisa Global**.
* Digite o número do contrato, nome do prestador ou NE.
* **Dê um duplo clique** no resultado para abrir uma aba exclusiva para aquele contrato.

### 2. Cadastrando um Contrato
1.  Clique no botão **Novo Contrato** na barra superior.
2.  Preencha os dados básicos. O sistema valida automaticamente o formato do CNPJ.
3.  **Dica:** Use a aba "Serviços" para definir o orçamento de cada item do contrato.

### 3. Lançando Pagamentos
1.  Dentro da aba do contrato, vá em **Financeiro**.
2.  Selecione a Nota de Empenho (NE) desejada.
3.  Clique em **+ Pagamento**.
4.  O sistema calcula automaticamente o saldo restante e impede pagamentos que excedam o valor.

### 4. Usando a Inteligência Artificial
1.  Clique no botão **IA Gemini** na barra de ferramentas.
2.  Pergunte coisas como:
    * *"Qual contrato vence este mês?"*
    * *"Resuma a situação financeira da empresa X"*
3.  A IA analisará sua base de dados local e responderá instantaneamente.

---

## 📂 Estrutura de Pastas

Para o funcionamento correto das integrações, mantenha os seguintes arquivos na mesma pasta do executável:

* `GC_Gestor.exe`: O sistema principal.
* `dados_sistema.db`: Seu banco de dados (o sistema cria automaticamente se não existir).
* `chave_api.txt`: (Opcional) Sua chave da API do Google Gemini.
* `credentials.json`: (Opcional) Para sincronização com Google Drive.

---

## 📞 Suporte

Em caso de dúvidas técnicas ou sugestões de melhoria:

* **Desenvolvedor:** Cássio de Souza Lopes
* **E-mail:** cassio.souzza@gmail.com

---

*© 2024-2026 GC Gestor. Todos os direitos reservados.*
