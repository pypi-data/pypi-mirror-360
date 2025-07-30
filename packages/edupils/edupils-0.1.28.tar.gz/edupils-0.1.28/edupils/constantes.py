import unicodedata

NOME_PAINEL_FUNDO = "painelFundo"
NOME_PAINEL_FRENTE = "painelFrente"
NOME_PAINEL_AUXILIAR = "painelAuxiliar"

LARGURA_PADRAO_CANVAS=500
ALTURA_PADRAO_CANVAS=300

COR_PRIMARIA = "#9D21FC"
COR_SECUNDARIA = "#34F9FF"
COR_ESCURA = "#555555"
COR_CLARA = "#F5F5F5"

TRADUCAO_PADRAO_DE_LINHA = {
    "tracejada":"dashed",
    "tracejado":"dashed",
    "pontilhada":"dotted",
    "pontilhado":"dotted",
    "solida":"solid",
    "solido":"solid",
}

TRADUCAO_CORES = {
    "preto":"black",
    "preta":"black",
    "prata":"silver",
    "cinza":"gray",
    "branco":"white",
    "branca":"white",
    "marrom":"maroon",
    "vermelho":"red",
    "vermelha":"red",
    "rosa":"pink",
    "roxo":"purple",
    "fucsia":"fuchsia",
    "verde":"green",
    "lima":"lime",
    "oliva":"olive",
    "amarelo":"yellow",
    "amarela":"yellow",
    "azul-marinho":"navy",
    "azul":"blue",
    "verde-agua":"teal",
}


def normalizar_palavra(palavra):
    palavra_normalizada = unicodedata.normalize('NFD', palavra)
    return ''.join(char for char in palavra_normalizada if char.isascii())

def traduzir(palavra, dicionario):
    palavra = normalizar_palavra(palavra)
    palavra = palavra.lower()
    
    if palavra in dicionario:
        return dicionario[palavra]
    return palavra