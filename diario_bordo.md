# DIÁRIO DE BORDO: ETAPA 1 (DESAFIOS E SOLUÇÕES) 

**1. Insuficiência do Modelo *Small***

* **Problema:** O modelo inicial (`pt_core_news_sm`) apresentou baixa precisão em textos curtos de redes sociais.
* **Erro:** Classificou incorretamente o sujeito "Elize" como Organização (`ORG`) e verbos no início de frase (ex: "Acho") como Pessoas (`PER`).
* **Solução:** Migração para o modelo **`pt_core_news_lg` (Large)**, que possui maior volume de dados e contexto semântico.

**2. Interferência de Emojis e Sintaxe Informal**

* **Problema:** O uso informal de emojis funcionou como "falsa pontuação", gerando ambiguidades sintáticas.
* **Erro:** O verbo "Vi" (posicionado após o emoji 😱) foi classificado erroneamente como entidade `MISC` devido à capitalização.
* **Solução:** Implementação de um **`Entity Ruler` (Régua de Entidades)** no spaCy para:
* **Forçar classificação:** Garantir que "Elize" seja sempre `PER` e "Tremembé" seja `LOC`.
* **Filtragem (Stopwords):** Criar uma lista de exclusão para ignorar verbos comuns ("Vi", "Acho") erroneamente detectados.

**3. Perda de Dados em Menções e Hashtags**

* **Problema:** A limpeza inicial com Regex removia completamente menções (`@usuario`) e hashtags (`#tema`), descartando entidades valiosas (ex: `@justiça_br`) e palavras-chave de sentimento.
* **Solução:** Refatoração do Regex para remover apenas os símbolos especiais (`@` e `#`), preservando o texto útil. Adicionamos regras manuais para que perfis institucionais (como `justiça_br`) fossem reconhecidos corretamente como Organizações (`ORG`).

---

### Resumo do que entra no slide:

1. **Troca de Modelo** (`sm`  `lg`) por falta de contexto.
2. **Ambiguidades** ("Vi"  `MISC`) causadas por emojis/informalidade, resolvidas com filtros.
3. **Preservação de Dados** (Manter texto de `@` e `#`) para enriquecer a análise.


# DIÁRIO DE BORDO: DESAFIOS E SOLUÇÕES (ETAPA 2)

###  Problemas Técnicos Resolvidos
1. **Instabilidade na API Oficial (OAuth2):** O portal de desenvolvedores do Reddit apresentou falhas na geração de chaves.
   * **Solução:** Migração para ingestão via **Endpoint JSON Público**, garantindo a coleta sem travas de autenticação.
2. **Resíduos de Formatação Invisível:** Identificamos entidades HTML (`&amp;`) e caracteres Unicode (`\u200b`) que o Regex comum não limpava.
   * **Solução:** Integração da biblioteca `html.unescape` e filtros de string para normalização completa do texto.
3. **Ambiguidade no NER:** O modelo estatístico `lg` confundia nomes próprios isolados (ex: "Suzane") com organizações.
   * **Solução:** Implementação de um **EntityRuler** para forçar padrões fixos de reconhecimento de personagens e locais.

###  Melhorias de Engenharia de Dados
4. **Resiliência de Conexão:** Risco de bloqueio por "Too Many Requests".
   * **Solução:** Implementação de um **User-Agent** personalizado e tratamento de exceções com `raise_for_status()`.
5. **Estruturação para Análise:** Dados "soltos" no terminal dificultam estudos posteriores.
   * **Solução:** Integração com a biblioteca **Pandas** para exportação tabular em CSV, permitindo a persistência dos dados.
