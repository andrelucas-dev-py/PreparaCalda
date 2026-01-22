# 🚜 PreparaCalda Pro - Edição Campo (Offline WASM)

Este repositório contém a implementação **Edge Computing** do PreparaCalda Pro. O sistema utiliza **WebAssembly (WASM)** para executar o interpretador Python 3.11 diretamente no hardware do dispositivo móvel, garantindo operação em locais sem conectividade (Modo Avião).

## 🧪 Tecnologias e Conceitos de ADS
* **Engine:** [stlite](https://github.com/whitphx/stlite) (Streamlit + Pyodide).
* **Runtime:** WebAssembly para execução de código nativo no browser.
* **Persistência:** SQLite 3 integrado ao Virtual File System (VFS) do navegador.
* **UI/UX:** Design adaptativo (Mobile-First) com alto contraste para visibilidade em campo.



## 📂 Estrutura de Deploy
1.  `index.html`: Wrapper em JavaScript que gerencia o ciclo de vida do ambiente WASM e injeta as configurações de tema.
2.  `app_offline.py`: Lógica de negócio em Python, otimizada para evitar requisições de rede.
3.  `preparacalda2.db`: Banco de dados relacional contendo a inteligência de misturas químicas.

## 🚀 Como Instalar no Smartphone (PWA)
Para garantir o funcionamento 100% offline, siga este protocolo:

1.  **Sincronização:** Acesse a URL do projeto via Safari (iOS) ou Chrome (Android) com internet.
2.  **Download do Runtime:** Aguarde o carregamento inicial (o navegador baixará o core do Python e a biblioteca Pandas).
3.  **Instalação Local:**
    * **iOS:** Toque em `Compartilhar` > `Adicionar à Tela de Início`.
    * **Android:** Toque nos três pontos > `Instalar Aplicativo`.
4.  **Uso em Campo:** Uma vez instalado, o app pode ser aberto sem internet. O Service Worker recuperará todos os binários do cache local.



## 🛠️ Manutenção e Atualização
Sempre que o arquivo `app_offline.py` ou o banco de dados forem alterados no GitHub:
1.  O cache do navegador detectará a mudança na próxima vez que houver conexão.
2.  O sistema atualizará automaticamente os binários locais.

## 🎓 Créditos
Desenvolvido como projeto prático para o curso de **Análise e Desenvolvimento de Sistemas (ADS)** - IF Sertão Campus Petrolina.

👨‍🎓**Desenvolvedor Estudante**: André Lucas
---
*Foco: Praticidade, Segurança Química e Autonomia Tecnológica no Semiárido.*


