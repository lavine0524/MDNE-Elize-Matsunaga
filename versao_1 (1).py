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
from spacy.language import Language
import requests


# 1. PRÉ-COMPILAÇÃO DE REGEX (OTIMIZAÇÃO DE PERFORMANCE)
# Compilamos os padrões aqui para não recriá-los a cada frase (muito mais rápido)
RE_URL = re.compile(r'https?://\S+|www\.\S+')
# Risadas: kkk, rsrs, hahaha, huahua (independente de maiúsculas)
RE_RISADAS = re.compile(r'(?i)\b(k+|r+|s+|(rs)+|(ha)+|(hua)+|lol|lmao|lmfao)\b')
# Pontuação repetida: "!!!!" vira "!"
RE_PONTUACAO = re.compile(r'([!?,.])\1+')
# Espaços múltiplos
RE_ESPACOS = re.compile(r'\s+')
# Entidades HTML (como &amp;x200B;, &quot;, etc.)
RE_HTML = re.compile(r'&[a-z0-9#]+;')



# 2. CARREGAMENTO DO MODELO SPACY
print("Carregando modelo de linguagem... (Aguarde)")

try:
    # Prioridade: Modelo Large (Mais inteligente)
    nlp = spacy.load("pt_core_news_lg")
except OSError:
    print("⚠️  AVISO: Modelo 'pt_core_news_lg' não encontrado.")
    print("   Tentando carregar o modelo 'sm' (backup)...")
    try:
        nlp = spacy.load("pt_core_news_sm")
    except:
        print("❌ ERRO CRÍTICO: Nenhum modelo spaCy encontrado.")
        print("   Execute no terminal: python -m spacy download pt_core_news_lg")
        exit()


# 3. PERSONALIZAÇÃO (ENTITY RULER)
# Regras manuais para corrigir falhas de interpretação em textos curtos
if not nlp.has_pipe("entity_ruler"):
    ruler = nlp.add_pipe("entity_ruler", before="ner")

    padroes = [
        # --- GABARITO (O que deve ser identificado) ---
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

        # --- FILTRO (O que deve ser ignorado) ---
        # Palavras comuns que o modelo confunde com nomes próprios
        {"label": "IGNORAR", "pattern": "Vi"},
        {"label": "IGNORAR", "pattern": "Acho"},
        {"label": "IGNORAR", "pattern": "Gente"},
        {"label": "IGNORAR", "pattern": "Olha"},
    ]
    ruler.add_patterns(padroes)


# 4. FUNÇÕES DE LIMPEZA E ANÁLISE
def limpar_texto(texto_bruto):
    """
    Limpa o texto preservando Emojis e tratando ruídos de redes sociais.
    """
    # Usamos o módulo html
    texto = html.unescape(texto_bruto)
    
    # 2. Remove resíduos específicos de espaços invisíveis Unicode
    texto = texto.replace('\u200b', '').replace('#x200B', '')

    # 3. Remove URLs usando o regex compilado
    texto = RE_URL.sub('', texto)

    # 4. Limpeza de Menções (@) e Hashtags (#)
    texto = texto.replace('@', '').replace('#', '')

    # 5. Remove risadas (kkk, lol, etc.)
    texto = RE_RISADAS.sub('', texto)

    # 6. Normaliza pontuação (!!!! -> !)
    texto = RE_PONTUACAO.sub(r'\1', texto)

    # 7. Remove espaços extras e quebras de linha (Finalização)
    texto = RE_ESPACOS.sub(' ', texto).strip()

    return texto


def analisar_comentario(comentario_original):
    # Passo A: Limpeza Otimizada
    texto_limpo = limpar_texto(comentario_original)

    # Passo B: Processamento NLP
    doc = nlp(texto_limpo)

    # Exibição dos Resultados
    print(f"\n{'='*60}")
    print(f"📝 ORIGINAL: {comentario_original}")
    print(f"🧹 LIMPO:    {texto_limpo}")
    print(f"{'-'*60}")
    print("🔍 ENTIDADES DETECTADAS:")

    encontrou_algo = False
    for ent in doc.ents:
        # Pula entidades marcadas na lista negra
        if ent.label_ == "IGNORAR":
            continue

        encontrou_algo = True
        print(f"   • {ent.text:<20} | Tipo: {ent.label_}")

    if not encontrou_algo:
        print("   (Nenhuma entidade relevante encontrada)")
    print(f"{'='*60}")


def coletar_dados_sem_api(termo_busca, limite=5):
    print(f"\n--- Coletando dados reais (Via JSON Publico) sobre: {termo_busca} ---")
    
    # URL de busca do Reddit em formato JSON
    url = f"https://www.reddit.com/r/brasil/search.json?q={termo_busca}&limit={limite}"
    
    # O "User-Agent" é obrigatório para o Reddit não bloquear a requisição
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        resposta = requests.get(url, headers=headers)
        dados = resposta.json()
        
        textos_coletados = []
        # Navega na estrutura do JSON para pegar os títulos dos posts
        for post in dados['data']['children']:
            titulo = post['data']['title']
            # Também podemos pegar o texto do post (selftext)
            corpo = post['data']['selftext']
            textos_coletados.append(f"{titulo} {corpo}")
            
        return textos_coletados
    except Exception as e:
        print(f"Erro na coleta rápida: {e}")
        return []

if __name__ == "__main__":
    # 1. Coleta os dados reais
    comentarios_reais = coletar_dados_sem_api("Elize Matsunaga documentário solta", limite=5)
    
    # 2. Roda a sua análise da Etapa 1
    for texto in comentarios_reais:
        analisar_comentario(texto)



