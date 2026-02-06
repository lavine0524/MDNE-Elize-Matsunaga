# =========================================================
# PROJETO: Modelagem de Dados Não Estruturados - Etapa 1
# TEMA: Análise do Caso Elize Matsunaga
#
# INTEGRANTES DO GRUPO:
# 1. Bianca Lavine
# 2. Letícia Braz
# 3. Kaio Vitor
#
# PROFESSORA: Adriana Carla Damasceno
# =========================================================

import re
import spacy
from spacy.language import Language


# 1. PRÉ-COMPILAÇÃO DE REGEX (OTIMIZAÇÃO DE PERFORMANCE)
# Compilamos os padrões aqui para não recriá-los a cada frase (muito mais rápido)
RE_URL = re.compile(r'https?://\S+|www\.\S+')
# Risadas: kkk, rsrs, hahaha, huahua (independente de maiúsculas)
RE_RISADAS = re.compile(r'(?i)\b(k+|r+|s+|(rs)+|(ha)+|(hua)+)\b')
# Pontuação repetida: "!!!!" vira "!"
RE_PONTUACAO = re.compile(r'([!?,.])\1+')
# Espaços múltiplos
RE_ESPACOS = re.compile(r'\s+')


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
        {"label": "ORG", "pattern": "justiça_br"},  # Perfil sem o @

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
    Limpa o texto preservando Emojis (sentimento) e palavras-chave de Hashtags/Menções.
    Usa regex compilado para alta performance.
    """
    # 1. Remove URLs (Links não têm sentimento)
    texto = RE_URL.sub('', texto_bruto)

    # 2. Limpeza de Menções (@) e Hashtags (#)
    # Removemos apenas os símbolos, mantendo o texto (Ex: #justiça -> justiça)
    # Isso enriquece a análise de sentimento posterior
    texto = texto.replace('@', '').replace('#', '')

    # 3. Remove risadas (ruído)
    texto = RE_RISADAS.sub('', texto)

    # 4. Normaliza pontuação (Ex: "Crime!!!!" -> "Crime!")
    texto = RE_PONTUACAO.sub(r'\1', texto)

    # 5. Remove espaços extras e quebras de linha
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



if __name__ == "__main__":
    print("\n:. INICIANDO ANÁLISE DE ENTIDADES - PROJETO ELIZE (FINAL) .:\n")

    # Lista de comentários simulados (Futuramente virá da API do Reddit)
    comentarios_reddit = [
        "A Elize Matsunaga agora é motorista de app? 😱 Vi no link https://reddit.com/r/crime kkkkkk #elizematsunaga",
        "Acho um absurdo ela ter saído de Tremembé tão cedo... @justiça_br fiquem de olho!",
        "O documentário da Netflix sobre a Elize é muito bom, mostra detalhes do crime em SP. rsrsrsrs",
        "Gente, não dá pra acreditar que ela está solta. #justiça #truecrimebr kkkk",
        "A empresa Uber deveria banir motoristas com antecedentes criminais graves!!!!!"
    ]

    # Processamento iterativo
    for comentario in comentarios_reddit:
        analisar_comentario(comentario)


