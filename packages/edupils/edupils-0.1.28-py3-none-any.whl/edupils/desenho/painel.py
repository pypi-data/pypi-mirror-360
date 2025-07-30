from js import document
from .. import constantes



# Function to create a canvas with specific attributes
def criar_camada(id, width, height):
    painel = document.createElement("canvas")
    painel.setAttribute("id", id)
    painel.width = width
    painel.height = height
    painel.style.position = "absolute"
    painel.style.left = 0
    painel.style.top = 0
    return painel

def apagar_painel(id_painel=constantes.NOME_PAINEL_FRENTE):
    painel = document.getElementById(id_painel)
    contexto = painel.getContext('2d')
    contexto.clearRect(0, 0, painel.width, painel.height)


def criar_painel(
        largura=constantes.LARGURA_PADRAO_CANVAS, 
        altura=constantes.ALTURA_PADRAO_CANVAS,
        nome_painel_fundo=constantes.NOME_PAINEL_FUNDO,
        nome_painel_frente=constantes.NOME_PAINEL_FRENTE,
        nome_painel_auxiliar=constantes.NOME_PAINEL_AUXILIAR,
    ):
    
    div = document.createElement("div")
    div.setAttribute("id", "gameCanvas")
    div.style.setProperty("position", "relative")
    div.style.setProperty("width", f"{largura}px")
    div.style.setProperty("height", f"{altura}px")

    for nome_painel in (
        [nome_painel_fundo] + 
        [nome_painel_auxiliar] + 
        [nome_painel_frente]
    ):
        painel = criar_camada(nome_painel, largura, altura)
        div.appendChild(painel)

    return div
    
painel = criar_painel()