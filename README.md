🚜 PreparaCalda Pro - Edição Campo (Offline WASM)
Este repositório contém a implementação Edge Computing do PreparaCalda Pro. O sistema utiliza WebAssembly (WASM) para executar o interpretador Python 3.11 diretamente no hardware do dispositivo móvel, garantindo operação em locais sem conectividade (Modo Avião).

🧪 Tecnologias e Conceitos de ADS
Motor gráfico: stlite (Streamlit + Pyodide).
Runtime: WebAssembly para execução de código nativo no navegador.
Persistência: SQLite 3 integrado ao Virtual File System (VFS) do navegador.
UI/UX: Design adaptativo (Mobile-First) com alto contraste para visibilidade em campo.
📂 Estrutura de Implantação
index.html: Wrapper em JavaScript que gerencia o ciclo de vida do ambiente WASM e injeta as configurações do tema.
app_offline.py: Lógica de negócio em Python, otimizada para evitar requisições de rede.
preparacalda2.db: Banco de dados relacional contendo inteligência de misturas químicas.
🚀 Como Instalar no Smartphone (PWA)
Para garantir o funcionamento 100% offline, siga este protocolo:

Sincronização: Acesse a URL do projeto via Safari (iOS) ou Chrome (Android) com internet.
Download do Runtime: Aguarde o carregamento inicial (o navegador baixará o núcleo do Python e a biblioteca Pandas).
Instalação Local:
iOS: Toque em Compartilhar> Adicionar à Tela de Início.
Android: Toque nos três pontos > Instalar Aplicativo.
Uso em Campo: Uma vez instalado, o aplicativo pode ser aberto sem internet. O Service Worker recuperará todos os binários do cache local.
🛠️ Manutenção e Atualização
Sempre que o arquivo app_offline.pyou o banco de dados foram alterados no GitHub:

O cache do navegador detectará uma mudança na próxima vez que houver conexão.
O sistema atualizará automaticamente os binários locais.
🎓 Créditos
Desenvolvido como projeto prático para o curso de Análise e Desenvolvimento de Sistemas (ADS) - IF Sertão Campus Petrolina.

👨‍🎓 Desenvolvedor Estudante : André Lucas
Foco: Praticidade, Segurança Química e Autonomia Tecnológica no Semiárido.
