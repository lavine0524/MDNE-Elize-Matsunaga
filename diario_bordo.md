{
 "cells": [
  {
   "cell_type": "markdown",
   "id": "aeccb99b",
   "metadata": {},
   "source": [
    "### **DIÁRIO DE BORDO: DESAFIOS E SOLUÇÕES**\n",
    "\n",
    "**1. Insuficiência do Modelo *Small***\n",
    "\n",
    "* **Problema:** O modelo inicial (`pt_core_news_sm`) apresentou baixa precisão em textos curtos de redes sociais.\n",
    "* **Erro:** Classificou incorretamente o sujeito \"Elize\" como Organização (`ORG`) e verbos no início de frase (ex: \"Acho\") como Pessoas (`PER`).\n",
    "* **Solução:** Migração para o modelo **`pt_core_news_lg` (Large)**, que possui maior volume de dados e contexto semântico.\n",
    "\n",
    "**2. Interferência de Emojis e Sintaxe Informal**\n",
    "\n",
    "* **Problema:** O uso informal de emojis funcionou como \"falsa pontuação\", gerando ambiguidades sintáticas.\n",
    "* **Erro:** O verbo \"Vi\" (posicionado após o emoji 😱) foi classificado erroneamente como entidade `MISC` devido à capitalização.\n",
    "* **Solução:** Implementação de um **`Entity Ruler` (Régua de Entidades)** no spaCy para:\n",
    "* **Forçar classificação:** Garantir que \"Elize\" seja sempre `PER` e \"Tremembé\" seja `LOC`.\n",
    "* **Filtragem (Stopwords):** Criar uma lista de exclusão para ignorar verbos comuns (\"Vi\", \"Acho\") erroneamente detectados.\n",
    "\n",
    "**3. Perda de Dados em Menções e Hashtags**\n",
    "\n",
    "* **Problema:** A limpeza inicial com Regex removia completamente menções (`@usuario`) e hashtags (`#tema`), descartando entidades valiosas (ex: `@justiça_br`) e palavras-chave de sentimento.\n",
    "* **Solução:** Refatoração do Regex para remover apenas os símbolos especiais (`@` e `#`), preservando o texto útil. Adicionamos regras manuais para que perfis institucionais (como `justiça_br`) fossem reconhecidos corretamente como Organizações (`ORG`).\n",
    "\n",
    "---\n",
    "\n",
    "### Resumo do que entra no slide:\n",
    "\n",
    "1. **Troca de Modelo** (`sm`  `lg`) por falta de contexto.\n",
    "2. **Ambiguidades** (\"Vi\"  `MISC`) causadas por emojis/informalidade, resolvidas com filtros.\n",
    "3. **Preservação de Dados** (Manter texto de `@` e `#`) para enriquecer a análise."
   ]
  }
 ],
 "metadata": {
  "language_info": {
   "name": "python"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}

# DIÁRIO DE BORDO: ETAPA 2 (COLETA E SANITIZAÇÃO)

---

## 4. Dificuldade de Acesso à API Oficial (OAuth2)
* **Problema:** O formulário de desenvolvedor do Reddit apresentou falhas silenciosas de validação (cache e erros de nome), impedindo a criação das chaves de acesso (Client ID/Secret).
* **Erro:** O botão "create app" não processava a requisição, travando o fluxo de autenticação via biblioteca PRAW.
* **Solução:** Implementação de uma abordagem de coleta alternativa via **Endpoint JSON Público** do Reddit. Utilizamos a biblioteca `requests` para capturar os dados brutos sem a necessidade de tokens, garantindo a agilidade da Etapa 2.

## 5. Ruídos de Formatação HTML e Unicode
* **Problema:** Os dados extraídos continham "lixo" de formatação invisível e entidades HTML codificadas que poluíam o corpus.
* **Erro:** Presença recorrente de sequências como `&amp;x200B;` (Zero Width Space) no texto limpo, que o Regex de pontuação comum não capturava.
* **Solução:** Integração da biblioteca nativa `html` para decodificação de entidades (`html.unescape`) e refatoração da função de limpeza para remover especificamente caracteres Unicode (`\u200b`).

## 6. Ambiguidade em Dados Bilíngues
* **Problema:** A busca global pelo tema trazia resultados em inglês, causando "alucinações" no modelo spaCy de Língua Portuguesa.
* **Erro:** Expressões genéricas (ex: "Has anyone") eram erroneamente classificadas como entidades MISC ou PER devido à capitalização.
* **Solução:** Refinamento da **Query de busca** com palavras-chave exclusivas do contexto brasileiro (*"documentário"*, *"solta"*, *"regime"*) para forçar um corpus em português e aumentar a precisão do NER.
