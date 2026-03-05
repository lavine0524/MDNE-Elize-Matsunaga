# =========================================================
# PROJETO: Modelagem de Dados Não Estruturados - Etapa 2
# TEMA: Análise do Caso Elize Matsunaga
#
# INTEGRANTES DO GRUPO:
# 1. Bianca Lavine
# 2. Letícia Braz
# 3. Kaio Vitor
#
# PROFESSORA: Adriana Carla Damasceno
# =========================================================

import html
import re
import spacy
import requests
import pandas as pd

#PRÉ-COMPILAÇÃO DE REGEX (OTIMIZADO)
RE_URL = re.compile(r'https?://\S+|www\.\S+')
RE_RISADAS = re.compile(
    r'(?i)\b(k+|r+|s+|(rs)+|(ha)+|(hua)+|lol|lmao|lmfao)\b')
RE_PONTUACAO = re.compile(r'([!?,.])\1+')
RE_ESPACOS = re.compile(r'\s+')

#2. CARREGAMENTO DO MODELO SPACY
print("Carregando modelo de linguagem... (Aguarde)")
try:
    nlp = spacy.load("pt_core_news_lg")
except OSError:
    print("⚠️  AVISO: Modelo 'pt_core_news_lg' não encontrado. Tentando 'sm'...")
    try:
        nlp = spacy.load("pt_core_news_sm")
    except:
        print("❌ ERRO CRÍTICO: Nenhum modelo spaCy encontrado.")
        exit()

#3. PERSONALIZAÇÃO (ENTITY RULER)
if not nlp.has_pipe("entity_ruler"):
    ruler = nlp.add_pipe("entity_ruler", before="ner")
    padroes = [
        {"label": "PER", "pattern": "Elize Matsunaga"},
        {"label": "PER", "pattern": "Elize"},
        {"label": "LOC", "pattern": "Tremembé"},
        {"label": "ORG", "pattern": "Netflix"},
        {"label": "ORG", "pattern": "Uber"},
        {"label": "MISC", "pattern": "True Crime"},
        {"label": "ORG", "pattern": "justiça_br"},
        {"label": "PER", "pattern": "Suzane"},
        {"label": "PER", "pattern": "Marcos"},
        {"label": "PER", "pattern": "Suzane von Richthofen"},
        {"label": "MISC", "pattern": "Era Uma Vez Um Crime"},
        {"label": "IGNORAR", "pattern": [
            {"LOWER": {"IN": ["vi", "acho", "gente", "olha"]}}]}
    ]
    ruler.add_patterns(padroes)

#4. FUNÇÕES DE LIMPEZA E EXTRAÇÃO (NLP)
def limpar_texto(texto_bruto):
    if not texto_bruto:
        return ""
    texto = html.unescape(texto_bruto)
    texto = texto.replace('\u200b', '').replace('#x200B', '')
    texto = RE_URL.sub('', texto)
    texto = texto.replace('@', '').replace('#', '')
    texto = RE_RISADAS.sub('', texto)
    texto = RE_PONTUACAO.sub(r'\1', texto)
    texto = RE_ESPACOS.sub(' ', texto).strip()
    return texto


def processar_comentario(comentario_original):
    texto_limpo = limpar_texto(comentario_original)
    if not texto_limpo or len(texto_limpo) < 5:
        return None

    doc = nlp(texto_limpo)

    entidades = [ent.text for ent in doc.ents if ent.label_ != "IGNORAR"]
    adjetivos = [token.text.lower() for token in doc if token.pos_ == "ADJ"]
    substantivos = [token.text.lower()
                    for token in doc if token.pos_ == "NOUN"]

    return {
        "texto_original": comentario_original,
        "texto_limpo": texto_limpo,
        "entidades": ", ".join(entidades),
        "adjetivos": ", ".join(adjetivos),
        "substantivos": ", ".join(substantivos)
    }

#5. COLETA DE DADOS VIA JSON
def coletar_dados_sem_api(termo_busca, limite=15):
    print(f"\n--- Coletando dados no r/brasil sobre: '{termo_busca}' ---")
    url = f"https://www.reddit.com/r/brasil/search.json?q={termo_busca}&limit={limite}"

    headers = {
        'User-Agent': 'script:analise_textual_nlp:v1.0 (by /u/seu_usuario_aqui)'}

    try:
        resposta = requests.get(url, headers=headers)
        resposta.raise_for_status()
        dados = resposta.json()

        textos_coletados = []
        for post in dados['data']['children']:
            titulo = post['data']['title']
            corpo = post['data']['selftext']
            textos_coletados.append(f"{titulo}. {corpo}")

        print(f"✅ {len(textos_coletados)} posts encontrados.")
        return textos_coletados
    except Exception as e:
        print(f"❌ Erro na coleta: {e}")
        return []


#6. EXECUÇÃO PRINCIPAL
if __name__ == "__main__":
    termo = "Elize Matsunaga documentário solta"
    comentarios_reais = coletar_dados_sem_api(termo, limite=20)

    dados_finais = []

    print("\nProcessando textos com spaCy (limpeza, entidades, adjetivos e substantivos)...")

    # Usamos o enumerate para saber qual é o número do texto atual (índice 'i')
    for i, texto in enumerate(comentarios_reais):
        resultado = processar_comentario(texto)

        if resultado:
            dados_finais.append(resultado)

            
            if i < 3:
                print(f"\n{'='*60}")
                # Imprime apenas os primeiros 150 caracteres para não poluir demais a tela
                print(f"📝 ORIGINAL:  {resultado['texto_original'][:150]}...")
                print(f"🧹 LIMPO:     {resultado['texto_limpo'][:150]}...")
                print(f"🔍 ENTIDADES: {resultado['entidades'] or '(Nenhuma)'}")
                print(f"✨ ADJETIVOS: {resultado['adjetivos'] or '(Nenhum)'}")
                print(f"📚 SUBSTANT.: {resultado['substantivos'][:100]}...")
                print(f"{'='*60}")

    #7. EXPORTAÇÃO
    if dados_finais:
        df = pd.DataFrame(dados_finais)
        nome_arquivo = "dados_reddit_elize.csv"

        df.to_csv(nome_arquivo, index=False, encoding='utf-8')
        print(
            f"\n✅ SUCESSO! {len(dados_finais)} registros foram salvos em '{nome_arquivo}'.")
        print("📊 Seu dataset estruturado está pronto para ser analisado!")
    else:
        print("\n⚠️ Nenhum dado foi processado para ser salvo.")




