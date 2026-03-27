# =========================================================
# PROJETO: Modelagem de Dados Não Estruturados - Etapa 3
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
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from transformers import pipeline

# --- 1. PRÉ-COMPILAÇÃO DE REGEX (LIMPEZA) ---
RE_URL = re.compile(r'https?://\S+|www\.\S+')
RE_RISADAS = re.compile(r'(?i)\b(k+|r+|s+|(rs)+|(ha)+|(hua)+|lol|lmao|lmfao)\b')
RE_PONTUACAO = re.compile(r'([!?,.])\1+')
RE_ESPACOS = re.compile(r'\s+')

# --- 2. CARREGAMENTO DOS MODELOS ---
print("Carregando modelos de NLP... (Aguarde)")
try:
    nlp = spacy.load("pt_core_news_lg")
except OSError:
    print("Aviso: Baixando modelo sm por segurança...")
    nlp = spacy.load("pt_core_news_sm")

# Inicializando a IA de Sentimentos
sentimento_analyser = pipeline("sentiment-analysis", 
                               model="nlptown/bert-base-multilingual-uncased-sentiment")

# Configurando o Entity Ruler
if not nlp.has_pipe("entity_ruler"):
    ruler = nlp.add_pipe("entity_ruler", before="ner")
    padroes = [
        {"label": "PER", "pattern": "Elize Matsunaga"},
        {"label": "PER", "pattern": "Elize"},
        {"label": "LOC", "pattern": "Tremembé"},
        {"label": "ORG", "pattern": "Netflix"},
        {"label": "PER", "pattern": "Marcos"},
        {"label": "MISC", "pattern": "True Crime"}
    ]
    ruler.add_patterns(padroes)

# --- 3. FUNÇÕES DE APOIO (DEFINIÇÕES) ---

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

def coletar_reddit(termo, limite=25):
    print(f"\n--- Buscando no Reddit: '{termo}' ---")
    url = f"https://www.reddit.com/r/brasil/search.json?q={termo}&limit={limite}"
    headers = {'User-Agent': 'python:projeto_faculdade_nlp:v1.0'}
    try:
        resposta = requests.get(url, headers=headers)
        dados = resposta.json()
        posts = []
        for post in dados['data']['children']:
            titulo = post['data']['title']
            corpo = post['data']['selftext']
            posts.append(f"{titulo}. {corpo}")
        return posts
    except Exception as e:
        print(f"❌ Erro na coleta: {e}")
        return []

def processar_completo(comentario_original):
    texto_limpo = limpar_texto(comentario_original)
    if not texto_limpo or len(texto_limpo) < 5:
        return None

    doc = nlp(texto_limpo)

    # Requisitos Etapa 3
    entidades = [ent.text for ent in doc.ents]
    lemmas = [token.lemma_.lower() for token in doc if not token.is_stop and not token.is_punct]
    chunks = [chunk.text for chunk in doc.noun_chunks]

    # Sentimento
    resultado_sent = sentimento_analyser(texto_limpo[:512])[0] 

    return {
        "texto_original": comentario_original,
        "texto_limpo": texto_limpo,
        "entidades": ", ".join(entidades),
        "lemmas": " ".join(lemmas),
        "noun_chunks": ", ".join(chunks),
        "score_sentimento": resultado_sent['label']
    }

def gerar_graficos(df):
    print("\n📊 Criando arquivos de imagem...")
    
    # Gráfico de Barras
    plt.figure(figsize=(10, 6))
    df['score_sentimento'].value_counts().sort_index().plot(kind='bar', color='skyblue')
    plt.title('Sentimentos - Caso Elize Matsunaga')
    plt.ylabel('Quantidade')
    plt.savefig('grafico_sentimentos.png')
    plt.close()

    # Nuvem de Palavras
    textao = " ".join(df['lemmas'].astype(str).tolist())
    wc = WordCloud(width=800, height=400, background_color='white').generate(textao)
    plt.figure(figsize=(10, 5))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis("off")
    plt.savefig('nuvem_palavras.png')
    plt.close()

# --- 4. EXECUÇÃO (O START DO CÓDIGO) ---

if __name__ == "__main__":
    print("\n🚀 Iniciando Etapa 3!")
    
    # 1. Busca os dados
    lista_posts = coletar_reddit("Elize Matsunaga", limite=25)
    
    dados_finais = []

    # 2. Processa os dados
    if lista_posts:
        print(f"Analisando {len(lista_posts)} textos...")
        for p in lista_posts:
            res = processar_completo(p)
            if res:
                dados_finais.append(res)
        
        # 3. Gera resultados
        if dados_finais:
            df_final = pd.DataFrame(dados_finais)
            df_final.to_csv("dados_completos_elize.csv", index=False, encoding='utf-8')
            gerar_graficos(df_final)
            print("\n✅ TUDO PRONTO!")
            print("Verifique os arquivos 'grafico_sentimentos.png' e 'nuvem_palavras.png' na sua pasta!")
        else:
            print("⚠️ Falha ao processar os textos.")
    else:
        print("❌ Nenhum dado coletado do Reddit.")




