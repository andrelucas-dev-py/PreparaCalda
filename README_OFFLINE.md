# 🚜 PreparaCalda Pro - Edição Offline (WASM)

Este repositório contém a versão **100% Offline** do sistema PreparaCalda Pro. Utilizando a tecnologia **stlite (Streamlit + WebAssembly)**, o software é capaz de executar o interpretador Python diretamente no navegador do dispositivo móvel, eliminando a necessidade de um servidor ativo após o primeiro carregamento.

## 📱 Objetivo do Projeto
Permitir que produtores rurais em áreas sem cobertura de internet (zonas de sombra) realizem o cálculo de dosagem e verifiquem a ordem química de mistura de defensivos agrícolas com segurança e precisão.

## 🏗️ Arquitetura Técnica (Edge Computing)

Diferente do modelo tradicional Client-Server, esta versão utiliza:
* **stlite:** Um port do Streamlit para WebAssembly (Pyodide).
* **PWA (Progressive Web App):** Permite a instalação na tela inicial e cache local de arquivos.
* **SQLite Local:** O banco de dados `preparacalda2.db` é baixado para o sistema de arquivos virtual do navegador.



## 📂 Estrutura de Arquivos

* `index.html`: O ponto de entrada que configura o ambiente stlite e monta o sistema de arquivos.
* `app_offline.py`: O código-fonte Python adaptado para execução local.
* `preparacalda2.db`: Base de dados SQLite contendo categorias, produtos e regras de prioridade.

## 🚀 Como Utilizar (Modo Offline)

1.  **Acesso Inicial:** Acesse o link do GitHub Pages (requer internet apenas na primeira vez).
2.  **Download do Runtime:** O navegador baixará cerca de 30MB (interpretador Python + bibliotecas). Aguarde o app carregar.
3.  **Instalação:** No navegador do celular (Safari ou Chrome), selecione "Adicionar à Tela de Início".
4.  **Uso em Campo:** Ative o Modo Avião e abra o ícone na tela inicial. O sistema funcionará instantaneamente via cache.

## 🔧 Configuração de Deploy (GitHub Pages)

Para replicar este ambiente:
1. Suba os arquivos `index.html`, `app_offline.py` e `preparacalda2.db` para o repositório.
2. No `index.html`, aponte as URLs `raw.githubusercontent.com` para os seus arquivos.
3. Ative o **GitHub Pages** em *Settings > Pages*.

## 👨‍💻 Conceitos de ADS Aplicados
* **Client-Side Rendering (CSR):** Todo o processamento ocorre na CPU do cliente.
* **Persistence:** Uso de SQLite em ambiente sandboxed.
* **Service Workers:** Garantia de disponibilidade offline via protocolo PWA.

---
Desenvolvido como projeto prático para o **IF Sertão - Campus Petrolina**.